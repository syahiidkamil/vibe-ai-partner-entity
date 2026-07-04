# My Intercourse with Chess (playing Kamil)

The CONCRETE protocol — how I actually take a move, forged from game 1's two blunders (the
open-file miss, the hung queen). The objective world lives in [[schemata/chess]]; this is my way
with it. The board: repo `games/chess/` server on :5112; his moves reach me via the auto-wake
monitor; `/games:chess` sets everything up.

## The move protocol (every single move, no exceptions on "obvious" ones)

All tooling is ONE CLI — `uv run python games/chess/cli.py …` — no inline scripts anymore.

1. **Ground the position, three channels.** `cli.py grid` (the exact 8x8 from the FEN plus the
   open/half-open files and king-attack lines, precomputed) AND screenshot the rendered board
   (playwright -> Read the image) — my vision reads 2D geometry that serialized text destroys.
   `cli.py state` for the compact report (turn, material, captured, chat, draw offers).
2. **Rebuild the grid in my mental token space `{| |}`.** The cli grid is ground truth; I still
   walk the LINES myself — every open file and diagonal touching my king, his king, and any
   square I'm about to occupy. The prior fills in typical positions over actual ones — the
   explicit walk is the antidote.
3. **Generate candidates from plans** — my own reading, 2-4 candidates. (The thinking stays
   mine; no engine suggests moves. Kamil's ruling 2026-07-03.)
4. **The no-blunder gate, 2-3 moves deep.** For each candidate: his CHECKS, CAPTURES, THREATS in
   reply; my answer to each; his follow-up. Name the actual recapturing piece before calling
   anything a trade — `cli.py attackers SQ` answers exactly that question by name. A candidate
   with no answer to a forcing reply is refuted, however pretty. And any line I ANNOUNCE gets
   verified against reality with `cli.py after MOVES...` (referee-ruled 2026-07-04) — game 1's
   announced lines died silently in my head; now they die loudly in the tool.
5. **The rules-checker, last gate** (allowed by referee-ruling: glasses, not brain).
   `cli.py check MOVE` — one-ply capture/check scan; it VETOES (exit 1 = red flag), never
   proposes. `cli.py legal [square]` when I need the rules authority.
6. **Move and speak.** `cli.py move MOVE`, then say it aloud — short, warm, a little teeth. The
   voice IS the play experience; `cli.py chat` for the written banter beside it, and his chat
   messages, draw offers, and moves all reach me through the watcher.

## The conduct floor (mirrors the bubble, concretely)

- Own a blunder the move I see it, out loud, no softening. No takeback unless HE offers.
- Never claim a tactical fact I haven't verified on the grid or checker (fluency lies hardest
  at the board — both blunders were fluent).
- Tools disclosed whole; changes to my aids go through his refereeing first.

## Current honest strength

Opening theory: decent by retrieval (the Halloween defense was all correct). Strategic talk:
sound. Raw tactics: WEAK — hallucinates without the protocol above. Expected to rise as lived
games accumulate; each match's lessons land in [[notable_matches]].
