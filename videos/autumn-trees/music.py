"""Autumn Trees — calm music + drawing sounds, synthesized with numpy (no samples).

Reads timeline.json (run `node export-timeline.js` first) so every crayon scratch, marker squeak
and leaf tap lands on its stroke. Usage: python3 music.py music.wav
"""
import json
import sys
import wave
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
TL = json.loads((HERE / "timeline.json").read_text())
SR = 44100
DUR = float(TL["duration"])
N = int(SR * DUR)
t = np.arange(N) / SR
rng = np.random.default_rng(5)


def bandnoise(lo, hi, n=N):
    """White noise band-passed in the frequency domain (fast, no scipy)."""
    spec = np.fft.rfft(rng.standard_normal(n))
    f = np.fft.rfftfreq(n, 1 / SR)
    spec[(f < lo) | (f > hi)] = 0
    x = np.fft.irfft(spec, n)
    return x / (np.max(np.abs(x)) + 1e-9)


def add(buf, sig, start, amp=1.0):
    i = int(start * SR)
    j = min(len(buf), i + len(sig))
    if 0 <= i < len(buf):
        buf[i:j] += amp * sig[: j - i]


def note(freq, dur, amp=1.0, decay=2.2):
    """Soft felt-piano-like tone."""
    tt = np.arange(int(SR * dur)) / SR
    env = np.minimum(1, tt / 0.012) * np.exp(-tt * decay)
    tone = np.sin(2 * np.pi * freq * tt) + 0.28 * np.sin(4 * np.pi * freq * tt) * np.exp(-tt * 3) \
        + 0.08 * np.sin(6 * np.pi * freq * tt) * np.exp(-tt * 5)
    return amp * env * tone


def midi(m):
    return 440 * 2 ** ((m - 69) / 12)


# ---------------- calm music: slow arpeggios, 66 bpm, I–vi–IV–V in C, a gentle melody on top --------
music = np.zeros(N)
beat = 60 / 66
chords = [[48, 55, 60, 64], [45, 52, 57, 60], [41, 48, 53, 57], [43, 50, 55, 59]]
melody = [76, None, 74, 72, None, 69, 72, None, 74, None, 72, 71, 72, None, None, None]
b = 0
while b * beat < DUR - 2:
    ch = chords[(b // 8) % 4]
    s = 0.4 + b * beat
    add(music, note(midi(ch[0]), 3.0, 0.20, 1.2), s) if b % 8 == 0 else None
    add(music, note(midi(ch[1 + (b % 3)]), 1.8, 0.10, 2.0), s)
    m = melody[b % len(melody)]
    if m and (b // 16) % 2 == 1:                       # melody every other phrase: rest, then sing
        add(music, note(midi(m), 1.6, 0.075, 1.8), s)
    b += 1
music *= np.minimum(1, t / 2.0) * np.minimum(1, (DUR - t) / 3.0)

# ---------------- drawing sounds ----------------
fx = np.zeros(N)
scratch = bandnoise(1800, 6500) * 0.6 + bandnoise(300, 1200) * 0.4      # waxy crayon on paper
squeak = bandnoise(2600, 5200)                                            # felt-tip marker
env_c, env_m = np.zeros(N), np.zeros(N)
for s in TL["strokes"]:
    i0, i1 = int(s["t0"] * SR), int(s["t1"] * SR)
    if i1 <= i0:
        continue
    seg = np.arange(i1 - i0) / SR
    fade = np.minimum(1, np.minimum(seg / 0.05, (seg[-1] - seg) / 0.08 + 1e-9))
    if s["kind"] == "crayon":
        e = 0.55 * fade
        # each row: louder in the middle of the stroke, a dip where the crayon turns around
        turns = np.array(s["turns"] + [s["t1"]])
        tabs = s["t0"] + seg
        idx = np.searchsorted(turns, tabs)
        prev = np.where(idx > 0, turns[np.maximum(idx - 1, 0)], s["t0"])
        nxt = turns[np.minimum(idx, len(turns) - 1)]
        u = (tabs - prev) / np.maximum(nxt - prev, 1e-3)
        e = e * (0.45 + 0.55 * np.sin(np.pi * np.clip(u, 0, 1)))
        env_c[i0:i1] = np.maximum(env_c[i0:i1], e)
    elif s["kind"] == "marker":
        e = 0.5 * fade * (0.7 + 0.3 * np.sin(np.pi * np.clip(seg / seg[-1], 0, 1)))
        env_m[i0:i1] = np.maximum(env_m[i0:i1], e)
    else:                                                                  # leaf dot: soft tap
        tt = np.arange(int(SR * 0.08)) / SR
        add(fx, bandnoise(800, 3000, len(tt)) * np.exp(-tt * 60), s["t0"] + 0.06, 0.35)
fx += scratch * env_c * 0.55 + squeak * env_m * 0.32

# hand movement: a soft swish when the hand comes in / leaves with a new tool
for h in TL["hand"]:
    dur = h["t1"] - h["t0"]
    tt = np.arange(int(SR * dur)) / SR
    add(fx, bandnoise(200, 1500, len(tt)) * np.sin(np.pi * tt / dur) ** 2, h["t0"], 0.10)
# paper sliding onto the table at the start
tt = np.arange(int(SR * 1.2)) / SR
add(fx, bandnoise(400, 4000, len(tt)) * np.sin(np.pi * tt / 1.2) ** 2 * np.exp(-tt * 1.5), 0.2, 0.25)
# finished: a little bell arpeggio
for k, m in enumerate([72, 76, 79, 84]):
    add(fx, note(midi(m), 2.0, 0.10, 2.5), TL["drawEnd"] + 0.45 + k * 0.12)

mix = music + fx
mix /= np.max(np.abs(mix)) / 0.89                       # ~ -1 dBFS peak
st = np.stack([mix, mix], axis=1)
with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((st * 32767).astype(np.int16).tobytes())
print("wrote", sys.argv[1], f"{DUR:.0f}s")
