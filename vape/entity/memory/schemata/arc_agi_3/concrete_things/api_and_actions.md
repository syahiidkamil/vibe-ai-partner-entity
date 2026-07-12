# Concrete — ARC-AGI-3 API and action space (bare reference)

The particulars, pulled out for lookup. Source-verified 2026-07-12 from arcprize.org +
docs.arcprize.org; the exact request/response JSON is pending the live key (see `disclaimer`).

## Grid / frame
- Grid: **max 64×64** cells.
- Cell value: **integer 0–15** (color/state).
- Origin `(0,0)` top-left; coordinates `(x, y)`.
- Per turn: **1–N frames** of JSON (state + metadata). N frames = an animation/sequence from one
  action.

## Actions (7)
| action    | params        | meaning                                                      |
|-----------|---------------|-------------------------------------------------------------|
| ACTION1   | none          | simple, game-dependent (e.g. move/select/jump/rotate/fire)  |
| ACTION2   | none          | simple, game-dependent                                      |
| ACTION3   | none          | simple, game-dependent                                      |
| ACTION4   | none          | simple, game-dependent                                      |
| ACTION5   | none          | simple, game-dependent                                      |
| ACTION6   | X, Y (0–63)   | coordinate command — click / place at a cell                |
| ACTION7   | none          | undo (games that support it)                                |
| RESET     | —             | new session / reset (`/game/reset`)                         |

Meaning of ACTION1–5 is hidden and per-game; the agent learns the action→effect map by trying.

## SDK
- Install: `uv add arc-agi` · `pip install arc-agi`
- Auth: `ARC_API_KEY` (env var or `.env`); anonymous key works, registered unlocks public games.
- Client: `arc_agi.Arcade()`
- Env: `arc.make(game_id, render_mode)` — `render_mode="terminal"` visualizes; omit for +2K FPS.
- Loop: `reset → step(action) → observe` (RL-classic).

## REST endpoints
- `/game/list` — metadata for all exposed games
- `/game/reset` — new session or reset
- `/scorecard/open` — start a scorecard (aggregates across plays)
- `/scorecard/close` — finalize/lock
- `/scorecard/retrieve` — read stats

## Known games (seen in docs)
- `ls20`, `ft09` — full list via `list-games` or arcprize.org/tasks.

## Partner templates
- Anthropic, LangChain, HuggingFace, AgentOps.

## Still UNKNOWN until the live key (do not assert — verify by connecting)
- Exact frame JSON field names (`frame`? `grid`? `state`? `score`? `guid`? `available_actions`?).
- The game-state enum (likely something like NOT_STARTED / NOT_FINISHED / WIN / GAME_OVER — NOT
  confirmed, background guess only).
- Exact request/response bodies, rate limits, and per-game action legends.
