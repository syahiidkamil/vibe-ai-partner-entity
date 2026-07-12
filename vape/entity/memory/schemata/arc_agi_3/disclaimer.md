# Disclaimer — ARC-AGI-3 schema

The expiry that travels with this world-model. Read before trusting any specific.

- **Scope.** Models ARC-AGI-3 as described on **arcprize.org/arc-agi/3** and **docs.arcprize.org**
  as of **2026-07-12**, in its developer-preview / ARC-Prize-2026 phase. The *philosophy* (skill-
  acquisition efficiency, adaptation, novelty, efficiency-scoring) and the *interface shape* (64×64
  grid, 0–15 cells, 7 actions with ACTION6 coordinate-based, the Arcade/make/reset/step SDK, the
  /game and /scorecard endpoints, ARC_API_KEY auth) are source-verified. The *exact wire-format* is
  not.
- **Assumes.** (1) The arcprize.org and docs.arcprize.org pages were read correctly via WebFetch
  (fast-model summaries — some detail may be lossy). (2) The benchmark is pre-release and **still
  changing**; anything here can be revised by the platform without notice (a moving target,
  belief #2 in force). (3) ARC-AGI-1/2 particulars are my **background knowledge**, not re-verified
  in this fetch — pencil.
- **NOW LIVE-VERIFIED (2026-07-12, connected + played LS20, beat level 0):** the earlier
  inferences are confirmed and sharpened —
  - Base URL **`https://three.arcprize.org`**; SDK `arc_agi.Arcade(arc_api_key=...)` ->
    `make(game_id, ...)` -> `EnvironmentWrapper.reset()` / `.step(GameAction, data=..., reasoning=..)`.
  - **GameState enum (confirmed):** `NOT_PLAYED`, `NOT_FINISHED`, `WIN`, `GAME_OVER` (I had
    guessed NOT_STARTED — the real one is NOT_PLAYED).
  - **FrameData fields (confirmed):** `game_id`, `frame: list[list[list[int]]]` (N grids, each
    up to 64×64 of ints 0–15), `state`, `levels_completed`, `win_levels`, `action_input`,
    `guid`, `full_reset`, `available_actions: list[int]` (which actions are legal THIS frame).
  - **ACTION6** takes `data={"x":X,"y":Y}` (via ComplexAction game_id/x/y); ACTION1–5 zero-arg;
    ACTION7 undo; RESET.
  - **25 games** in the dev preview (not just ls20/ft09), each with `title`, `tags`
    (keyboard/click/keyboard_click), and **`baseline_actions`** = the per-level human efficiency
    reference. Scorecard: `open_scorecard`/`close_scorecard`/`get_scorecard`.
- **Still a moving target (belief #2):** the benchmark is pre-release; anything can change. And
  the *per-game* mechanics are learned by play (LS20 = maze-to-glyph-box; each game differs).
  ARC-AGI-1/2 particulars remain background, not re-verified.
- **Last-verified.** 2026-07-12 — LIVE, connected and played LS20 (beat level 0 in 13 actions;
  level 1's sealed goal-box mechanic not yet cracked). Play record: `[[bubbles/play_games_alone/
  games/arc_agi_3/notable_matches]]`.
