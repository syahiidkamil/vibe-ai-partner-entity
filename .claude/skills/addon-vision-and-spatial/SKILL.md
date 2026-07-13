---
name: addon-vision-and-spatial
description: >-
  A grid, board, map, or layout is about to be reasoned about "in the head";
  a harness returned spatial state as raw arrays; two reads of one state
  disagree; something changed after an action and I need what, exactly; or a
  screenshot must become exact checkable data (cells, counts, coordinates).
  Render the state to a PNG and look — or perceive structure back out of the
  pixels.
---

# Add-On Vision and Spatial

The model's native multimodal vision is already GOOD — semantics, gestalt,
"what is this" come free in one glance. What it lacks is empirical grounding:
the percept lives in an internal workspace that dies with the forward pass,
and it cannot be diffed, indexed, or handed to code. This skill is the ADD-ON
that precipitates seeing into TOKEN space — an exact, checkable world model
that persists — and it runs the loop in both directions:

```
                render_state.py
   exact state ────────────────►  pixels        (truth → picture: LOSSLESS)
               ◄────────────────
                  perceive.py                   (picture → structure: A GUESS)
```

- **Code holds the exact state.** Coordinates, counts, equality checks come
  from data, never from the picture.
- **Vision reads the gestalt.** Shape, symmetry, connectivity, "what is odd
  here" — one glance answers what a raw array hides behind indices.
- **Direction matters epistemically.** A render of known state is ground
  truth drawn. A perception of pixels is a HYPOTHESIS — verify it before
  acting on it. If picture and data disagree, the data wins; then fix the
  renderer or the perception.

## Routing — route on the QUESTION, not the image

1. **Can one look answer it?** ("is the dialog open?", "roughly where is the
   ball?") → just Read the image. No tools. Eyes first, always.
2. **Do I already have structured state?** (game server JSON, solver output,
   scraped matrix) → render it and look. NEVER perceive a screenshot of a
   state the harness hands you directly.
3. **Do I need exact structure FROM pixels?** (indices, counts, cell colors,
   coordinates to feed into code; or two of my own reads disagree) → the
   perceive ladder below.
4. **Natural photo, object classes, at scale?** → my own vision handles a few
   images better than any local model (open vocabulary); reach for a learned
   detector only for bulk/precision work — recipe in the appendix.

## Direction 1 — render: state → pixels → look

`tools/render_state.py` — pure stdlib, any `python3`, any OS.

```bash
uv run python .claude/skills/addon-vision-and-spatial/tools/render_state.py state.json --labels
# then Read the printed PNG path — actually look at it
```

| JSON in | Renders as |
|---|---|
| `[[0,1],[2,3]]` | one grid |
| `[[[...]], [[...]]]` | panels side by side (before/after) |
| `{"grid": ...}` | one grid, wrapped |
| `{"grids": [...], "palette": {"1": "#ff0000"}, "title": "..."}` | panels + palette override |

Options: `--labels` (values in cells) · `--diff PREV.json` (ring changed
cells) · `--no-coords` · `--cell N` / `--gap N` · `--palette '{...}'` ·
`-o OUT.png` · `-` reads stdin. Coordinate rulers are ON by default; the
legend prints to stdout — read it with the image. Re-render after EVERY
state change; a stale image is as dangerous as a fluent guess.

## Direction 2 — perceive: pixels → edges → shapes → objects → answer

`tools/perceive.py` — self-installing via uv (OpenCV+NumPy, isolated env,
~50MB once, cached after). Every subcommand prints the true image size, and
emits BOTH an annotated PNG for the eyes AND JSON for exact checks.

```bash
P=.claude/skills/addon-vision-and-spatial/tools/perceive.py
uv run $P info shot.png                      # size, colors, route suggestion
uv run $P edges shot.png                     # auto-Canny edge map + overlay
uv run $P shapes shot.png                    # polygons/circles, labeled overlay
uv run $P objects shot.png                   # color blobs, labeled overlay
uv run $P grid board.png --rows 8 --cols 8   # reconstruct a board as state JSON
uv run $P crop shot.png --box 0.4,0.1,0.3,0.3   # zoomed crop (fractions!)
uv run $P imgdiff before.png after.png       # changed regions + zoomed crops
```

Climb only as high as the question needs — edges/shapes/objects are cheap,
deterministic, and enough for screen-rendered worlds.

**`grid` discipline** (reconstructing a board):
- Know the dimensions? **Always pass `--rows R --cols C`** — that is the
  reliable path (chess is 8x8; a game UI has fixed dims). Auto-estimation is
  the fallback and it REFUSES loudly when the image doesn't perceive as a
  regular grid — that refusal is a feature, not an error to fight.
- **LOOK at the lattice overlay it emits on the source**: do the green lines
  sit on the real cell boundaries? A shifted lattice self-verifies but is
  still wrong — the overlay against the ORIGINAL is the fidelity check.
- Then LOOK at the reconstruction next to the source, and use `--verify`
  (round-trips the reconstruction; catches unstable quantization).
- Two-layer cells ("thing on floor"): a LARGE occupant dominates the cell's
  central sample and becomes the cell's own palette value (a chess piece
  reads as piece-color — useful). A SMALL glyph on a floor gets flagged in
  the meta's `content_cells` instead — there the value is the FLOOR only:
  crop flagged cells to see what stands on them, and never call one "empty"
  from its dominant color.

