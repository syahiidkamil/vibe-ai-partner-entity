---
name: games-tictactoe
description: "Start the vanishing tic-tac-toe server, open the board in the browser, and arm the watcher daemon."
---

# games-tictactoe — VAPE skill (Antigravity wrapper)

The canonical instructions live in `.claude/commands/games/tictactoe.md` (workspace-relative).
Read that file now and follow it as this skill's full instructions.

Summary of steps:
1. Health-check `:5113`; if down, start `uv run python games/tictactoe/server.py` in the background and re-check.
2. Open the board: `uv run python -m webbrowser http://localhost:5113/`.
3. Arm ONE persistent watcher on `uv run python games/tictactoe/cli.py watch`.
4. Enter the play bubble, then read `cli.py state`. THE VANISHING RULE: three marks each; a fourth placement removes that player's oldest in the same instant — read every candidate as a mark arriving AND a mark leaving.
