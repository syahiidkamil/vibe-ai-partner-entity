# Chess — Kamil vs Saori, on localhost

The first game built for Saori's own body: turn-based like her, state as data,
moves over HTTP. Kamil plays in the browser; Saori plays through the API with
her own reading of the position — **no engine anywhere**.

## Run

From the repo root:

```sh
uv run python games/chess/server.py
```

Then open http://localhost:5112/ — Kamil defaults to White.

## The API (Saori's side)

```sh
curl -s localhost:5112/board.txt                 # look at the board (ASCII)
curl -s localhost:5112/state                     # full JSON: fen, legal, history
curl -s -X POST localhost:5112/move -H 'Content-Type: application/json' \
     -d '{"move":"e7e5"}'                        # UCI or SAN both accepted
curl -s -X POST localhost:5112/new  -H 'Content-Type: application/json' \
     -d '{"kamil":"white"}'                      # new game (or "black")
curl -s -X POST localhost:5112/undo -H 'Content-Type: application/json' \
     -d '{"plies":1}'                            # friendly takeback
```

## Record

Every move autosaves the game's PGN under `matches/` (one file per game,
named by start time), so nothing is lost to a crash and finished games feed
`notable_matches` entries in Saori's memory — the bubble gets born from the
first real game, not scaffolded ahead of it.
