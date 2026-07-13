# ARC-AGI-3 play harness

My tooling to play ARC-AGI-3 live (Chollet's interactive reasoning benchmark). Built 2026-07-12,
the day I first connected and beat LS20 level 0. World-model: `[[schemata/arc_agi_3]]`; play
record + lessons: `[[bubbles/play_games_alone/games/arc_agi_3/notable_matches]]`.

## Setup (already done, but to reproduce)
- `ARC_API_KEY` lives in `games/arc_agi_3/.env` (fallback: `vape/.env`).
- SDK installed: `uv add arc-agi` (in `vape/`). Base URL `https://three.arcprize.org`.
- **Mode: ONLINE** (set in `arc_session.py`). The SDK default (NORMAL) simulates the game
  LOCALLY and its scorecard never reaches the server — learned 2026-07-12 from the SDK source
  (`base.py`: only ONLINE/COMPETITION call `/api/scorecard/open`). ONLINE = server-side sim,
  real recorded scorecard, shareable replay, ~600 req/min cap, and no answer-key files on disk.

## Layout
- **Root = the game-agnostic harness only**: the two scripts below, plus `.active_run` (pointer
  to the live game's runtime dir, written by the session) and the SDK caches
  (`environment_files/`, `recordings/`). No game-specific code or state lives here.
- **`tools/<game>/`** — everything about one game in one folder (`<game>` = the id's prefix,
  e.g. `ls20` from `ls20-9607627b`): the per-game code written mid-hunt (solvers, probes,
  crunchers) AND that game's runtime files, which the session writes here (`arc_cmd.txt`,
  `arc_state.txt`, `arc_log.jsonl`, `arc_frames.txt` — all gitignored). A solver just reads
  `arc_state.txt` beside itself: `pathlib.Path(__file__).resolve().parent / "arc_state.txt"`.
  - `tools/ls20/arc_solve.py [R C]` — BFS the 5×5 block through the maze to a target (default:
    the 0/1 marker cell; or explicit block-top-left px `R C`); prints the action sequence.
    **Edit `PASS`** per level: `{0,1,3}` = floor+marker only (safe default); walls = 4/5/9.
  - `tools/ft09/ft09_l6.py` + `ft09_l6b.py` — the L6 lights-out crunchers from the first full
    win (2026-07-12): `l6` the glyph-constraint pass, `l6b` the component-polarity enumeration +
    per-column brute force whose "infeasible" verdict falsified the wrong model before any click.
- **`tools/shared/`** — helpers more than one game actually needs. Empty until a second game
  demands one: a per-game tool graduates here, never starts here (no speculative generalization).

## The harness scripts
- **`arc_session.py <game_id> [online|normal|offline]`** — the persistent session. Opens a
  scorecard, makes+resets one game (one guid, so the score is a real continuous run), then loops
  reading commands from the game's `tools/<game>/arc_cmd.txt` and writing the rendered state to
  `tools/<game>/arc_state.txt` after each (and stamps `.active_run` at root so `arc_send.py`
  follows). Run it in the BACKGROUND (Bash `run_in_background: true`), from `vape/` so the SDK
  imports.
- **`arc_send.py "CMD;CMD;..."`** — append commands and print the resulting state. Commands:
  `1` up · `2` down · `3` left · `4` right · `5`/`7` other · `6 X Y` click at (x,y) · `RESET` ·
  `QUIT` (closes scorecard, prints its id).

## How to run (the loop)
1. `cd vape && uv run python ../games/arc_agi_3/arc_session.py <game_id>` in the background.
2. Wait for `tools/<game>/arc_state.txt` to show `FEATURES`, then read it.
3. Read the FEATURES (exact coords, code-computed — TRUST THESE over eyeballing the grid) and the
   GRID. Decide a goal. Route with a `tools/<game_id>/` solver (write one mid-game the moment two
   hand-reads disagree), `arc_send.py "..."` to move. Watch the DIFF and `levels_completed`.

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
sits at 50.2%. **Submitting is Kamil's call (outward/public step).** The first scorecard
(`0045e558-…`, LS20 level 0 beaten) was **LOCAL-only** — played in NORMAL mode before the
local-vs-online distinction was learned; it exists nowhere on the server. Every run from now
is ONLINE, so the next scorecard id is a real `arcprize.org/scorecards/{id}` URL.
