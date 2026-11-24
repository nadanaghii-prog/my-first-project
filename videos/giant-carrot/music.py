"""The Giant Carrot — music bed + effects, synthesized (storybook house sound).

Writes two files so HyperFrames mixes them on separate lanes:
  assets/music.wav  music-box melody in C major + soft pad (bed, ducks under the voice lines)
  assets/sfx.wav    effects placed on the animation's frames (see compositions/story.html)
Usage: python3 music.py   (run from the project folder)
"""
import wave

import numpy as np

SR, DUR = 44100, 12.5
N = int(SR * DUR)
rng = np.random.default_rng(11)


def track():
    return np.zeros(N)


def add(buf, sig, start, amp=1.0):
    i = int(start * SR)
    j = min(N, i + len(sig))
    if 0 <= i < N:
        buf[i:j] += amp * sig[: j - i]


def nf(name):
    names = {"C": -9, "D": -7, "E": -5, "F": -4, "G": -2, "A": 0, "B": 2}
    return 440.0 * 2 ** ((names[name[0]] + (int(name[-1]) - 4) * 12) / 12)


def music_box(f, dur=1.2):
    t = np.arange(int(SR * dur)) / SR
    return np.exp(-t * 4.5) * np.minimum(1, t * 400) * (
        np.sin(2 * np.pi * f * t) + 0.35 * np.sin(4 * np.pi * f * t) * np.exp(-t * 6))


def pad(fs, dur):
    t = np.arange(int(SR * dur)) / SR
    env = np.minimum(1, t / 0.6) * np.minimum(1, (dur - t) / 0.6)
    return env * sum(np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 2.002 * t) for f in fs) / len(fs)


def lowpass(x, a):
    y, acc = np.empty_like(x), 0.0
    for i, v in enumerate(x):
        acc += a * (v - acc)
        y[i] = acc
    return y


def sweep(f0, f1, dur, decay=0.0):
    t = np.arange(int(SR * dur)) / SR
    f = f0 + (f1 - f0) * t / dur
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * decay)


def thud(f0=120, dur=0.3):
    t = np.arange(int(SR * dur)) / SR
    return np.sin(2 * np.pi * np.cumsum(f0 * (1 + 1.6 * np.exp(-t * 30))) / SR) * np.exp(-t * 16)


def noise_burst(dur, a=0.15, decay=10):
    n = int(SR * dur)
    t = np.arange(n) / SR
    x = rng.uniform(-1, 1, n)
    return (x - lowpass(x, a)) * np.exp(-t * decay) * np.minimum(1, t * 200)


# ---------------- music bed ----------------
music = track()
mel = [("E5", .4), ("G5", .7), ("A5", 1.0), ("G5", 1.3), ("E5", 1.6), ("C5", 2.2),
       ("D5", 2.6), ("E5", 2.9), ("G5", 3.4),
       ("A4", 3.6), ("A4", 4.3), ("A4", 5.2), ("B4", 5.6), ("C5", 6.0), ("D5", 6.4),   # tension: repeated notes climbing
       ("C6", 6.82), ("G5", 7.1), ("E5", 7.35), ("C6", 7.8), ("B5", 8.1), ("A5", 8.4), ("G5", 8.7),
       ("E5", 9.0), ("G5", 9.25), ("C6", 9.5), ("E6", 9.75), ("C6", 10.5), ("G5", 11.0), ("C6", 11.5)]
for n, s in mel:
    add(music, music_box(nf(n)), s, 0.22)
for s, ns, d in [(0, ["C4", "E4", "G4"], 3.4), (3.4, ["A3", "C4", "E4"], 1.8), (5.2, ["F3", "A3", "C4"], 1.6),
                 (6.8, ["C4", "E4", "G4"], 2.2), (9.0, ["F3", "A3", "C4"], 1.5), (10.5, ["C4", "E4", "G4"], 2.0)]:
    add(music, pad([nf(x) for x in ns], d + 0.3), s, 0.06)
t = np.arange(N) / SR
duck = np.ones(N)                                   # dip the bed under each voice line
for s, d in [(0.35, 2.2), (3.5, 1.0), (5.2, 1.0), (6.72, 2.2)]:
    duck -= 0.35 * np.clip(np.minimum((t - s + 0.15) / 0.15, (s + d + 0.15 - t) / 0.2), 0, 1)
music *= duck

# ---------------- effects (each on its picture, ~1 frame late) ----------------
sfx = track()
for s in [3.48, 5.18]:                              # leaves rustle as they yank
    add(sfx, noise_burst(0.35, 0.2, 7), s, 0.25)
add(sfx, sweep(180, 420, 1.15, 0.2) * np.linspace(0, 1, int(SR * 1.15)) ** 2, 5.62, 0.12)  # strain creak rising
add(sfx, sweep(900, 140, 0.16, 18), 6.83, 0.9)       # POP
add(sfx, noise_burst(0.12, 0.5, 30), 6.83, 0.6)
w = lowpass(rng.uniform(-1, 1, int(SR * 0.5)), 0.08) * np.sin(np.linspace(0, np.pi, int(SR * 0.5))) ** 2
add(sfx, w, 6.85, 0.8)                               # whoosh up
for k in range(9):                                   # dirt patter
    add(sfx, noise_burst(0.05, 0.3, 60), 7.1 + k * 0.06 + rng.uniform(0, .03), 0.25)
add(sfx, thud(150, 0.25), 7.08, 0.5)                 # kids bump down
add(sfx, thud(95, 0.4), 7.78, 1.0)                   # carrot lands
add(sfx, thud(260, 0.18), 7.78, 0.7)                 # mid "thump" so phone speakers hear the landing
add(sfx, noise_burst(0.08, 0.35, 40), 7.78, 0.5)
for k, f in enumerate([1568, 2093, 2637]):           # sparkle on the landing
    add(sfx, music_box(f, 0.6), 7.8 + k * 0.06, 0.08)
for s in [8.61, 8.76, 9.36, 9.61, 10.36, 10.66]:     # boing on each hop take-off
    add(sfx, sweep(260, 640, 0.3, 9), s, 0.18)


def write(path, buf, fade_out=0.8):
    buf = buf * np.minimum(1, t / 0.05) * np.minimum(1, (DUR - t) / fade_out)
    peak = np.max(np.abs(buf))
    buf = buf / peak * 0.89 if peak > 0 else buf      # ~ -1 dBFS peak
    st = np.stack([buf, buf], axis=1)
    with wave.open(path, "wb") as f:
        f.setnchannels(2)
        f.setsampwidth(2)
        f.setframerate(SR)
        f.writeframes((st * 32767).astype(np.int16).tobytes())
    print("wrote", path)


write("assets/music.wav", music)
write("assets/sfx.wav", sfx)
