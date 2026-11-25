/* drawing.js — the drawing lesson as data: every stroke the hand makes, in order, with its time.
 *
 * Shared by scene.html (picture) and export-timeline.js → timeline.json → music.py (drawing sounds),
 * so the crayon scratches and marker squeaks land exactly on the strokes.
 * Our own composition of a classic kids' art lesson (autumn trees on a round paper) — not a trace.
 */
(function (root) {
  // ---------- seeded randomness ----------
  function mulberry32(a) {
    return function () {
      a |= 0; a = (a + 0x6D2B79F5) | 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  // ---------- paper ----------
  const PAPER = { cx: 540, cy: 1030, r: 468 };
  const OFF = [1320, 2150];               // where the hand rests off-screen (bottom right)

  // ---------- tools ----------
  const TOOLS = {
    orange: { kind: "crayon", color: "#f47a20", wrap: "#e05f0c", speed: 640, width: 34 },
    yellow: { kind: "crayon", color: "#f6d31f", wrap: "#e2b90b", speed: 640, width: 34 },
    green: { kind: "crayon", color: "#8bd63a", wrap: "#5fae1d", speed: 640, width: 34 },
    pink: { kind: "crayon", color: "#f49cc8", wrap: "#e573ab", speed: 640, width: 34 },
    groundY: { kind: "crayon", color: "#f8dc3a", wrap: "#e2b90b", speed: 1500, width: 42 },
    groundO: { kind: "crayon", color: "#f5862a", wrap: "#e05f0c", speed: 1500, width: 42 },
    black: { kind: "marker", color: "#1d1919", speed: 520, width: 9 },
    red: { kind: "marker", color: "#de4a2c", speed: 300, width: 9 },
  };

  // ---------- geometry helpers ----------
  const dist = (a, b) => Math.hypot(b[0] - a[0], b[1] - a[1]);
  function polyLen(pts) { let L = 0; for (let i = 1; i < pts.length; i++) L += dist(pts[i - 1], pts[i]); return L; }
  function cumul(pts) { const c = [0]; for (let i = 1; i < pts.length; i++) c.push(c[i - 1] + dist(pts[i - 1], pts[i])); return c; }
  function pointAt(stroke, u) {             // point at arc-length fraction u
    const target = u * stroke.len, c = stroke.cum, p = stroke.pts;
    let lo = 0, hi = c.length - 1;
    while (hi - lo > 1) { const m = (lo + hi) >> 1; if (c[m] < target) lo = m; else hi = m; }
    const seg = c[hi] - c[lo] || 1, k = (target - c[lo]) / seg;
    return [p[lo][0] + (p[hi][0] - p[lo][0]) * k, p[lo][1] + (p[hi][1] - p[lo][1]) * k, p[hi][0] - p[lo][0], p[hi][1] - p[lo][1]];
  }
  function curve(p0, c, p1, n = 14) {       // quadratic curve sampled as points
    const out = [];
    for (let i = 0; i <= n; i++) { const u = i / n, a = 1 - u; out.push([a * a * p0[0] + 2 * a * u * c[0] + u * u * p1[0], a * a * p0[1] + 2 * a * u * c[1] + u * u * p1[1]]); }
    return out;
  }
  function wobble(pts, amt, rnd) { return pts.map(([x, y], i) => (i === 0 || i === pts.length - 1) ? [x, y] : [x + (rnd() - .5) * amt, y + (rnd() - .5) * amt]); }

  // crayon colouring: back-and-forth rows filling a cloud-like (superellipse) blob
  function scribbleBlob(cx, cy, rx, ry, seed, step = 21) {
    const rnd = mulberry32(seed), pts = [];
    let dir = 1;
    for (let y = cy - ry; y <= cy + ry; y += step) {
      const v = Math.abs((y - cy) / ry), w = rx * Math.pow(Math.max(0, 1 - Math.pow(v, 2.6)), 1 / 2.6);
      if (w < 14) continue;
      const bump = 1 + 0.1 * Math.sin(y * 0.045 + seed) + (rnd() - .5) * 0.12;   // ragged, leafy edge
      const xl = cx - w * bump, xr = cx + w * bump * (1 + (rnd() - .5) * 0.08);
      const slant = -10;
      if (dir > 0) { pts.push([xl, y - slant / 2]); pts.push([xr, y + slant / 2]); }
      else { pts.push([xr, y + slant / 2]); pts.push([xl, y - slant / 2]); }
      dir = -dir;
    }
    return wobble(pts, 5, rnd);
  }
  // ground colouring: rows clipped to the paper circle below a wavy horizon
  function scribbleGround(y0, y1, seed, step = 26) {
    const rnd = mulberry32(seed), pts = [];
    let dir = 1;
    for (let y = y0; y <= y1; y += step) {
      const dy = y - PAPER.cy, half = Math.sqrt(Math.max(0, PAPER.r * PAPER.r - dy * dy)) - 6;
      if (half < 30) continue;
      const xl = PAPER.cx - half + (rnd() - .5) * 18, xr = PAPER.cx + half + (rnd() - .5) * 18;
      const s = -6;
      if (dir > 0) { pts.push([xl, y - s]); pts.push([xr, y + s]); } else { pts.push([xr, y + s]); pts.push([xl, y - s]); }
      dir = -dir;
    }
    return wobble(pts, 6, rnd);
  }

  // ---------- the picture ----------
  const TREES = [   // foliage blob + trunk base; our own layout
    { tool: "orange", cx: 255, cy: 880, rx: 118, ry: 178, base: [272, 1178], top: [262, 770], seed: 11 },
    { tool: "yellow", cx: 442, cy: 905, rx: 100, ry: 155, base: [458, 1150], top: [450, 810], seed: 23 },
    { tool: "green", cx: 640, cy: 850, rx: 130, ry: 200, base: [655, 1195], top: [646, 715], seed: 37 },
    { tool: "pink", cx: 850, cy: 905, rx: 100, ry: 152, base: [862, 1152], top: [855, 815], seed: 51 },
  ];
  const HORIZON = 1112;

  function trunkAndBranches(tr, seed) {
    const rnd = mulberry32(seed), strokes = [];
    const [bx, by] = tr.base, [tx, ty] = tr.top;
    // trunk: two strokes that start apart with a little root flare and meet at the top
    for (const off of [-8, 8]) strokes.push(wobble([[bx + off * 2.6, by + 10], ...curve([bx + off, by - 14], [bx + off * 0.6 + (tx - bx) * .5, (by + ty) / 2], [tx + off * 0.1, ty], 12)], 1.5, rnd));
    // branches: alternate sides, angled up and out; the lower two get a twig
    const n = 4;
    for (let i = 0; i < n; i++) {
      const h = 0.3 + i * 0.15, side = i % 2 ? 1 : -1;
      const sx = bx + (tx - bx) * h, sy = by + (ty - by) * h;
      const len = (tr.rx * 0.78) * (1 - h * 0.45) * (0.85 + rnd() * 0.3);
      const ex = sx + side * len, ey = sy - len * (0.75 + rnd() * 0.35);
      const br = wobble(curve([sx, sy], [sx + side * len * 0.55, sy - len * 0.2], [ex, ey], 10), 1.5, rnd);
      strokes.push(br);
      if (i > 0) continue;
      const k = 0.55, px = sx + (ex - sx) * k, py = sy + (ey - sy) * k;
      strokes.push([[px, py], [px + side * len * 0.12, py - len * 0.42]]);
    }
    return strokes;
  }
  function bird(x, y, s) {
    return [...curve([x - 26 * s, y - 4 * s], [x - 14 * s, y - 22 * s], [x - 2 * s, y + 4 * s], 8),
            ...curve([x - 2 * s, y + 4 * s], [x + 12 * s, y - 22 * s], [x + 26 * s, y - 8 * s], 8).slice(1)];
  }

  // ---------- build the timeline ----------
  function build() {
    const strokes = [], actions = [], steps = [];
    let t = 0, hand = OFF.slice(), tool = null;

    const addStroke = (toolName, pts, layer, opts = {}) => {
      const T = TOOLS[toolName];
      // travel (pen lifted) from where the hand is to the stroke start
      const d = dist(hand, pts[0]);
      if (d > 2) {
        const dur = Math.min(0.8, Math.max(0.22, d / 1000));
        actions.push({ type: "travel", tool: toolName, from: hand.slice(), to: pts[0].slice(), t0: t, t1: t + dur });
        t += dur;
      }
      const s = { id: strokes.length, tool: toolName, kind: T.kind, color: T.color, width: opts.width || T.width, pts, layer };
      s.cum = cumul(pts); s.len = s.cum[s.cum.length - 1];
      const dur = Math.max(0.35, s.len / (opts.speed || T.speed));
      s.t0 = t; s.t1 = t + dur;
      strokes.push(s);
      actions.push({ type: "stroke", tool: toolName, stroke: s.id, t0: s.t0, t1: s.t1 });
      t = s.t1; hand = pts[pts.length - 1].slice();
      return s;
    };
    const tap = (toolName, at, layer, color) => {
      const d = dist(hand, at), dur = Math.min(0.6, Math.max(0.3, d / 700));
      actions.push({ type: "travel", tool: toolName, from: hand.slice(), to: at.slice(), t0: t, t1: t + dur });
      t += dur;
      const s = { id: strokes.length, tool: toolName, kind: "dot", color, width: 0, pts: [at], layer, cum: [0], len: 0, t0: t, t1: t + 0.22 };
      strokes.push(s);
      actions.push({ type: "tap", tool: toolName, stroke: s.id, t0: t, t1: t + 0.22 });
      t += 0.3; hand = at.slice();
    };
    const enter = (toolName, to) => {
      actions.push({ type: "enter", tool: toolName, from: OFF.slice(), to: to.slice(), t0: t, t1: t + 1.0 });
      t += 1.0; hand = to.slice(); tool = toolName;
    };
    const exit = () => {
      actions.push({ type: "exit", tool, from: hand.slice(), to: OFF.slice(), t0: t, t1: t + 0.8 });
      t += 0.8; hand = OFF.slice();
    };
    const step = (text, fn) => { const s = { text, t0: t }; steps.push(s); fn(); s.t1 = t; t += 0.5; };

    t = 3.6;   // intro: paper arrives + title
    TREES.forEach((tr, i) => {
      const words = ["1. First tree: color it orange", "2. The second one: yellow", "3. A big tree: green", "4. And a pink tree"][i];
      step(words, () => {
        const pts = scribbleBlob(tr.cx, tr.cy, tr.rx, tr.ry, tr.seed);
        enter(tr.tool, pts[0]);
        addStroke(tr.tool, pts, "tree" + i);
        exit();
      });
    });
    step("5. The ground: yellow… then orange", () => {
      const yl = scribbleGround(HORIZON, 1300, 71, 30);
      enter("groundY", yl[0]); addStroke("groundY", yl, "groundY"); exit();
      const or = scribbleGround(1250, 1500, 83, 28);
      enter("groundO", or[0]); addStroke("groundO", or, "groundO"); exit();
    });
    step("6. Black marker: trunks and branches", () => {
      const all = TREES.map((tr, i) => trunkAndBranches(tr, 100 + i));
      enter("black", all[0][0][0]);
      all.forEach((list, i) => list.forEach(p => addStroke("black", p, "ink")));
      exit();
    });
    step("7. Little birds in the sky", () => {
      const bs = [[560, 655, 1.45], [710, 615, 1.25], [835, 690, 1.1]].map(([x, y, s]) => bird(x, y, s));
      enter("black", bs[0][0]);
      bs.forEach(b => addStroke("black", b, "ink", { speed: 200, width: 8 }));
      exit();
    });
    step("8. Falling leaves", () => {
      const rnd = mulberry32(909);
      const spots = [];
      for (let i = 0; i < 11; i++) {
        const x = 150 + rnd() * 780, y = 1060 + rnd() * 380;
        const dy = y - PAPER.cy, half = Math.sqrt(Math.max(0, PAPER.r * PAPER.r - dy * dy)) - 40;
        if (Math.abs(x - PAPER.cx) < half) spots.push([x, y]);
      }
      for (let i = 0; i < 4; i++) spots.push([220 + i * 190 + rnd() * 40, 990 + rnd() * 60]);   // in the air too
      spots.sort((a, b) => b[0] - a[0] || a[1] - b[1]);
      enter("red", spots[0]);
      spots.forEach(p => tap("red", p, "dots", rnd() > .35 ? "#de4a2c" : "#f07a2a"));
      exit();
    });
    const drawEnd = t;
    const duration = Math.ceil(drawEnd + 6.5);
    return { PAPER, OFF, TOOLS, strokes, actions, steps, drawEnd, duration, pointAt };
  }

  const API = { build, pointAt, PAPER, OFF, TOOLS };
  if (typeof module !== "undefined" && module.exports) module.exports = API;
  else root.Drawing = API;
})(typeof window !== "undefined" ? window : globalThis);
