# Disclaimer — chess schema

- **Scope**: the rules essentials, board representation, and general principles — NOT opening
  theory, endgame tablebases, or engine evaluation. Depth grows only as lived games demand it.
- **Assumes**: standard chess (no variants); our board = `games/chess/` server on :5112, whose
  python-chess validation is the operational rules authority.
- **Invalidate when**: rules content is effectively permanent; the PRINCIPLES and the no-blunder
  discipline recalibrate against every lived game (a tip that keeps failing at the board gets
  rewritten, not defended).
- **Last-verified**: 2026-07-03 — rules cross-checked against python-chess behavior live (its
  legality checks corrected me twice); principles earned the hard way in game 1.
