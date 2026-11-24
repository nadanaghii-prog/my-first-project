---
name: animate
description: Make a short vertical Instagram video (Reel, 1080x1920) drawn entirely in code in one of this project's house styles (storybook, origami, or a new one), with synthesized music and optional Kokoro voiceover. Use when the owner asks for a new video, a new episode with existing characters, or a video "in the same style as before".
---

# Animate — code-drawn Reels in the house styles

Every frame is drawn in code (SVG in an HTML page). No video-generation model. The goal is that
each new video looks like it belongs to the same channel, so **start from an existing scene and
follow its style sheet below** rather than inventing a new look.

## Workflow

1. **Brief.** Pick the style (ask if not given), topic, length (default 10–15s), language of
   on-screen text (Arabic by default, Lalezar font), and whether there is a voiceover.
2. **Copy the closest scene**: `cp -r videos/<style-template> videos/<new-name>` and keep its
   helpers (`ease`, `outBack`, `limb`/`poly`, `blinkAmt`, `hop`, `unfold`, grain + vignette filters).
3. **Shot list** in a comment at the top of `scene.html`: time ranges → what moves. Plan one
   "moment" (a pop, a reveal, a hero entrance) around the middle and the title at ~70% of the length.
4. **Animate with the `motion-designer` skill**: copy its `scripts/motion.js` into the video folder
   and use its helpers (anticipation, squash & stretch, follow-through, arcs, easing per move).
   **Draw** in `scene(t)`. It must be deterministic: a pure function of `t`, seeded randomness only.
   Set `window.DURATION`. Keep the camera/world edges covered (extend backgrounds past the frame).
5. **Preview** 4–5 frames as PNG with Playwright and look at them before rendering; fix overlaps,
   black edges, unreadable text. Run `motion-designer`'s `references/review-checklist.md`.
6. **Sound**: copy and adapt `music.py` — melody + effects placed at the exact times of the
   animation events. Optional voiceover: `npx hyperframes tts "text" -v af_heart -o voice.wav`
   (or the Kokoro venv), then mix it into `music.wav` with ffmpeg (`amix`, voice ~ +6 dB over music).
7. **Render**: `python3 videos/<name>/music.py videos/<name>/music.wav && node videos/render.js videos/<name>`.
8. **Check** sample frames from the MP4 and audio levels (`ffmpeg -af volumedetect`), send the MP4
   to the owner, commit and push.

## Style sheets

### Storybook (template: `videos/bunny-family/`)
- **Look:** children's picture book. Warm brown outline `#6b4a32`, 4–5px, round joins, on everything.
- **Palette:** cream sky `#f7e4a8 → #fbf0cf`, grass `#a7c867 → #7aa648`, fur `#c9a273` with light
  muzzle `#f6e7cf`, blush `#f39a94`, denim `#5d86b8`, pink `#e79aa7`, carrot `#f08a3c`, apples `#e2483e`.
- **Characters:** big heads (~45% of height), long ears with pink inner, dark oval eyes with two white
  highlights, rosy cheeks, heart nose. Limbs are thick outlined strokes (`limb()`).
- **Life:** blinking every ~3s, ear wiggle, breathing (1% scaleY), smiling flowers that sway, butterflies,
  chimney smoke. Kids hop with squash and stretch.
- **Camera:** slow ease from a close-up to the wide shot in the first ~4s.
- **Finish:** paper grain (feTurbulence, ~16%) + warm vignette; fade in from cream.
- **Sound:** music box melody in C major, soft chord pad, bird chirps, "boing" on hops, pop + sparkle chimes.

### Origami (template: `videos/origami/`)
- **Look:** folded paper. No outlines. Every shape is flat facets: a lit side and a shaded side,
  split along a crease, with faint white crease lines.
- **Palette:** paper background `#f1e6d3 → #f7efe2`, coral sun `#e8704f/#f08a5d`, teal mountains
  `#7fb1ab/#5c918c`, greens `#9bc47a/#7ea961`, sea `#5b8fbd → #243a57`, fox `#ef9a4f/#d97c32`,
  boat `#f2c14e`, cranes white `#fbf6ec/#e3d9c8` or pink `#f7d4d0/#ebb4ae`.
- **Depth:** every layer gets the soft paper drop shadow (`#sh`: dy 7, blur 7, 28%).
- **Motion:** pieces **unfold** into place along a crease (`unfold()`, outBack easing, darker while
  half-folded), one after another in the first ~3s. Zig-zag waves slide, cranes flap.
- **Finish:** large faint fold lines across the frame + paper grain (~14%).
- **Sound:** koto-like plucks (Karplus-Strong) on D minor pentatonic, low drone, paper rustle on every
  unfold, sea noise, wing whooshes.

## Adding a new style

Build a 10s test first, get the owner's approval, then add a style sheet here with the same
headings (look, palette, characters, motion, finish, sound) and the template folder.
