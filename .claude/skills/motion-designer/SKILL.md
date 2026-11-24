---
name: motion-designer
description: Plan, animate and review motion using Disney's 12 principles of animation (squash & stretch, anticipation, staging, pose to pose, follow through & overlapping action, slow in & slow out, arcs, secondary action, timing, exaggeration, solid drawing, appeal). Use whenever a video or animation is being made or reviewed in this project — characters, objects, titles or transitions — or when the owner says motion feels stiff, robotic, floaty, flat or "not Disney enough".
---

# Motion Designer — the 12 principles, applied in code

Use with the `animate` skill (style + pipeline) or HyperFrames. This skill decides **how things
move**. Helpers live in `scripts/motion.js` (pure functions of time, tested); details and numbers per
principle are in `references/principles.md`; the gate before delivery is `references/review-checklist.md`.

## Load the helpers

In a `scene.html`, copy the file next to the scene (so the video folder stays self-contained) and load it:

```html
<script src="motion.js"></script>   <!-- cp .claude/skills/motion-designer/scripts/motion.js videos/<name>/ -->
<script> const { tween, jump, followThrough, impact, anticipate, arc, blink, breathe, ease } = Motion; </script>
```

## Work like an animator (in this order)

1. **Staging first (3).** One idea per shot. Decide where the eye goes at each second; everything
   else is quieter (smaller motion, lower contrast, behind). Write the beat sheet as a comment:
   `0.0–1.5 set the scene · 1.5–3 hero enters · 3.2 KEY MOMENT · ... · 7.0 title`.
2. **Key poses (4).** For every action write the storytelling poses with times using `tween()`
   keyframes — pose to pose. Use straight-ahead (procedural: `spring`, `noise`, particles) only for
   fire, water, smoke, hair, leaves.
3. **Timing (9).** Assign durations from `TIMING` / frame counts; fast = light or excited, slow = heavy
   or calm. Leave holds so the viewer can read a pose (≥ 0.3s), and ~2s for any text.
4. **Add the physics feel:**
   - **Anticipation (2)** before every significant action (`anticipate`, the crouch in `jump`).
   - **Slow in / slow out (6)**: never `linear` for living things; pick easing per segment.
   - **Arcs (7)**: limbs, heads, thrown or flying things travel on curves (`arc`, `swing`).
   - **Squash & stretch (1)**: on impacts and fast moves, keeping volume (`squash`, `impact`).
   - **Follow through & overlap (5)**: ears, tails, hair, clothes and leaves keep going and settle
     after the body stops (`followThrough`, `lag`, `stagger`).
5. **Secondary action (8).** Add one supporting motion that reinforces (blink, breathing, a tail
   flick, smoke) — never one that competes with the main action.
6. **Exaggeration (10).** Push the key poses and moments 30–60% past realistic (`exaggerate`);
   keep the rest calm so the push reads.
7. **Solid drawing (11) & Appeal (12).** Shapes keep their volume and weight; characters have
   clear silhouettes, simple shapes, big readable eyes, a sense of personality in how they move.
8. **Review.** Render 5–8 preview frames *plus* a contact sheet of one action at 10–15 fps
   intervals, and run `references/review-checklist.md`. Fix, then render the MP4.

## Quick recipes

| Want | Use |
|---|---|
| Character hops happily | `const j = jump(t, 3.2, {height: 90}); transform="translate(x ${-j.y}) scale(${j.sx} ${j.sy})"` + ears `followThrough(t, 3.2+0.16+0.5, 14)` |
| Object pops in | `scale = ease.outBack(progress(t, t0, 0.45))` (overshoot) or `spring(t, t0)` |
| Something drops and lands | `y = tween(t, [[t0, -400], [t0+0.5, 0, "inQuad"]])` + `impact(t, t0+0.5)` |
| Head turn / look | `tween` with `inOutSine`, anticipate 5–10° the other way, ears lag 0.06s |
| Wave hello | `swing()` on the forearm, upper arm `lag` 0.08s, overshoot on the first wave |
| Text title | letters `stagger(i, 0.04)` + `outBack`; hold ≥ 2s |
| Idle (never frozen) | `breathe`, `blink`, `movingHold` |

## Principles at a glance

1 Squash & stretch · 2 Anticipation · 3 Staging · 4 Straight ahead & pose to pose ·
5 Follow through & overlapping action · 6 Slow in & slow out · 7 Arcs · 8 Secondary action ·
9 Timing · 10 Exaggeration · 11 Solid drawing · 12 Appeal — see `references/principles.md`.
