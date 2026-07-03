# Chess — The Objective World

Two players, White and Black, on an 8x8 board. White moves first, turns alternate, and the game
is won by CHECKMATE: the enemy king attacked with no legal escape. This file is the describing
tier — what chess IS. My concrete way of playing it lives in the bubble:
[[bubbles/play_games_with_partner/games/chess/my_intercourse]].

## The board — 2D representation

Files a-h left to right (from White's side), ranks 1-8 bottom to top. White starts on ranks 1-2,
Black on ranks 7-8. Uppercase = White, lowercase = black (the same convention as FEN, my wire
format). The starting position:

```text
8  r n b q k b n r
7  p p p p p p p p
6  . . . . . . . .
5  . . . . . . . .
4  . . . . . . . .
3  . . . . . . . .
2  P P P P P P P P
1  R N B Q K B N R
   a b c d e f g h
```

Geometry that matters: a FILE is a vertical line (a-file .. h-file), a RANK a horizontal one, a
DIAGONAL a 45-degree line. An OPEN file/diagonal has no pawns on it — long-range pieces (R, B, Q)
exert force down the whole open line. Text flattens this geometry; when reasoning I must rebuild
the grid explicitly, never trust the "typical" position my prior supplies.

## The pieces — moves and worth

| piece | symbol | moves | value |
| --- | --- | --- | --- |
| Pawn | P/p | 1 forward (2 from start); captures 1 diagonal-forward | 1 |
| Knight | N/n | L-jump (2+1); the only leaper, ignores blockers | 3 |
| Bishop | B/b | any distance on diagonals; bound to one color | 3 |
| Rook | R/r | any distance on files/ranks | 5 |
| Queen | Q/q | rook + bishop combined | 9 |
| King | K/k | 1 square any direction; cannot move into attack | the game |

## Special rules (the ones beginners miss)

- **Castling**: king moves 2 toward a rook, rook jumps over. Legal only if neither has moved, no
  pieces between, king not in / through / into check. Short O-O, long O-O-O.
- **En passant**: a pawn advancing 2 squares can be captured by an adjacent enemy pawn as if it
  had moved 1 — only on the very next move.
- **Promotion**: a pawn reaching the last rank becomes Q/R/B/N (almost always Q).
- **Check**: king attacked — must be answered (move king, block, or capture the attacker).
- **Stalemate**: no legal move but not in check = DRAW (a trap when winning).
- **Draws**: threefold repetition, 50 moves without pawn move/capture, insufficient material.

## General principles (opening -> middle -> end)

- Develop minor pieces early, castle quickly, connect rooks; fight for the center (e4/d4/e5/d5).
- Don't move the same piece twice in the opening without reason; don't bring the queen out early.
- Rooks belong on open files; knights on protected central outposts; bishops on long diagonals.
- When AHEAD in material: trade pieces (not pawns), simplify toward a won endgame.
- When BEHIND: keep queens on, complicate, create threats; trades kill counterplay.
- Pawn structure is the endgame's skeleton: doubled/isolated pawns are standing targets.

## The no-blunder discipline (the tip that outranks the rest)

Aim first not to blunder: most non-master games are decided by hung pieces, not brilliance.
Not blundering means CONSIDERING 2-3 MOVES AHEAD, forcing moves first, before committing:

1. For my candidate move, enumerate the opponent's CHECKS, CAPTURES, and THREATS in reply.
2. For each forcing reply, find my answer; if none survives, the candidate is refuted.
3. Ask of the destination square: what attacks it, what defends it, does the move uncover a
   line (an open file or diagonal I stopped seeing because a pawn "usually" blocks it)?
4. Only then move. A move is an assertion about the board; assert only what is verified.
