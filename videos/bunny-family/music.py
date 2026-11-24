"""Synthesize the soundtrack in pure Python + numpy (no samples, no AI music).

Music-box melody + soft pad + bird chirps + sound effects timed to the animation.
Usage: python3 music.py out.wav
"""
import sys
import wave

import numpy as np

SR = 44100
DUR = 10.0
N = int(SR * DUR)
out = np.zeros(N)


def note_freq(name):
    names = {"C": -9, "D": -7, "E": -5, "F": -4, "G": -2, "A": 0, "B": 2}
    semis = names[name[0]] + (int(name[-1]) - 4) * 12
    return 440.0 * 2 ** (semis / 12)


def add(sig, start):
    i = int(start * SR)
    j = min(N, i + len(sig))
    if i < N:
        out[i:j] += sig[: j - i]


def music_box(freq, dur=1.2, amp=0.22):
    t = np.arange(int(SR * dur)) / SR
    env = np.exp(-t * 4.5) * np.minimum(1, t * 400)
    tone = (np.sin(2 * np.pi * freq * t)
            + 0.35 * np.sin(2 * np.pi * freq * 2 * t) * np.exp(-t * 6)
            + 0.12 * np.sin(2 * np.pi * freq * 3.01 * t) * np.exp(-t * 9))
    return amp * env * tone


def pad(freqs, dur, amp=0.05):
    t = np.arange(int(SR * dur)) / SR
    env = np.minimum(1, t / 0.6) * np.minimum(1, (dur - t) / 0.6)
    sig = sum(np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 2.002 * t) for f in freqs)
    return amp * env * sig / len(freqs)


def chirp(start, f0=2600, f1=4200, dur=0.09, amp=0.05):
    t = np.arange(int(SR * dur)) / SR
    f = f0 + (f1 - f0) * (t / dur)
    sig = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / dur)
    add(amp * sig, start)


def boing(start, amp=0.12):
    t = np.arange(int(SR * 0.35)) / SR
    f = 260 + 380 * t / 0.35 + 30 * np.sin(2 * np.pi * 18 * t)
    sig = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)
    add(amp * sig, start)


def pop(start, amp=0.35):
    t = np.arange(int(SR * 0.18)) / SR
    f = 900 * np.exp(-t * 22) + 120
    sig = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 26)
    add(amp * sig, start)


def sparkle(start):
    for k, n in enumerate(["E6", "G6", "C7", "E7", "G7"]):
        add(music_box(note_freq(n), 0.8, 0.09), start + k * 0.06)


# --- melody (C major, ~120 bpm, eighth = 0.25s) ---
melody = [
    ("E5", 0.5), ("G5", 0.75), ("A5", 1.0), ("G5", 1.25), ("E5", 1.5), ("C5", 2.0),
    ("D5", 2.25), ("E5", 2.5), ("G5", 3.0), ("E5", 3.5),
    ("A5", 4.0), ("G5", 4.25), ("E5", 4.5), ("D5", 4.75), ("C5", 5.0),
    ("E5", 6.0), ("G5", 6.25), ("C6", 6.5), ("B5", 6.75), ("A5", 7.0), ("G5", 7.5),
    ("E5", 8.0), ("D5", 8.25), ("C5", 8.5), ("G4", 8.75), ("C5", 9.0),
]
for n, s in melody:
    add(music_box(note_freq(n)), s)

# gentle chord pad underneath
chords = [(0.0, ["C4", "E4", "G4"]), (2.0, ["A3", "C4", "E4"]), (4.0, ["F3", "A3", "C4"]),
          (6.0, ["G3", "B3", "D4"]), (8.0, ["C4", "E4", "G4"])]
for s, ns in chords:
    add(pad([note_freq(n) for n in ns], 2.4), s)

# birds in the background
for s in [0.3, 0.42, 1.9, 2.02, 4.6, 6.9, 7.02, 9.2]:
    chirp(s)

# effects synced to the animation
for s in [3.2, 3.5, 5.6, 5.75, 7.9, 8.2]:
    boing(s)
pop(5.2)
sparkle(5.25)
sparkle(7.0)

# master: fade in/out, normalize
t = np.arange(N) / SR
out *= np.minimum(1, t / 0.4) * np.minimum(1, (DUR - t) / 0.8)
out /= np.max(np.abs(out)) * 1.15
stereo = np.stack([out, out], axis=1)

with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((stereo * 32767).astype(np.int16).tobytes())
print("wrote", sys.argv[1])
