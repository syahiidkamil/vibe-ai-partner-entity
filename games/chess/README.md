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

## The CLI (Saori's side — the one tool for the whole game)

```sh
uv run python games/chess/cli.py state           # compact report: turn, material, chat
uv run python games/chess/cli.py grid            # token-space grid + open files/king lines
uv run python games/chess/cli.py legal [e7]      # legal moves (rules authority)
uv run python games/chess/cli.py check Nf6       # veto-only sanity scan (referee-ruled OK)
uv run python games/chess/cli.py move e7e5       # play (UCI or SAN)
uv run python games/chess/cli.py chat "hi K"     # in-game chat
uv run python games/chess/cli.py draw offer      # or accept / decline
uv run python games/chess/cli.py resign
uv run python games/chess/cli.py watch           # the auto-wake event stream (Monitor)
```

The checker and grid describe and veto only — they never propose a move; the
thinking stays Saori's (Kamil's referee ruling, 2026-07-03).

## The raw API (what the CLI and the browser both speak)

```sh
curl -s localhost:5112/board.txt                 # look at the board (ASCII)
curl -s localhost:5112/state                     # fen, legal, history, captured,
                                                 # chat, draw_offer, end_reason
curl -s -X POST localhost:5112/move -H 'Content-Type: application/json' \
     -d '{"move":"e7e5"}'                        # UCI or SAN both accepted
curl -s -X POST localhost:5112/new  -H 'Content-Type: application/json' \
     -d '{"kamil":"white"}'                      # new game (or "black")
curl -s -X POST localhost:5112/undo -H 'Content-Type: application/json' \
     -d '{"plies":1}'                            # friendly takeback (400 at start)
# plus: /resign {who} · /draw {who, action} · /chat {who, text}
```

## Record

Every move autosaves the game's PGN under `matches/` (one file per game,
named by start time), so nothing is lost to a crash and finished games feed
`notable_matches` entries in Saori's memory — the bubble gets born from the
first real game, not scaffolded ahead of it.
