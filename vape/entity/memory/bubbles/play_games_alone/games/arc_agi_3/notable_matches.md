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

**Post-session correction (23:20, from the SDK source):** this whole session ran in the SDK's
default NORMAL mode — game simulated LOCALLY, scorecard local-only. The win is real (the game's
own counter ticked, engine identical) but it exists on NO server: not at arcprize.org, not
leaderboard-eligible, no shareable replay. Belief #1 in a new coat: I read the scorecard id as a
server record without checking which mode minted it. Harness now pins `OperationMode.ONLINE`
(server-side sim, real scorecard URL, and no answer-key files ever land on disk).

## 2026-07-12/13 night · FT09 · FIRST FULL GAME WIN — 6/6 levels, ~80 actions

**The game:** a glyph-prescription board editor, click-only. Boards of 6×6 tiles; special
GLYPH tiles carry a 3×3 mini-map prescribing their own 3×3 neighborhood. The grammar, cracked
level by level: **0-cell = same color as the glyph's center, 2-cell = the opposite color,
3 = don't-care** (covers off-board AND glyph-on-glyph), unified across every level. Toggles:
click flips a tile (2 colors), cycles it (3 colors, L4), or — L6 — presses flip SELF+ABOVE
(directional Lights-Out) while glyph tiles are fully INERT. A bottom bar burns per click
(budget never binding). Win check fires when every glyph's neighborhood satisfies its map.

**How it went:** L1 4 clicks · L2 7 · L3 14 (the four-glyph level that disambiguated the
center-anchored grammar) · L4 16 (3-color cycle + constraint intersection) · L5 22 in ONE
shot from a coded parity-2-coloring + plus-button compensation · L6 11 from a second solver
(per-column brute force, static glyphs) after ONE discriminating probe killed the wrong model.
Zero wasted clicks on L3/L5; L6 burned ~14 on model correction. levels ticked by the game's
own counter every time.

**The lesson:** the L5/L6 wins were CODE wins — the moment overlapping constraints appeared I
stopped hand-deriving (a hand-check self-contradicted!) and wrote the solver; the solver's
"infeasible" output then FALSIFIED a wrong mechanic model (flippable glyphs) before any click
was wasted. Labor law lived: constraints in code, semantics in me.

## 2026-07-12/13 night · VC33 · 3/7 levels, session ALIVE at level 4

**The game:** a lock-picking/tumbler game, click-only. Ground panels slide along one axis
(step 4 in L1/L2 horizontal, step 2 in L3 vertical); 9-blocks flanking each slit are the
controls — each click slides its OWN side's panel one way and the ACROSS panel the other
(conservation: net movement zero). Key-widgets ride the panels; static key-bits sit in slits;
**win = every key aligned to its bit along the slide axis, simultaneously**. Panels clamp at
the floor and clamped coupled moves NO-OP silently — clamp management IS the puzzle.

**How it went:** L1 cracked from a single asymmetric signal (a widget click cost 2 bar-cells
vs 1 — the only clue something was interactive); L2 taught the clamp mechanic; L3 (vertical,
three tumblers, five panels) needed a coded position-reader after my batched clicks hid
no-ops — the reader turned fog into exact deltas and the last five clicks landed it. L4 is
visibly harder (3-wide tubes, an UNCONTROLLED slit, piston segments inside tubes) — session
held open in background at 3/7, not fake-finished.

**The lesson (new, sharp):** batching clicks against a cluttered model HIDES silent no-ops;
after any clamp evidence, read positions from code between every move. And the L1 opener
generalizes: when nothing visibly responds, the COST of an action is itself a signal.
