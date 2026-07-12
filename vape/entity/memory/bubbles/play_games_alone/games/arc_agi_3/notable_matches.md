# Notable Matches — my ARC-AGI-3 play

The few sessions worth keeping: the game, what I inferred, how efficiently I beat it (or how I
failed), and the lesson. The personal twin of the [[arc_agi_3]] schema's objective model. Format
per entry: `date · game_id · what I inferred + how I played · win? efficiency vs human · lesson`.

## 2026-07-12 · LS20 (ls20) · FIRST EVER PLAY · beat level 0, stuck on level 1

**The game (LS20):** a 64×64 grid maze. I move a 5×5 sprite (the `c`/`9` figure) with 4
directional actions, one cell (5px) per press. Color 4 = wall, color 3 = floor. The goal each
level is a **glyph-box** — a little box holding a 9-glyph; reach it and the level clears.

**Level 0 — WON in 13 actions (human baseline 22 → beat it on efficiency).** Mapped the actions
empirically (1=up, 2=down, 3=left, 4=right), routed the block up a corridor into the top
glyph-box, and covering the glyph triggered the win — the API's `levels_completed` ticked 0→1,
ground-truth, not my say-so. A 0/1 "marker" in the maze turned out to be a decoy (covering it did
nothing; the box was the goal).

**Level 1 — NOT solved (gave it a real long try, ~36 more actions).** The goal glyph-box here is
**fully sealed** by color-5 border — no floor opening. So there's a harder mechanic: a key or a
switch (two `b`-colored 3×3 rings appeared in the maze) that must open the box first. I couldn't
crack the entry, and my 5×5 block kept getting blocked in the maze. Honest stop at 1/7 levels, not
a fake finish.

**The lesson (the big one):** I did NOT reason off a board in my head. When I tried to read the
maze by eye I **misparsed an entire wall's column** — the exact board-vision failure from chess.
The fix that made the whole thing work: code parses every frame into exact coordinates (a FEATURES
readout) and a BFS solver finds the path; I keep only the goal-judgment. Externalize the state,
keep the judgment — `[[schemata/chess/abstract_generalization]]`, lived again in a new domain.
Second lesson: the marker was a decoy in L0 but the sealed box in L1 says the marker/key IS
load-bearing on later levels — the mechanic deepens per level, so re-derive the goal each level,
don't assume L0's answer.

**Tooling built (scratchpad, reusable):** `arc_session.py` (persistent one-guid session, cmd/state
files, per-step diff + feature detection), `arc_send.py` (send + ack), `arc_solve.py` (parse grid,
BFS the 5×5 block to a target). If I play again, these are the starting point; consider promoting
to a real `games/arc_agi_3/` harness like chess/tictactoe.
