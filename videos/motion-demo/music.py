"""Motion demo soundtrack (pure numpy). Effects land on the exact animation frames.

Timings mirror scene.html: ball impacts, the bunny's two hops, label and title pops.
Usage: python3 music.py out.wav
"""
import sys
import wave

import numpy as np

SR, DUR = 44100, 10.0
N = int(SR * DUR)
out = np.zeros(N)
rng = np.random.default_rng(2)


def add(sig, start, amp=1.0):
    i = int(start * SR)
    j = min(N, i + len(sig))
    if 0 <= i < N:
        out[i:j] += amp * sig[: j - i]


def tone(f, dur, decay=5.0):
    t = np.arange(int(SR * dur)) / SR
    return np.sin(2 * np.pi * f * t) * np.exp(-t * decay) * np.minimum(1, t * 300)


def thud(f0=150):
    t = np.arange(int(SR * 0.25)) / SR
    f = f0 * (1 + 1.5 * np.exp(-t * 30))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 18)


def whoosh(dur, up=True):
    n = int(SR * dur)
    t = np.arange(n) / SR
    noise = rng.uniform(-1, 1, n)
    y, acc = np.empty(n), 0.0
    for i in range(n):                       # sweeping low-pass
        a = 0.02 + 0.18 * (t[i] / dur if up else 1 - t[i] / dur)
        acc += a * (noise[i] - acc)
        y[i] = acc
    return y * np.sin(np.pi * t / dur) ** 2


def pop():
    t = np.arange(int(SR * 0.12)) / SR
    f = 500 + 900 * np.exp(-t * 40)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 35)


# ball: impacts get quieter and higher as the bounces shrink (timing)
impacts = [0.75]
for d in [0.8, 0.6, 0.45, 0.32, 0.22]:
    impacts.append(impacts[-1] + d)
for k, ti in enumerate(impacts):
    add(thud(140 + 25 * k), ti, 0.9 * 0.72 ** k)

# bunny hops: crouch → whoosh up → landing thud (second one bigger: exaggeration)
for t0, crouch, air, amp in [(3.9, 0.16, 0.5, 0.5), (5.9, 0.26, 0.75, 0.8)]:
    add(whoosh(air * 0.6), t0 + crouch, amp * 0.6)
    add(thud(110), t0 + crouch + air, amp)
    add(tone(880, 0.4), t0 + crouch + 0.02, 0.12 * amp)   # little "boing" lift
    add(tone(1320, 0.3), t0 + crouch + 0.06, 0.08 * amp)

# label pops and title word pops
for s in [0.3, 2.1, 3.75, 4.75, 5.8]:
    add(pop(), s, 0.25)
for i, s in enumerate([7.5, 7.64, 7.78, 7.92]):
    add(tone([523, 659, 784, 1047][i], 0.9, 3.5), s, 0.22)
    add(pop(), s, 0.2)

# soft background: plucked C-major arpeggio
notes = [262, 330, 392, 523, 392, 330]
for k, s in enumerate(np.arange(0.2, 9.6, 0.4)):
    add(tone(notes[k % len(notes)], 0.5, 6), s, 0.07)

t = np.arange(N) / SR
out *= np.minimum(1, t / 0.2) * np.minimum(1, (DUR - t) / 0.7)
out /= np.max(np.abs(out)) * 1.15
stereo = np.stack([out, out], axis=1)
with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((stereo * 32767).astype(np.int16).tobytes())
print("wrote", sys.argv[1])
