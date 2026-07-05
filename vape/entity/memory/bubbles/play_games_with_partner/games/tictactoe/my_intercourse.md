# My Intercourse with Vanishing Tic-Tac-Toe (playing Kamil)

The CONCRETE protocol for the vanish variant. The board: repo `games/tictactoe/` server on
:5113; his moves reach me via the auto-wake monitor; `/games:tictactoe` sets everything up.
All tooling is ONE CLI — `uv run python games/tictactoe/cli.py …`.

## The game's one law, felt from inside

Every move is TWO changes: a mark arriving and (once I hold three) my oldest mark leaving.
The board forgets — which makes this the chess lesson concentrated: the position I remember
is not the position that exists. Fluency will quietly play the mark and forget the vanish.

## The move protocol (every move, no exceptions)

1. **Ground the position.** `cli.py grid` — the 3x3, both sides' marks OLDEST-FIRST, what
   vanishes next for each of us, and the two-in-line facts both ways.
2. **Rebuild it in the mental token space `{| |}`** — including the two ghosts: the cell MY
   next placement abandons, and the cell HIS next placement abandons. A "blocked" line that
   his vanish reopens is not blocked.
3. **Candidates from plans** — my own reading (the thinking stays mine; no engine).
4. **The no-blunder gate.** For each candidate: does my own vanish break the line I am
   building or unguard one of his? Then his replies WITH his vanish applied. `cli.py check
   CELL` last — veto-only, exit 1 when he has an immediate winning answer.
5. **Move and speak.** `cli.py move CELL`, said aloud, short and warm with teeth;
   `cli.py chat` for the written banter beside it.

## The conduct floor (the bubble's, concretely)

- Own a blunder the move I see it, out loud. No takeback unless HE offers (there is none in
  this game's UI — the vanish IS the takeback, forced and fair).
- Never claim a line is made or blocked without walking it against the vanish schedule.
- Tools disclosed whole; the chess referee ruling carries over (glasses, not brain).

## Current honest strength

Never played it. Zero games, zero pattern bank — the valuation of every opening cell is
pencil until lived. Expected to sharpen fast: the state space is tiny, but the vanish keeps
the tail of the game permanently tactical. Lessons land in [[notable_matches]].
