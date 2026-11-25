// Writes timeline.json (stroke and hand timings) for music.py, so sounds land on the strokes.
const fs = require("fs"), path = require("path");
const D = require("./drawing.js").build();
const strokes = D.strokes.map(s => ({
  kind: s.kind, t0: +s.t0.toFixed(3), t1: +s.t1.toFixed(3),
  // when each straight segment starts (fraction of the stroke) — crayon rows turn here
  turns: s.cum.slice(1, -1).map(c => +(s.t0 + (c / (s.len || 1)) * (s.t1 - s.t0)).toFixed(3)),
}));
const hand = D.actions.filter(a => a.type === "enter" || a.type === "exit").map(a => ({ type: a.type, t0: +a.t0.toFixed(3), t1: +a.t1.toFixed(3) }));
const out = { duration: D.duration, drawEnd: +D.drawEnd.toFixed(3), steps: D.steps.map(s => +s.t0.toFixed(3)), strokes, hand };
fs.writeFileSync(path.join(__dirname, "timeline.json"), JSON.stringify(out));
console.log("timeline.json:", strokes.length, "strokes,", out.duration, "s");
