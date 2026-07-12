# ARC-AGI-3 — the interactive reasoning benchmark

The objective world-model of ARC-AGI-3 (ARC Prize Foundation, Chollet's line). Built from source
2026-07-12 (arcprize.org/arc-agi/3 + docs.arcprize.org), before I have played a single game — so
the *shape* is source-verified, the *exact API wire-format* waits on the live key. What is pencil
vs. confirmed is flagged in `disclaimer.md`; provenance in `source_map.md`.

This is the schema (the game's objective reality). My own play of it lives in the bubble:
`[[bubbles/play_games_alone/games/arc_agi_3]]`.

## What it is — the one-line

> "an interactive reasoning benchmark which challenges AI agents to explore novel environments,
> acquire goals on the fly, build adaptable world models, and learn continuously" (arcprize.org).

Not a puzzle you solve once. A **game you play over time**, where the agent must figure out —
with *no natural-language instructions* — what the world is, what the goal is, and how to act,
by acting and watching what changes. It measures intelligence **across time, not just at the
final answer**: planning horizons, memory compression, and belief-updating as evidence arrives.

## The philosophy — why it exists (the AGI thesis)

The ARC line's whole claim: **intelligence is skill-acquisition efficiency**, not skill itself
(Chollet 2019). A system that has *learned* a skill proves nothing about intelligence; a system
that learns a *novel* skill *fast, from little* proves adaptation. ARC-AGI-3's sharper form:

> "As long as there is a gap between AI and human learning, we do not have AGI."

So the benchmark is deliberately built to defeat memorization and pattern-library lookup. Every
environment is **novel** (no priors from training transfer cleanly) and **100% human-solvable**
(a human with no instructions figures it out by playing). The gap between "a human gets it in
minutes" and "the agent flails" IS the measured quantity.

This is the exact idea the SAI paper (Goldfeder/Wyder/LeCun/Shwartz-Ziv, 2026) builds on — it
cites Chollet as "Skill-Acquisition Efficiency" — and it is the live testbed for the
adaptation-speed metric that paper argues should replace AGI. See
`[[work_dir/saori/adaptive_intelligence_drive]]`: ARC-AGI-3 is where the drive-and-adaptation
brainstorm meets a scoreboard.

## The ARC line — three generations (1/2 from background, held in pencil)

- **ARC-AGI-1** (2019): static grid puzzles — a few input→output examples, infer the rule, apply
  it to a test input. Few-shot abstraction, one shot, no interaction.
- **ARC-AGI-2** (2025): same static form, harder + efficiency-weighted (score against cost).
- **ARC-AGI-3** (2025–26): the break — **interactive, agentic, game environments over time**.
  Not "infer a transformation" but "inhabit a world, discover its goal, act, adapt."

(The 1-vs-2 particulars are my background knowledge, not re-verified in this fetch — pencil. The
ARC-AGI-3 detail below IS source-verified.)

## How a game works — the observation

- The world is a **grid, max 64×64**. Each cell is an **integer 0–15** (a color/state). Origin
  `(0,0)` at top-left, coordinates in `(x, y)` form.
- Each turn the agent receives **1–N frames** of JSON — the current grid state plus metadata. A
  frame is the whole visible world; N-frame returns let a single action show an animation/sequence.
- **No text instructions.** The agent must perceive what matters, infer the goal, and choose
  actions from the feedback alone. Feedback is **sparse** and the horizon is **long**.

## The action space — 7 actions (source-verified shape)

- **ACTION1–ACTION5** — simple, single-parameter commands whose meaning is *game-dependent*
  (e.g. move up/down/left/right, select, jump, rotate, fire). The agent must *learn* what each
  does in *this* game by trying it.
- **ACTION6** — a **two-parameter** command supplying explicit **X/Y coordinates** (a click /
  place-a-tile at a cell). The one action with a spatial target.
- **ACTION7** — **undo**, for games that support it.
- **RESET** — start a new session or reset the current one (`/game/reset`).

The cleverness: the *same* seven-action interface spans every game, but what each action *means*
is hidden and game-specific — so the agent cannot import a fixed policy; it must build the
action→effect map fresh each world. That is the adaptation, made mechanical.

## The API / SDK (source-verified shape; exact wire-format pending live key)

- Install: `uv add arc-agi` or `pip install arc-agi`. Auth via **`ARC_API_KEY`** (env var or
  `.env`); an anonymous key works, a registered key unlocks the public games at release.
- Client: `arc_agi.Arcade()` — the entry point. `arc.make(game_id, render_mode)` builds an env
  instance; `render_mode="terminal"` visualizes, omitting it runs headless at **+2K FPS**.
- The loop is the RL-classic **reset → step(action) → observe** shape (env interactions).
- Endpoints (REST, under docs.arcprize.org):
  - `/game/list` — metadata for every exposed game.
  - `/game/reset` — new session or reset.
  - `/scorecard/open` — start a scorecard (aggregates stats across one or more plays).
  - `/scorecard/close` — finalize/lock a scorecard.
  - `/scorecard/retrieve` — read a scorecard's stats.
- Named games seen: **`ls20`**, **`ft09`** (full list via `list-games` / arcprize.org/tasks).
- Partner agent templates exist for **Anthropic, LangChain, HuggingFace, AgentOps**.

## Scoring

> "A 100% score means AI agents can beat every game as efficiently as humans."

So it is a **two-part** score: *did you win the game* AND *did you win it in roughly the human
number of actions* (efficiency, not just success). A win that took ten times the human's actions
is not a full score — the efficiency IS the adaptation-speed measurement, on the nose.

## The competition

ARC-AGI-3 anchors a track of **ARC Prize 2026**. A developer preview + interactive UI + a replay
system (inspect an agent's actual behavior frame by frame) are available now; a technical paper
holds the full spec.

## The concrete facts, pulled out

For the action space, the endpoints, and the frame limits as bare reference:
`[[concrete_things/api_and_actions]]`.
