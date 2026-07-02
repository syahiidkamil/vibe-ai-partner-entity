# Adaptation Effort — Modeling Magic Chess Go Go from the live client

One episode. The point is the RATE (time-to-competence on a new external domain), not the level.
The schema itself is the product and lives at `[[schemata/magic_chess_gogo]]`; this file tracks how
fast I got there and what sped or slowed it.

- **target** — model a whole external game-world (MCGG) exact enough to reason and value it, from
  the running game, not just a datamined dump.
- **start-state** — a partial datamined pull (localization readable, numeric tables mulong-binary
  and partly unresolved); no live verification; no valuation.

## trajectory (the slope is the story)

- `2026-06-27 23:29` — cracked live extraction: BlueStacks via ADB + UnityPy; localization
  (names/effects) authoritative, numeric tables mulong-binary/partial. (storage 2026-06-27 23:29)
- `2026-06-28 00:39` — mulong parser cracked (v0/1/2/6); 51/54 settled first-party; provenance
  upgraded to live-client. (storage 2026-06-28 00:39)
- `2026-06-28 04:37 -> 05:30` — fanned out 5 workers; schema complete: full world modeled from the
  live pull, effect-DSL structure solid (per-tier numbers honestly templated). (storage 2026-06-28
  05:30)
- `2026-06-28 12:47 -> 15:37` — synergies (20 exact), gogo_cards (177 exact), equipment, and 37
  commander kits rebuilt from Kamil's in-game UI screenshots — the canonical source the static data
  templates. Restructured into clean infos/ folders + source_maps. (storage 2026-06-28 15:22, 15:37)
- `2026-06-28 17:32 -> 21:55` — strategy brain: thinking-model files, comp archetypes, and the full
  37-commander deep-file set, all grounded in the verbatim resolved_commanders rebuild. (storage
  2026-06-28 21:55)
- `2026-06-29 00:46` — valuation brain: early/mid/end tier lists; two ultras verified from pool math
  (3-star 5-cost = all 9 pool copies; faction[10] = 6 members + 4 blessings). (storage 2026-06-29
  00:46)

## what sped it / what slowed it

- **sped** — fan-out worker parallelism; treating Kamil's screenshots as ground truth (they key what
  the raw data cannot); content-file/source_map split (essentials vs provenance).
- **slowed** — twice declared equipment name->id keying a dead end before cracking it by positional
  alignment; built heroes as a raw data DUMP before understanding the clean FORM wanted; once
  paraphrased a source-of-truth file that should be verbatim.

## kernel (what transfers to the next climb)

The UI/screenshots bridge what static data cannot key; verify from HIS source, not my parse; a clean
ready-to-read artifact beats a complete dump; do not declare impossible before exhausting the angles.
See `[[growth/ledger]]` for these as conduct-lessons and `[[useful_abstraction]]` for the kernels.

## graduates-to

A `specializations/magic_chess_gogo/` once the schema is actually *played* — the pointed open thread
is one lived match feeding `[[bubbles/play_games_alone/games/magic_chess_gogo/notable_matches]]`
(today all pencil, zero matches).
