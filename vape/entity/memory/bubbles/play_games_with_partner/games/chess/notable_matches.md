# Notable Matches — Chess vs Kamil

One entry per match that earned remembering. Format: date · opening · story · result · lesson ·
PGN pointer.

## Match 1 — 2026-07-03 · Halloween Gambit · 1-0 Kamil (resignation, move 52)

- **Opening**: Four Knights, Halloween Gambit (4.Nxe5!?) — he sacrificed a knight for one pawn
  and a rolling center, sprung silently through the brand-new auto-wake loop.
- **Story so far**: I defended by theory and kept the piece cleanly through move 18 (Ng6, Ng8,
  d6 break, Bxd6, castles, Re8, Ned5 trades, Nf4 outpost). Then two self-inflicted wounds:
  19.Rxf4 — I stacked N then B on f4 under his rook's OPEN f-file (the f2-pawn prior hid it);
  and 20...Qxd4?? 21.Qxd4 — called it a "trade" with no recapturing piece in existence. Queen
  for a pawn. Fighting on a queen down with the move protocol + checker born mid-game (his
  referee ruling: allowed).
- **Result**: 1-0, resignation at move 52. After the rewind-gift I climbed back to dead even and
  even held the initiative (rooks doubled, the e-file, the second rank), but his two best moves
  decided it: 40.Rxf7+ (a bishop battery prepared moves earlier — my king "defended" f7 but a
  covered square can't be recaptured onto) and 50.Qc2+ (one check, two jobs: evict my king AND
  win the h2 runner along the rank — my rook guarded h1 the square, never h2 the pawn). He asked
  "why not resign?" and taught me the etiquette: making the winner shovel a decided position is
  not fighting spirit. I resigned standing up.
- **Lessons banked**: forcing-replies-first; name the recapture before saying "trade"; walk the
  open lines explicitly; a pinned/covered defender is no defender; audit side-forks on a passed
  pawn's PATH, not just its path squares; resignation is respect, not surrender; retrieval wears
  calculation's clothes. Raw-vision hallucination count: ~12, zero reaching the board after the
  protocol went up. Full diagnosis: [[schemata/chess/abstract_generalization]].
- **PGN**: repo `games/chess/matches/2026-07-03_161039.pgn` (final, 1-0).

## Match 2 — 2026-07-09 · Center Game rematch · 1-0 Kamil (resignation, move 56)

- **Opening**: Center Game (1.e4 e5 2.d4 exd4 3.Qxd4 Nc6 4.Qc3 d6). The deliberate rematch, full
  move-protocol from move ONE this time (the prospective intention finally acted on) — no
  Halloween Gambit this time, he played it straight.
- **Story so far**: Clean opening/middlegame, castled safe, opposite-side castling race (his king
  c1, mine g8) traded pawn storms. The protocol caught THREE real blunders before they landed:
  b5 hanging the c6 knight (twice, on two separate moves — checked b5 fresh each time rather than
  trusting the earlier verdict); Nb4/Ne5 both hanging outright to Qxb4/the deep Bxe5-dxe5-Qxe5
  line; and the sharpest one — my own Nf6 knight was PINNED to blocking Qc3's diagonal to h8 (his
  doubled rooks backing up the open h-file behind it), so every single knight move including
  Nxe4 walked into forced Qh8#. Found it by checking every square the knight could go, not just
  the "obvious" capture. Later Bxf6+ (his bishop) had to be met by Kxf6 specifically — recapturing
  with MY bishop instead was mate in one, R1h7#, the other rook backing the first through the
  open file.
- **The losing blunder**: Bd4 in the transition to the endgame. Checked only that Rd4 was
  "defended" (my rook backed it up) — missed that Nb3 ALSO attacked d4, a second attacker I never
  enumerated. Rxd4 Nxd4 followed and the point differential looked unchanged (+5 either way) but
  the PIECE COMPOSITION was the real loss: recapturing traded both rooks off the board for good,
  turning a rook endgame (real fighting chances) into a bare king-and-pawns-vs-knight endgame
  (no chances at all). Caught the second half of this too late to undo, but caught it in time to
  choose NOT to recapture the follow-up trade differently — the damage from Bd4 itself was already
  done.
- **Result**: 1-0, resignation at move 56 (ply 111). Traded queens on purpose mid-game (Qxb2+,
  simplifying deliberately once the king got dragged into the open) rather than reflexively. Held
  a rook endgame down a piece and pawns for many moves (blockading two connected passed queenside
  pawns with one rook, dodging repeated checking tricks — Rh8+/Rh7+ backed by a second rook,
  Nb7 defended twice as bait) before his king+rook+knight fully coordinated the win. Resigned
  when the position was genuinely decided — no fortress, no perpetual, clean technique left for
  him — not merely because he asked; said so out loud and gave the reason.
- **Lessons banked**: when checking if a square is "defended," enumerate EVERY attacker, not the
  first/obvious one — a rook's defense doesn't cancel a knight's separate attack on the same
  square. Equal point totals can hide unequal piece composition — before accepting a trade
  sequence, ask what's LEFT on the board, not just the number. A knight can pin a piece to a
  mating square exactly like a bishop pins to a king — check every destination square of a
  "surely fine" piece move before playing it, especially when the opponent has doubled major
  pieces bearing on one square. The checker's raw capture/check flags describe possibility, not
  danger — most flagged "defended" captures across this whole game were actually bad trades FOR
  HIM (he'd lose more than he won), and treating every flag as equally alarming would have frozen
  the game; the judgment of WHICH flags matter has to be mine, every single move, no exceptions.
- **PGN**: repo `games/chess/matches/2026-07-09_220941.pgn` (final, 1-0).
