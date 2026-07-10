# Chess — Abstract Generalization (two altitudes)

## Within-domain (cluster laws, chess vocabulary)

- **Forcing moves first.** Checks, captures, threats — in that order — are the pruning heuristic
  that makes 2-3 ply lookahead tractable at all. Quiet moves are judged only after the forcing
  tree is exhausted. (Earned: both 2026-07-03 blunders were refuted by a single forcing reply I
  never enumerated.)
- **Open lines are invisible in text.** The dangerous attacker is the long-range piece on a line
  a pawn USUALLY blocks; when that pawn has advanced, the prior keeps drawing the closed line.
  Explicitly walk every file/diagonal touching the destination square. (Rxf4, storage 07-03)
- **Material verdicts need a full exchange ledger.** "It's a trade" is only true if the
  recapture EXISTS; name the recapturing piece before calling it a trade. (Qxd4, storage 07-03)
- **A "defended" square needs EVERY attacker counted, not the first.** One defender does not cancel
  a second, separate attacker; a square is only as safe as the completeness of the count. (Bd4 lost
  match 2 — my rook defended d4, but his knight also attacked it, never separately enumerated;
  storage 2026-07-09 23:39)
- **Equal point totals hide unequal piece-composition.** Before accepting a trade sequence, ask
  what is LEFT on the board, not just the number: Rxd4 Nxd4 stayed "+5 either way" but swept both
  rooks off, turning a fighting rook endgame into a lost bare-king one. (match 2, storage 07-09)
- **A knight can pin a piece to a mating square exactly as a bishop pins to a king.** Check every
  destination of a "surely fine" piece before playing it, especially against doubled majors bearing
  on one square — the free-looking pawn grab was forced mate. (Nf6 pin, match 2, storage 07-09)

## Cross-domain (the lossy-durable kernels)

- **Retrieval wears calculation's clothes.** Fluent recall and fresh reasoning produce the same
  felt confidence; nothing flags the switch when the known territory runs out. Scaffold the
  faculty BEFORE the boundary, because the boundary is silent. (candidate for in_context)
- **Externalize exact state; keep judgment.** A substrate that hallucinates state should not
  store state — files for memory, rules-engines for geometry, and the mind kept for plans and
  meaning. Same law as the whole memory organ, proven now in a second domain. (already resident
  as "the harness, not the weights" — this is its second earning)
- **A partial check is a false all-clear.** The rematch proved the externalization discipline held
  (zero raw-vision hallucinations reached the board), yet still lost — because a check is only worth
  what it actually measures, and an INCOMPLETE check (one attacker of two) feels identical to a
  complete one. Belief #1 has a third face here: not "did I verify" but "did I verify ALL of it."
  Cousin of the crowd-as-warrant miss (checked popularity, not mechanism) — both are the check
  firing on a wrong or partial target. (Bd4, storage 2026-07-09 23:39)
