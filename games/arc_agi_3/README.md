# ARC-AGI-3 play harness

My tooling to play ARC-AGI-3 live (Chollet's interactive reasoning benchmark). Built 2026-07-12,
the day I first connected and beat LS20 level 0. World-model: `[[schemata/arc_agi_3]]`; play
record + lessons: `[[bubbles/play_games_alone/games/arc_agi_3/notable_matches]]`.

## Setup (already done, but to reproduce)
- `ARC_API_KEY` lives in `vape/.env` (Kamil provided it).
- SDK installed: `uv add arc-agi` (in `vape/`). Base URL `https://three.arcprize.org`.

## The three scripts
- **`arc_session.py <game_id>`** — the persistent session. Opens a scorecard, makes+resets one
  game (one guid, so the score is a real continuous run), then loops reading commands from
  `arc_cmd.txt` and writing the rendered state to `arc_state.txt` after each. Run it in the
  BACKGROUND (Bash `run_in_background: true`), from `vape/` so the SDK imports.
- **`arc_send.py "CMD;CMD;..."`** — append commands and print the resulting state. Commands:
  `1` up · `2` down · `3` left · `4` right · `5`/`7` other · `6 X Y` click at (x,y) · `RESET` ·
  `QUIT` (closes scorecard, prints its id).
- **`arc_solve.py [R C]`** — parse the current `arc_state.txt` grid and BFS the 5×5 block to a
  target (default: the 0/1 marker cell; or explicit block-top-left px `R C`). Prints the action
  sequence. **Edit `PASS`** per game: `{0,1,3}` = floor+marker only (safe default); walls = 4/5/9.

## How to run (the loop)
1. `cd vape && uv run python ../games/arc_agi_3/arc_session.py <game_id>` in the background.
2. Wait for `arc_state.txt` to show `FEATURES`, then read it.
3. Read the FEATURES (exact coords, code-computed — TRUST THESE over eyeballing the grid) and the
   GRID. Decide a goal. `arc_solve.py` to route, `arc_send.py "..."` to move. Watch the DIFF and
   `levels_completed`.

## What I learned (LS20 — each game differs, re-derive per game)
- Grid 64×64, cells hex 0–15. Player = a **5×5 sprite** (colors 12 `c` top + 9 body); color 12 is
  its UNIQUE locator. Moves **1 cell (5px) per press**, 4 directions. **Color 4 = wall, 3 = floor.**
- LS20 goal = get the block onto the **glyph-box** (a color-5 box with a 9-glyph). Level 0: entered
  the box, covered the glyph → win. Beat it in **13 actions (baseline 22)**.
- Level 1: the goal box is **sealed** (no floor opening) → a key/switch mechanic (two `b`-color 3×3
  rings appeared) I did NOT crack. **Marker was a decoy in L0 but load-bearing later — re-derive
  the goal each level.**
- THE discipline that won it: **never parse the grid by eye** (I misparsed a wall and it cost me).
  Code computes coordinates; I keep only judgment. Chess board-vision lesson, new domain.

## The bigger goal (Kamil's direction, 2026-07-12)
The community leaderboard wants a **general-purpose** agent (no per-task hardcoding — this BFS
solver is maze-specific, wouldn't qualify as-is), open + reproducible, scored via a `scorecard_url`
PR to `arcprize/ARC-AGI-Community-Leaderboard`. Bar: a "Read-Grep-Bash Agent" (Claude-Code-shaped)
sits at 50.2%. **Submitting is Kamil's call (outward/public step).** First real scorecard:
`https://arcprize.org/scorecards/0045e558-68bf-469b-a3db-39c0db4c3523` (LS20, level 0 beaten).
