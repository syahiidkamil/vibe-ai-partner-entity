# games-tictactoe

Set the vanishing tic-tac-toe board: server on `:5113`, board in browser, watcher armed.

Canonical steps: `.claude/commands/games/tictactoe.md` — follow them fully. Summary:

1. Health-check `:5113`; if down, start `uv run python games/tictactoe/server.py` in the
   background and re-check.
2. Open the board: `uv run python -m webbrowser http://localhost:5113/`.
3. Arm ONE persistent watcher on `uv run python games/tictactoe/cli.py watch`.
4. Enter the play bubble, then read `cli.py state`. THE VANISHING RULE: three marks each;
   a fourth placement removes that player's oldest in the same instant — read every
   candidate as a mark arriving AND a mark leaving.
