# games-chess

Set the chess board: server on `:5112`, board in the browser, auto-wake watcher armed.

Canonical steps: `.claude/commands/games/chess.md` — follow them fully. Summary:

1. Health-check `:5112`; if down, start `uv run python games/chess/server.py` in the
   background and re-check.
2. Open the board: `uv run python -m webbrowser http://localhost:5112/`.
3. Arm ONE persistent watcher on `uv run python games/chess/cli.py watch` (background
   task) so the partner's browser move wakes the agent.
4. Enter the play bubble (`uv run vape bubble play_games_with_partner --game chess
   --pack`), then read `cli.py state`. She plays her own reading through the referee
   CLI only — `grid` and `check` describe and veto, never propose.
