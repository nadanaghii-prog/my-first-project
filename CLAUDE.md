# my-first-project — Instagram videos drawn in code

Short vertical videos (Instagram Reels, 1080x1920, 30fps) where every frame is drawn in code
(SVG/HTML) — no video-generation model — with sound synthesized in Python or voiced by Kokoro.

## How to make a video

Use the `animate` skill (`.claude/skills/animate/SKILL.md`). It holds the house styles so new
videos look like the earlier ones. Existing videos live in `videos/<name>/`:

- `videos/bunny-family/` — "storybook" style (children's-book illustration)
- `videos/origami/` — "origami" style (folded paper)
- `videos/render.js` — renders any `videos/<name>/scene.html` + `music.wav` to `videos/<name>/<name>.mp4`

All motion follows Disney's 12 principles via the `motion-designer` skill
(`.claude/skills/motion-designer/`, helpers in `scripts/motion.js`); review every video with its checklist.

HyperFrames (`npm install` brings it back) and its skills (`.claude/skills/hyperframes*`, `media-use`)
are available for timeline/GSAP-based compositions, captions and voiceover.

## Rules

- **No usage beacon / telemetry.** The owner opted out. Never run `hyperframes events`, and skip the
  "usage note" step the HyperFrames skills ask for. Keep `hyperframes telemetry` disabled.
- **Pin the HyperFrames CLI** to the version in `package.json` (currently 0.9.91), e.g.
  `node .claude/skills/hyperframes/scripts/plugin-cli.mjs --cli-version 0.9.91 render ...`,
  so renders stay identical across sessions.
- **Voice:** Kokoro (`hyperframes tts`, or the venv at `/opt/kokoro-venv`, set `HYPERFRAMES_PYTHON=/opt/kokoro-venv/bin/python`) supports English,
  Spanish, French, Hindi, Italian, Japanese, Portuguese, Chinese — **not Arabic**. Say so before
  promising an Arabic voiceover.
- On-screen Arabic text uses the Lalezar font in `videos/bunny-family/fonts/`.
- Use reference images only as style inspiration; never trace or copy someone else's artwork.
- Commit each finished video (scene, music script and the MP4); don't commit `music.wav`.
