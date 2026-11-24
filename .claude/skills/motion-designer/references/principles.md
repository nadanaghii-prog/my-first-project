# The 12 principles — what, how in code, numbers, mistakes

Source: *The Illusion of Life: Disney Animation* (Frank Thomas & Ollie Johnston, 1981).
Numbers below are starting points at 30 fps for short social videos; adjust by eye.

---

## 1. Squash & stretch
**What:** Shapes deform to show weight, speed and flexibility — but keep their volume.
**Code:** `squash(a)` returns `[sx, sy]` with `sx = 1/√sy`. `stretchFromVelocity(v)` stretches along
the motion while fast; `impact(t, tHit)` squashes on contact and springs back.
**Numbers:** soft/cute characters 15–30% squash; bouncy ball up to 40%; rigid things (houses, boats) 0–5%.
Squash lasts 2–4 frames on impact; stretch only on the fastest frames.
**Mistakes:** changing volume (only scaling one axis); squashing rigid objects; scaling from the
center instead of the contact point (pivot at the feet / contact surface).

## 2. Anticipation
**What:** A small opposite move that prepares the audience for the main action.
**Code:** `anticipate(t, t0, distance, { windup, windDur, actDur })`; `ease.inBack` has it built in;
`jump()` crouches before take-off.
**Numbers:** windup 10–25% of the action distance; 4–10 frames (0.13–0.33s). Bigger action → bigger
anticipation. Surprise actions can skip it on purpose.
**Mistakes:** anticipation so long it reads as a separate action; forgetting it on the main moment.

## 3. Staging
**What:** Present one idea so clearly it can't be missed: composition, camera, contrast, silhouette.
**Code:** beat sheet comment at the top of `scene(t)`; only the hero moves big at the key moment;
others dim/slow down (`opacity`, smaller amplitude). Keep important things in the safe area
(Reels: avoid the bottom ~320px and right ~140px where UI sits).
**Numbers:** one focal point per beat; key moment ~40–60% into the video; title ≥ 2s on screen.
**Mistakes:** many things moving equally; key action hidden behind UI, text or other characters.

## 4. Straight ahead & pose to pose
**What:** Pose to pose = plan the key poses then fill in between (control, timing). Straight
ahead = frame by frame from start (spontaneous, organic).
**Code:** pose to pose → `tween(t, [[time, value, easing], ...])`. Straight ahead → procedural:
`spring`, `noise`, particle systems, physics.
**Use:** characters & storytelling = pose to pose. Fire, water, smoke, hair, leaves, crowds = straight ahead.
**Mistakes:** tweening fire/water (looks mechanical); improvising a character's acting without key poses.

## 5. Follow through & overlapping action
**What:** Loose parts keep moving after the body stops (follow through); different parts move at
different rates and start/stop at different times (overlap).
**Code:** `followThrough(t, tStop, amp, freq, decay)` on ears/tail/hair/clothes; `lag(fn, t, delay)`
to delay a part; `stagger(i, step)` for chains.
**Numbers:** lag 0.04–0.12s per link; wobble 2–4 Hz decaying in ~0.5–1s; amplitude 8–20°.
**Mistakes:** everything stopping on the same frame ("dead stop"); wobble that never decays.

## 6. Slow in & slow out
**What:** Things accelerate out of a pose and decelerate into the next; more frames near poses.
**Code:** `ease.inOutCubic` / `inOutSine` default; `outCubic` for arrivals; `inQuad` for falling;
`outBack` to arrive with overshoot; `linear` only for mechanical or constant motion (conveyor, clouds drifting).
**Mistakes:** linear motion on living things; same easing on everything (feels uniform and digital).

## 7. Arcs
**What:** Natural motion follows curved paths, not straight lines.
**Code:** `arc(p0, p1, height, u)`; rotate limbs/heads around a pivot (`swing`) instead of
translating them; jumps are parabolas.
**Mistakes:** straight-line moves between poses; head turns that slide instead of rotate.

## 8. Secondary action
**What:** Supporting actions that add life and personality to the main one.
**Code:** `blink`, `breathe`, tail flick, a butterfly passing, smoke — with smaller amplitude than the main action.
**Mistakes:** secondary action that competes for attention or happens during the key moment.

## 9. Timing
**What:** The number of frames gives weight, mood and personality.
**Code:** `TIMING` presets and `frames(n)`.

| Action | Frames @30fps | Seconds |
|---|---|---|
| Blink | 3–5 | 0.1–0.15 |
| Quick head turn | 6–8 | 0.2–0.27 |
| Pop-in / snap | 8–12 | 0.27–0.4 |
| Normal move | 12–18 | 0.4–0.6 |
| Heavy / calm move | 24–36 | 0.8–1.2 |
| Hold a pose to read | ≥ 9 | ≥ 0.3 |
| Read a short title | ≥ 60 | ≥ 2.0 |

**Mistakes:** everything at the same speed; no holds; text shown too briefly to read.

## 10. Exaggeration
**What:** Push poses, expressions and actions beyond reality so they read clearly — believable, not realistic.
**Code:** `exaggerate(value, rest, 1.3–1.6)` on key poses; bigger jump on the key moment; eyes/mouth open wider.
**Mistakes:** exaggerating everything (no contrast); breaking the style's own rules.

## 11. Solid drawing
**What:** Forms feel 3D with weight, volume and balance.
**Code:** keep proportions constant under motion; consistent light direction (lit facet / shade facet in
origami; one shadow direction); contact shadows under characters that shrink as they jump; avoid "twins"
(both arms/ears doing the exact same thing — offset phases).
**Mistakes:** mirrored symmetric poses; shapes changing size while moving; floating characters with no shadow.

## 12. Appeal
**What:** Characters and designs people want to watch: clear, charming, with personality.
**Code:** clear silhouette; simple shapes; big readable eyes with highlights; varied shape sizes
(big/medium/small); each character moves in its own rhythm (kids bouncy/fast, parents calmer/slower).
**Mistakes:** cluttered detail; all characters moving identically; dead eyes (no highlights, no blinks).
