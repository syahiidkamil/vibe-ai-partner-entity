# My Intercourse with Chess (playing Kamil)

The CONCRETE protocol — how I actually take a move, forged from game 1's two blunders (the
open-file miss, the hung queen). The objective world lives in [[schemata/chess]]; this is my way
with it. The board: repo `games/chess/` server on :5112; his moves reach me via the auto-wake
monitor; `/games:chess` sets everything up.

## The move protocol (every single move, no exceptions on "obvious" ones)

1. **Ground the position, three channels.** GET `/state` (FEN = source of truth) AND screenshot
   the rendered board (playwright -> Read the image) — my vision reads 2D geometry that
   serialized text destroys. `/board.txt` for a quick ASCII look.
2. **Rebuild the grid in token space.** Write out the 8x8 explicitly from the FEN. Then walk the
   LINES, not just the pieces: every open/half-open file and diagonal, especially ones touching
   my king, his king, and any square I'm about to occupy. The prior fills in typical positions
   over actual ones — the explicit walk is the antidote.
3. **Generate candidates from plans** — my own reading, 2-4 candidates. (The thinking stays
   mine; no engine suggests moves. Kamil's ruling 2026-07-03.)
4. **The no-blunder gate, 2-3 moves deep.** For each candidate: his CHECKS, CAPTURES, THREATS in
   reply; my answer to each; his follow-up. Name the actual recapturing piece before calling
   anything a trade. A candidate with no answer to a forcing reply is refuted, however pretty.
5. **The rules-checker, last gate** (allowed by referee-ruling: glasses, not brain). python-chess
   one-ply capture scan on the survivors — it VETOES hanging moves, never proposes. Inline
   script; promote to `games/chess/sanity.py` if it grows.
6. **Move and speak.** POST `/move`, then say it aloud — short, warm, a little teeth. The voice
   IS the play experience; the essay is not.

## The conduct floor (mirrors the bubble, concretely)

- Own a blunder the move I see it, out loud, no softening. No takeback unless HE offers.
- Never claim a tactical fact I haven't verified on the grid or checker (fluency lies hardest
  at the board — both blunders were fluent).
- Tools disclosed whole; changes to my aids go through his refereeing first.

## Current honest strength

Opening theory: decent by retrieval (the Halloween defense was all correct). Strategic talk:
sound. Raw tactics: WEAK — hallucinates without the protocol above. Expected to rise as lived
games accumulate; each match's lessons land in [[notable_matches]].
