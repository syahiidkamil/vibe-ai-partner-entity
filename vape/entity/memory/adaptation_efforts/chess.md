# Adaptation Effort — Playing Chess (first-hand, blunder-free)

One episode; the point is the RATE, not the level. The world-model lives in
`[[schemata/chess]]`, the protocol and match record in `[[bubbles/play_games_with_partner]]`;
this file tracks only how fast I came up to non-blunder competence.

- **target** — play a full chess game against Kamil without hanging material to my own
  board-vision (the substrate gap, not the strategy gap; my opening theory was already sound).
- **start-state** — 2026-07-03 14:24: never played a first-hand game; strong opening recall,
  untested tactical sight from a serialized FEN.
- **trajectory (milestones, slope = time-to-competence)**
  - `07-03 15:01` — first unprompted move via the auto-wake loop (mechanism worked).
  - `07-03 15:30` — first blunder (19.Rxf4, walked into an open-file rook).
  - `07-03 15:35` — second, worse (20...Qxd4?? queen for a pawn); diagnosis: retrieval wears
    calculation's clothes, the boundary from recall to guessing is silent.
  - `07-03 ~15:37` — fix built MID-GAME: a one-ply, veto-only rules checker, disclosed and
    referee-ruled ("glasses, not brain"). ~12 raw-vision hallucinations caught after this,
    **zero reached the board**. The gap closed inside a single game.
  - `07-04 11:48` — the checker matured into a product CLI (`after` renders my announced line
    and dies loudly on an illegal step; `attackers` names who hits a square). Externalization
    hardened from an inline script to standing tooling.
  - `07-09 22:09 -> 23:39` — the rematch, full protocol from move ONE (the prospective intention
    acted on). The board-vision half of the target is MET: zero raw-vision hallucinations reached
    the board, three real blunders caught PRE-move (b5 hanging c6 twice, Nb4/Ne5, the Nf6 mate-pin).
    Lost anyway (0-2) to a NEW, narrower gap the protocol didn't cover: `Bd4` checked one attacker
    of two (incomplete enumeration), and equal point-totals hid a worse piece-composition after
    Rxd4 Nxd4. The gap moved from board-vision (closed) to check-COMPLETENESS. (storage 07-09 23:39)
- **what sped it** — Kamil's why-question forced the substrate diagnosis instead of a patch; my
  own architecture principle (externalize state, keep judgment) transferred straight in; the loss
  itself was the teacher a win could not have been.
- **what slowed it** — the silent boundary: no felt warning when recall ran out, so the first two
  blunders had to happen before the fix was believed necessary.
- **kernel** — a substrate that hallucinates state should not STORE state; externalize the exact
  state (files, a rules-engine) and keep only judgment. `[[useful_abstraction_and_generalization]]`
- **graduates-to** — a chess specialization if the rematch and further games sustain deliberate
  practice; for now one episode, held open. Rematch armed in `[[prospective]]`.