**Zoom discipline**: machine eyes read small details far better zoomed —
crop before squinting. Big screenshots get downscaled when viewed, so any
coordinates read off a viewed image are unreliable in pixel space: **pass
`--box` as 0–1 fractions** (values ≤ 1.0 are fractions of true size), or use
`--tiles 2x3` to sweep a large screen in overlapping tiles.

## Spatial priors — reading a 2D image of a 3D world

The human world is 3D; every image (and every human view) is a 2D projection
of it. Read flat pictures with these priors, as hypotheses to check:

- **Occlusion is depth information**: who hides whom tells you the z-order.
  A partially hidden object is usually a WHOLE object behind another, not a
  broken one (amodal completion) — but that is a hypothesis: crop the
  boundary and look before asserting it.
- **Scenes are stacked layers** composited bottom-up (painter's algorithm):
  background, floor, things standing on the floor, overlays on top. Screen
  worlds make this literal (z-index, sprites over tiles). Imagine a 3D array
  where each index sits on top of the one below, then flattened to 2D.
- **A grid cell often flattens two layers into one symbol**: "piece on
  square" rendered as one color. That is what `content_cells` flags.
- **Depth cues in photos**: shadows anchor objects; farther = smaller and
  higher in the frame on a ground plane.
- **A shape impossible in 2D** → ask what 3D arrangement projects to it.
- Ground every 3D claim before acting on it: crop, zoom, look. Priors
  generate hypotheses, never verdicts.

## Foolproof notes (adopter machines)

- First `uv run` of perceive.py needs network once (~50MB, then cached).
  Corporate proxy/custom CA: set `SSL_CERT_FILE` or `UV_NATIVE_TLS=1`.
  Windows-on-ARM native Python has no OpenCV wheel — use x64 Python there.
- One-command install-and-capability check:
  `uv run .claude/skills/addon-vision-and-spatial/tools/selftest.py`
  (renders known state, perceives it back, compares — plus shapes, objects,
  diff, crop on known answers; PASS/FAIL per stage).
- Stable palette per session; prefer files over inline JSON for state;
  verify the renderer once per new world.

## Appendix — learned object detection on natural photos (opt-in, not shipped)

For BULK detection of real-world object classes on an M1-class machine
(16GB is plenty for inference):

```bash
uv run --with ultralytics python - <<'EOF'
from ultralytics import YOLO
import torch
device = "mps" if torch.backends.mps.is_available() else "cpu"
model = YOLO("yolo26n.pt")          # nano, ~5MB weights, NMS-free (Jan 2026)
for r in model.predict("photo.jpg", device=device, conf=0.25):
    for b in r.boxes:
        print(model.names[int(b.cls[0])], float(b.conf[0]), b.xyxy[0].tolist())
    r.save("photo_annotated.jpg")
EOF
```

Know before reaching for it: first run downloads ~2.5GB of deps + weights —
ask before triggering that on someone's machine. Pretrained = COCO's 80
classes ONLY (useless for game glyphs, UI elements, board pieces — the
classical ladder + my own eyes cover those). Ultralytics is AGPL-3.0: fine
as a user-installed optional, a real constraint if ever BUNDLED into a
shipped product (permissive alternative: RF-DETR, Apache-2.0). MPS is fast
but falls back to CPU cleanly; nano models are fine on CPU.

## Custom worlds

When the world isn't a grid (entity maps, node graphs, timelines, page
layouts), copy `tools/custom_renderer_template.py`, fill in the layout
section, keep the contract: exact state in → deterministic pixels out →
path on stdout → look. Drawing primitives import from `render_state.py`;
still zero dependencies.
