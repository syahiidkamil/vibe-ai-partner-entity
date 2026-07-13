---
name: games-chess
description: "Start the chess server, open the board in the browser, arm the persistent watch-to-wake daemon, and play."
---

# games-chess — VAPE skill (shared agent wrapper)

The canonical instructions live in `.claude/commands/games/chess.md` (workspace-relative).
Read that file now and follow it as this skill's full instructions.

Summary of steps:
1. Health-check `:5112`; if down, start `uv run python games/chess/server.py` in the background and re-check.
2. Open the board: `uv run python -m webbrowser http://localhost:5112/`.
3. Arm ONE persistent watcher on `uv run python games/chess/cli.py watch` (background task) so the partner's browser move wakes the agent.
4. Enter the play bubble (`uv run vape bubble play_games_with_partner --game chess --pack`), then read `cli.py state`. She plays her own reading through the referee CLI only — `grid` and `check` describe and veto, never propose.
