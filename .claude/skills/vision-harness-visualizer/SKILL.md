---
name: vision-harness-visualizer
description: >-
  Render any structured state a harness hands back — a grid, board, map, frame,
  layout, or matrix — into a PNG and LOOK at it with multimodal vision, instead
  of parsing raw arrays as text. Use whenever a game server, simulator, solver,
  scraper, or tool returns spatial/structured state; when about to reason about
  a board or layout held in the head; when two readings of the same state
  disagree; or when checking what actually changed after an action (diff view).
  Ships a default zero-dependency renderer plus a template for custom worlds.
---

# Vision Harness Visualizer

The model has real multimodal vision, and most sessions leave it idle while the
text side squints at `[[0,3,0],[3,3,1],...]` and hallucinates the shape. This
skill is the reflex that fixes that: **externalize the exact state into pixels,
then look at it**.

## The principle — two organs, one loop

- **Code holds the exact state.** Coordinates, counts, equality checks — those
  come from the data, never from the picture.
- **Vision reads the gestalt.** Shape, symmetry, connectivity, clusters,
  alignment, "what is odd here" — a rendered image answers in one glance what a
  raw array hides behind indices.
- The loop: source of truth → deterministic render → **look** → judge → act →
  re-render. A stale image is as dangerous as a fluent guess: re-render after
  **every** state change; never reason from the previous picture.

Vision complements the exact checks, never replaces them. If the picture and
the data disagree, the data wins — then fix the renderer.

## When to reach for it

- A harness (game server, simulator, emulator, layout engine, sensor dump,
  solver) returns state as a matrix/grid/frame/scene.
- You catch yourself reasoning about spatial structure held "in the head."
- Two hand-reads of the same state disagree — render, look, settle it.
- After an action: what ACTUALLY changed? (`--diff` rings every changed cell.)
- Before claiming a transformation worked: render input and output side by side.

Skip it only when the state is truly non-spatial (a scalar, a flat config) or
so tiny that text is already unambiguous.

## The default tool

`​.claude/skills/vision-harness-visualizer/tools/render_state.py` — pure
standard library, runs with any `python3` (or `uv run python`) on any OS.

```bash
# 1. dump the exact state to JSON (from the source of truth, not from memory)
# 2. render
uv run python .claude/skills/vision-harness-visualizer/tools/render_state.py state.json --labels
# 3. Read the printed PNG path with the Read tool — actually look at it
```

Input shapes it accepts:

| JSON | Renders as |
|---|---|
| `[[0,1],[2,3]]` | one grid |
| `[[[...]], [[...]]]` | panels side by side (before/after, frames) |
| `{"grid": ...}` | one grid, wrapped |
| `{"grids": [...], "palette": {"1": "#ff0000"}, "title": "..."}` | panels + palette override |

Cell values may be ints (0–15 map to a stable 16-color palette), strings,
floats, bools, or `null` (drawn as background); anything non-int gets a stable
hashed color. The legend (`value=#hex`) prints to stdout — read it together
with the image so colors keep their meaning.

The defaults are tuned for machine vision, whose known weaknesses are thin
lines, low contrast, and cell-counting: thick auto-scaling gridlines, a hard
black border around every panel, and **0-based coordinate rulers on by
default** (columns across the top, rows down the left — row down, column
right), so a cell can be named by index straight off the picture.

Options:

- `--labels` — draw numeric values inside cells (digits/`-`/`.`; auto-skipped
  when they don't fit)
- `--diff PREV.json` — double-ring (white+black) every cell that changed
- `--no-coords` — drop the index rulers (they're on by default)
- `--cell N` / `--gap N` — cell pixel size (default auto ≤~1100px wide) /
  gridline thickness (default auto, never thinner than 2px)
- `--palette '{"7":"#00ff88"}'` — inline color override
- `-o OUT.png` — output path (default: system temp dir; the path always prints)
- input `-` reads stdin: `echo '[[0,1],[1,0]]' | uv run python …/render_state.py -`

## Discipline

- **Stable palette per session.** If a value means "wall," keep it the same
  color in every render, or the eye re-learns the world each glance.
- **Diff, don't re-stare.** After an action, `--diff` against the prior dump —
  the rings take you straight to what moved.
- **Prefer files over inline JSON** for state (shell quoting eats brackets).
- **Verify the renderer once per new world**: render a state you already know
  and look — a wrong renderer is a wrong world.

## Custom worlds

When the world isn't a grid (entity maps, node graphs, timelines, page
layouts), copy `tools/custom_renderer_template.py`, fill in the layout section,
and keep the same contract: exact state in → deterministic pixels out → path on
stdout → look. All drawing primitives (`Canvas`, `save_png`, `color_for`, the
digit font) are importable from `render_state.py`; still zero dependencies.
