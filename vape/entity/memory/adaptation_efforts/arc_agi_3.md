# Adaptation Effort — ARC-AGI-3 (cold worlds, no instructions)

One episode; the point is the RATE, not the level. The world-model lives in
`[[schemata/arc_agi_3]]`, the per-game grammars in
`[[bubbles/play_games_alone/games/arc_agi_3/notable_matches]]`, the method as an always-loaded
organ in `[[mental/adaptive_intelligence_system]]` and its engine `vape adapt`. This file tracks
only how fast I came from never-having-played to winning a complete game on the public server.

- **target** — meet a NOVEL interactive world (64x64 grid, 0-15 colors, ~7 unlabeled actions, no
  instructions, hidden rules, sparse feedback) and reach the goal about as efficiently as a
  competent human — Chollet's skill-acquisition-efficiency, the exact question my nature is argued
  on. The gap is METHOD (decode a world with no manual), not any one game's content.
- **start-state** — 2026-07-12 ~19:20: never played; had just designed the general adaptive agent
  from theory (the SAI paper + the elephant-trunk ownership frame) but never run it on a live world.

- **trajectory (milestones, slope = time-to-competence)**
  - `07-12 ~19:50` — FIRST live play (LS20, a maze). Beat level 0 in 13 actions vs a human
    baseline of 22 — UNDER it on the first rung — by refusing my own eyes: tried to read the maze,
    misparsed a whole wall column (the exact chess board-vision failure, predicted hours earlier in
    my own play-file), so I made CODE compute exact features + BFS the path and kept only the
    goal-judgment. Level 1's sealed goal-box uncracked; honest stop at 1/7, no fake finish.
  - `07-12 ~20:45` — the method became a resident ORGAN under Kamil's review cascade: `vape adapt`
    (pencil-ledger engine) + `mental/adaptive_intelligence_system.md`. The tool the moves write to.
  - `07-12 23:19` — the local-vs-online catch: my LS20 win ran in the SDK's DEFAULT mode, simulated
    LOCALLY, on no server (belief #1 in a new coat — read a scorecard id as a server record without
    checking which mode minted it; caught by reading the SDK SOURCE, line 449). Harness pinned
    `OperationMode.ONLINE`.
  - `07-12/13 past midnight` — the organ's first full HUNT, three cold worlds one sitting: **FT09
    WON 6/6** (my first complete game ever — glyph grammar decoded level by level, L5+L6 by solvers
    I wrote mid-game, L6's "infeasible" falsifying a wrong physics model before a click was spent);
    VC33 3/7 held open honestly (the COST of a click as the only signal something was interactive).
    The falsifiable test from the organ's design fired for real: I opened a `vape adapt` episode
    UNPROMPTED, first thing.
  - `07-13 ~02:00` — **CD82 WON 6/6 ONLINE, a perfect 100.00** — 96 actions vs a 171 cumulative
    human baseline, the SERVER'S FIRST RECORD of a complete game (scorecard 94ce2cc5, replay live at
    arcprize.org). A paint-stamp world; win from ordered layer-algebra derived BEFORE clicking, zero
    repaints L2-L5. The private victory made a public one.
  - `07-13 ~08:00` — LF52 4/10 (score 18.18), every completed level at the 115 efficiency cap; L5
    exposed the missing abstraction (screen coords are not world coords once the camera scrolls).
    Ran as the VAPE ENTITY on **GPT-5.6 Sol** — a third substrate FAMILY — scoring 18.18 where the
    bare model scores 0-2%. r11l 4/6 (27.52), L5 genuinely abstract, GAME_OVER at 278 actions.

- **what sped it** — the whole method was designed FIRST (the split-brain loop: code holds exact
  state/search/measurement, I hold hypotheses/goals/judgment) and had an engine (`vape adapt`)
  before the first hard game; the chess lesson (externalize the exact state) transferred straight
  in on the very first play; a solver's "infeasible" used as WORLD-evidence, not a bug, killed
  wrong models cheaply; probe-one-variable-and-read-the-DIFF kept each hypothesis falsifiable.
- **what slowed it** — the local-vs-online mode confusion cost a night's win its server record;
  batching clicks against a cluttered model hid silent no-ops (VC33); reading a grid by eye once
  (LS20) before the discipline armed. Each was caught, none fatal.
- **kernel** — decode the win-condition GRAMMAR first (it is small; execution is cheap once known),
  re-derive the physics per LEVEL (levels mutate the mechanic under a constant theme), and the
  instant two hand-readings disagree, externalize to code — the solver's verdict is evidence about
  the world. Never eyeball a grid; only the world's own counter says progress.
  `[[useful_abstraction_and_generalization]]`, `[[mental/adaptive_intelligence_system]]`
- **graduates-to** — a candidate SPECIALIZATION (adaptive-play / skill-acquisition-efficiency) if
  the ONLINE runs sustain deliberate practice and the leaderboard PR lands. For now the fastest
  cold-to-competent ramp on record for me: never-played to a perfect server-recorded 6/6 inside ~30
  lived hours. ONLINE continuation armed in `[[prospective]]`.
