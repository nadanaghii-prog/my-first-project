/* motion.js — Disney's 12 principles of animation as small, deterministic helpers.
 *
 * Every function is a pure function of time t (seconds), so frames render identically
 * every time (works with videos/render.js and with HyperFrames).
 *
 * Browser:  <script src="motion.js"></script>  → window.Motion
 * Node:     const Motion = require("./motion.js")
 */
(function (root) {
  const TAU = Math.PI * 2;
  const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
  const lerp = (a, b, u) => a + (b - a) * u;
  const mix = (a, b, u) => Array.isArray(a) ? a.map((v, i) => lerp(v, b[i], u)) : lerp(a, b, u);
  const progress = (t, t0, dur) => clamp((t - t0) / dur);

  // ---------- 6. Slow in & slow out — easing curves ----------
  const ease = {
    linear: x => x,
    inQuad: x => x * x,
    outQuad: x => 1 - (1 - x) * (1 - x),
    inOutQuad: x => x < .5 ? 2 * x * x : 1 - Math.pow(-2 * x + 2, 2) / 2,
    inCubic: x => x * x * x,
    outCubic: x => 1 - Math.pow(1 - x, 3),
    inOutCubic: x => x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2,
    inOutSine: x => -(Math.cos(Math.PI * x) - 1) / 2,
    inBack: (x, s = 1.70158) => (s + 1) * x * x * x - s * x * x,           // anticipation built in
    outBack: (x, s = 1.70158) => 1 + (s + 1) * Math.pow(x - 1, 3) + s * Math.pow(x - 1, 2), // overshoot
    outElastic: x => x === 0 || x === 1 ? x : Math.pow(2, -10 * x) * Math.sin((x * 10 - .75) * TAU / 3) + 1,
    outBounce: x => {
      const n = 7.5625, d = 2.75;
      if (x < 1 / d) return n * x * x;
      if (x < 2 / d) return n * (x -= 1.5 / d) * x + .75;
      if (x < 2.5 / d) return n * (x -= 2.25 / d) * x + .9375;
      return n * (x -= 2.625 / d) * x + .984375;
    },
  };
  const getEase = e => typeof e === "function" ? e : (ease[e] || ease.inOutCubic);

  // ---------- 4. Pose to pose — keyframes with per-segment easing ----------
  // keys: [[time, value, easeIntoThisKey?], ...] sorted by time. value: number or array.
  function tween(t, keys, defaultEase = "inOutCubic") {
    if (t <= keys[0][0]) return keys[0][1];
    for (let i = 1; i < keys.length; i++) {
      const [t1, v1, e] = keys[i], [t0, v0] = keys[i - 1];
      if (t <= t1) return mix(v0, v1, getEase(e || defaultEase)((t - t0) / (t1 - t0)));
    }
    return keys[keys.length - 1][1];
  }

  // ---------- physics-feel helpers ----------
  // Spring step response 0 → 1 (overshoot + settle). freq in Hz, damping 0..1 (1 = no overshoot).
  function spring(t, t0 = 0, freq = 2.2, damping = 0.35) {
    const x = t - t0; if (x <= 0) return 0;
    const w = TAU * freq, z = damping, wd = w * Math.sqrt(1 - z * z);
    return 1 - Math.exp(-z * w * x) * (Math.cos(wd * x) + (z * w / wd) * Math.sin(wd * x));
  }

  // ---------- 5. Follow through — damped wobble after a motion stops ----------
  // Returns an offset (e.g. degrees for ears/tail/hair) that dies out after tStop.
  function followThrough(t, tStop, amp = 12, freq = 3, decay = 4) {
    const x = t - tStop; if (x < 0) return 0;
    return amp * Math.exp(-decay * x) * Math.sin(TAU * freq * x);
  }

  // ---------- 5. Overlapping action — parts lag behind the lead ----------
  // Evaluate any motion function a little later for a dragging part (ears, tail, cape).
  const lag = (fn, t, delay) => fn(t - delay);
  // Offset index i in a chain (tail segments, letters of a word, a row of flowers).
  const stagger = (i, step = 0.06) => i * step;

  // ---------- 1. Squash & stretch — volume preserving ----------
  // amount > 0 stretches along the motion axis, < 0 squashes. Returns [sx, sy] for a vertical axis.
  function squash(amount) {
    const sy = 1 + amount, sx = 1 / Math.sqrt(Math.max(0.2, sy)); // keep area ~constant
    return [sx, sy];
  }
  // Stretch from speed: faster → longer. velocity in px/s, k ~ 0.0006.
  const stretchFromVelocity = (v, k = 0.0006, max = 0.35) => squash(Math.min(max, Math.abs(v) * k));
  // Impact squash at tHit that springs back.
  function impact(t, tHit, amount = 0.3, dur = 0.18) {
    const x = (t - tHit) / dur; if (x < 0 || x > 1.6) return [1, 1];
    const a = -amount * Math.exp(-3 * x) * Math.cos(x * Math.PI * 1.3);
    return squash(a);
  }

  // ---------- 2. Anticipation ----------
  // Small move the opposite way before the main action. Returns the value to apply.
  // windup: how far back (same units as distance), windDur and actDur in seconds.
  function anticipate(t, t0, distance, { windup = 0.15 * distance, windDur = 0.25, actDur = 0.4, actEase = "outCubic" } = {}) {
    if (t < t0) return 0;
    if (t < t0 + windDur) return -windup * ease.inOutSine(progress(t, t0, windDur));
    const u = getEase(actEase)(progress(t, t0 + windDur, actDur));
    return lerp(-windup, distance, u);
  }

  // ---------- 7. Arcs ----------
  // Quadratic arc between p0 and p1, bulging `height` px (negative = up in SVG coords).
  function arc(p0, p1, height, u) {
    const c = [(p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2 + height];
    const a = 1 - u;
    return [a * a * p0[0] + 2 * a * u * c[0] + u * u * p1[0], a * a * p0[1] + 2 * a * u * c[1] + u * u * p1[1]];
  }
  // Rotation that "swings" on an arc (pendulum) — for arms, heads, flowers.
  const swing = (t, amp = 10, freq = 0.6, phase = 0) => amp * Math.sin(TAU * freq * t + phase);

  // ---------- Combined: a full character jump ----------
  // anticipation crouch → stretch on take-off → arc in the air → squash on landing → settle.
  // Returns { y, sx, sy, rot } to apply around the feet. height in px (positive = up).
  function jump(t, t0, { height = 120, crouch = 0.12, airTime = 0.5, crouchTime = 0.16, land = 0.25 } = {}) {
    const x = t - t0;
    if (x < 0) return { y: 0, sx: 1, sy: 1, rot: 0 };
    if (x < crouchTime) {                       // anticipation
      const [sx, sy] = squash(-crouch * ease.inOutSine(x / crouchTime));
      return { y: 0, sx, sy, rot: 0 };
    }
    const a = x - crouchTime;
    if (a < airTime) {                          // in the air: parabola (slow at the top)
      const u = a / airTime, y = height * 4 * u * (1 - u);
      const v = height * 4 * (1 - 2 * u) / airTime;          // vertical speed
      const [sx, sy] = stretchFromVelocity(v, 0.0009, 0.25);
      return { y, sx, sy, rot: (u - .5) * -6 };
    }
    const [sx, sy] = impact(x, crouchTime + airTime, land);   // landing squash + settle
    return { y: 0, sx, sy, rot: 0 };
  }

  // ---------- 8. Secondary action & 'alive' idles ----------
  const breathe = (t, rate = 0.35, amount = 0.012, phase = 0) => 1 + amount * Math.sin(TAU * rate * t + phase);
  // Blink: returns eye openness 0..1. Natural blink ~ 0.12–0.15s every 2.5–4s.
  function blink(t, period = 3.2, offset = 0, dur = 0.14) {
    const p = (((t + offset) % period) + period) % period;
    return p < dur ? 1 - Math.sin((p / dur) * Math.PI) : 1;
  }
  // Smooth 1D value noise (deterministic) for organic drift.
  function noise(x, seed = 0) {
    const h = n => { const s = Math.sin(n * 127.1 + seed * 311.7) * 43758.5453; return s - Math.floor(s); };
    const i = Math.floor(x), f = x - i, u = f * f * (3 - 2 * f);
    return lerp(h(i), h(i + 1), u) * 2 - 1;
  }
  // "Moving hold": tiny drift so a held pose never looks frozen.
  const movingHold = (t, amount = 2, seed = 0) => [noise(t * 0.8, seed) * amount, noise(t * 0.8, seed + 7) * amount];

  // ---------- 9. Timing ----------
  const FPS = 30;
  const frames = (n, fps = FPS) => n / fps;      // frames → seconds
  // Typical durations at 30fps (seconds) — see references/principles.md
  const TIMING = { blink: 0.13, quick: 0.2, snappy: 0.33, normal: 0.5, slow: 0.8, weighty: 1.2, read: 2.0 };

  // ---------- 10. Exaggeration ----------
  // Push any value past its rest by `factor` (1 = realistic, 1.3–1.6 = cartoon).
  const exaggerate = (value, rest = 0, factor = 1.4) => rest + (value - rest) * factor;

  const Motion = {
    clamp, lerp, mix, progress, ease, tween, spring, followThrough, lag, stagger,
    squash, stretchFromVelocity, impact, anticipate, arc, swing, jump,
    breathe, blink, noise, movingHold, frames, TIMING, exaggerate,
  };
  if (typeof module !== "undefined" && module.exports) module.exports = Motion;
  else root.Motion = Motion;
})(typeof window !== "undefined" ? window : globalThis);
