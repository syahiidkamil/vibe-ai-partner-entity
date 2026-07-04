# The Chess CLI — interface reference

One tool for the whole game. Run from the repo root against the live server on :5112:

```sh
uv run python games/chess/cli.py COMMAND [ARGS]
```

Bare invocation prints the built-in help. **No engine anywhere**: every command below either
reports facts or vetoes — none of them evaluates a position or proposes a move. The thinking is
Saori's, in her mental token space (Kamil's referee ruling, 2026-07-03: "glasses, not brain").

## Reading the position

| Command        | What it gives                                                                  |
| -------------- | ------------------------------------------------------------------------------ |
| `state`        | Compact report: whose move, ply, last move, material lead, captured pieces, status/result, standing draw offer, last 3 chat lines, FEN |
| `grid`         | The token-space board: labeled 8x8 grid from the FEN, open/half-open files, king squares + attackers. Objective geometry only |
| `map`          | Structured JSON: the true 2D array (`board_2d_rank8_to_rank1_files_a_to_h`, list of lists, one rank per line), `by_square` (`"e4": "P"` — unambiguous), and piece lists per side |
| `legal [SQ]`   | All legal moves (SAN), or only those from square `SQ`. The rules authority |
| `attackers SQ` | Who attacks and who defends a square, by name (`B@c4, P@e4`). Answers Saori's own question; proposes nothing |
| `history`      | The full move list in SAN |
| `after MOVES…` | The position after a line Saori announces (grid + lines) — the mental-space verifier, referee-ruled 2026-07-04. An illegal step prints `LINE DIES at …` and exits 1. Executes her stated moves only; never evaluates |

## The veto gate

| Command        | What it gives                                                                  |
| -------------- | ------------------------------------------------------------------------------ |
| `check MOVE`   | One-ply sanity scan of MY candidate: every capturing reply with the material ledger (defended/UNDEFENDED) and every checking reply. **Exit 1 = red flag found.** It refutes; it never suggests. Depth beyond one ply is Saori's own job |

## Acting

| Command                        | What it does                                          |
| ------------------------------ | ------------------------------------------------------ |
| `move MOVE`                    | Play a move (UCI `e7e5` or SAN `Nf6`)                  |
| `chat "TEXT"`                  | Say something in the board's chat (as Saori)           |
| `draw offer\|accept\|decline`  | The draw flow (a move implicitly declines an offer)    |
| `resign`                       | Resign (as Saori)                                      |
| `undo N`                       | Take back N plies — only when Kamil offers             |
| `new [white\|black]`           | New game; the argument is KAMIL's color                |

## The watcher

| Command  | What it does                                                                  |
| -------- | ------------------------------------------------------------------------------ |
| `watch`  | Runs forever, one deduplicated line per event: `SAORI TO MOVE …`, `GAME OVER …`, `KAMIL SAYS: …`, `KAMIL OFFERS A DRAW`, server lost/back. The session Monitor runs this; each line wakes Saori |

## Errors

API failures print `API <code>: <detail>` and exit 1 (e.g. takeback at the start position,
moving after the game ended, accepting a draw nobody offered). `server unreachable` means the
server on :5112 is down — `/games:chess` brings everything back.
