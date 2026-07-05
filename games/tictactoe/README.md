# Vanishing Tic-Tac-Toe — Kamil vs Saori, on localhost

A tiny FastAPI server holds one live game; a browser page and a CLI both talk to it over
HTTP. Kamil plays in the browser; Saori plays through the API with her own reading of the
board — no engine anywhere.

## The vanishing rule

Each player keeps at most **3 marks** on the board. Placing a 4th removes that player's
**oldest** mark in the same instant. Three surviving marks in a row win. The board can
never fill, so there is no stalemate: a game ends by a line, a resignation, or an agreed
draw. Both sides' oldest marks show faded on the board — what is about to be forgotten is
part of the position.

## Run

```
uv run python games/tictactoe/server.py
```

Then open http://localhost:5113/ — Kamil defaults to X (X always moves first).

## The pieces

- `server.py` — state, rules, autosaved match records under `matches/`
- `index.html` — Kamil's board: click to move, chat, draw/resign, the fade preview
- `cli.py` — Saori's whole interaction: `state · grid · legal · check · move · chat ·
  draw · resign · new · watch`. `check` is veto-only (it refutes, never suggests);
  `watch` is the auto-wake stream her session Monitor runs.

Cells are `a1..c3`, rank 1 at the bottom, chess-style. In the move list, `c3 -a1` means
"placed on c3, the old a1 mark vanished."
