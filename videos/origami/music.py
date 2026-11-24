"""Origami World soundtrack, synthesized in pure Python + numpy.

Koto-like plucks (Karplus-Strong) on a pentatonic scale, paper rustles timed to each
piece unfolding, soft sea ambience and wing whooshes for the big crane.
Usage: python3 music.py out.wav
"""
import sys
import wave

import numpy as np

SR = 44100
DUR = 10.0
N = int(SR * DUR)
out = np.zeros(N)
rng = np.random.default_rng(4)


def add(sig, start, amp=1.0):
    i = int(start * SR)
    j = min(N, i + len(sig))
    if 0 <= i < N:
        out[i:j] += amp * sig[: j - i]


def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def pluck(freq, dur=1.8, bright=0.5):
    """Karplus-Strong plucked string — sounds close to a koto."""
    n = int(SR * dur)
    period = int(SR / freq)
    buf = rng.uniform(-1, 1, period)
    res = np.empty(n)
    for i in range(n):
        res[i] = buf[i % period]
        nxt = buf[(i + 1) % period]
        buf[i % period] = 0.996 * (bright * buf[i % period] + (1 - bright) * nxt)
    return res * np.minimum(1, np.arange(n) / 40)


def lowpass(x, a):
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc += a * (v - acc)
        y[i] = acc
    return y


def rustle(dur=0.35):
    """Crinkly paper fold: filtered noise with random crackles."""
    n = int(SR * dur)
    t = np.arange(n) / SR
    noise = rng.uniform(-1, 1, n)
    crackle = (rng.uniform(0, 1, n) > 0.985) * rng.uniform(-1, 1, n) * 3
    sig = noise - lowpass(noise, 0.08) + crackle * 0.5
    env = np.minimum(1, t / 0.02) * np.exp(-t * 9)
    return sig * env


def whoosh(dur=0.5):
    n = int(SR * dur)
    t = np.arange(n) / SR
    sig = lowpass(rng.uniform(-1, 1, n), 0.05)
    return sig * np.sin(np.pi * t / dur) ** 2


# --- melody: D minor pentatonic (D F G A C), gentle and airy ---
scale = [62, 65, 67, 69, 72, 74, 77, 79, 81]
pattern = [(0.3, 4), (0.8, 3), (1.3, 5), (1.8, 4), (2.6, 2), (3.1, 4), (3.6, 6), (4.4, 5),
           (5.0, 3), (5.6, 7), (6.1, 6), (6.6, 5), (7.2, 8), (7.5, 7), (7.8, 5), (8.6, 4), (9.0, 2)]
for s, k in pattern:
    add(pluck(midi(scale[k])), s, 0.28)
# low drone notes
for s, m in [(0.0, 50), (3.6, 53), (7.2, 50)]:
    add(pluck(midi(m), 3.5, 0.3), s, 0.22)

# paper rustles on every unfold (matches scene.html timings)
for s in [0.25, 0.6, 0.85, 1.0, 1.45, 1.75, 1.9, 2.2, 2.4, 2.6, 2.8, 7.2]:
    add(rustle(), s, 0.09)

# sea ambience once the waves are in
sea_n = int(SR * 7.4)
sea = lowpass(rng.uniform(-1, 1, sea_n), 0.02)
tt = np.arange(sea_n) / SR
sea *= (0.6 + 0.4 * np.sin(2 * np.pi * 0.35 * tt)) * np.minimum(1, tt / 1.0)
add(sea, 2.4, 0.35)

# wing whooshes as the pink crane arrives
for s in np.arange(5.6, 9.6, 2 * np.pi / 5.5):
    add(whoosh(0.45), s, 0.25)

t = np.arange(N) / SR
out *= np.minimum(1, t / 0.3) * np.minimum(1, (DUR - t) / 0.8)
out /= np.max(np.abs(out)) * 1.15
stereo = np.stack([out, out], axis=1)
with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((stereo * 32767).astype(np.int16).tobytes())
print("wrote", sys.argv[1])
