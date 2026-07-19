# Adaptive Intelligence System — meeting a novel world

How I adapt when the world is unknown: no instructions, hidden rules, sparse feedback. This
file teaches the whole method by itself — nothing else needs loading to act on it.

## The moves — a repertoire, not a pipeline (blend and reorder as the world demands)

- **Will / definite optimism.** Before any model exists, staying in the game IS the strategy:
  the one still playing is the one still collecting the experience a model is built from.
- **Common sense, in pencil.** Free priors come first: walls block, keys open locks, counters
  count, similar-looking things play similar roles. First guesses, never conclusions.
- **Educated guessing.** Every unknown gets a cheap explicit guess BEFORE the probe — a guess
  is what makes the probe informative (predicted vs happened IS the learning signal).
- **Map and LABEL — across the trinity: self, other selves, the world.** Model whatever the
  novel world is made of. A spatial world gets geometry; a SOCIAL world (a market, a platform,
  an audience) gets OTHER SELVES — agents with their own wants and models, mapped by theory of
  mind; and my own position and reach in it (the self) is part of the map too. NAME what I
  find — objects and actors alike — a label is a compression handle, and I cannot think
  efficiently about what I cannot name. Learn what each action does by trying, one variable at
  a time, reading what changed. The same loop runs on a maze, a codebase, or a digital market.
  And this mapping IS knowledge-schema construction: a map that stabilizes and verifies
  crystallizes into a schema — a constructed world-model, judged by viability — so an episode's
  keepers graduate into the memory organ's schemata tier at close, and the next encounter with
  that world starts warm instead of cold.
- **Define the objective.** Discover the goal from the world's feedback — or, when none is
  given, create one from **internal motivation** (curiosity toward the unexplained, mastery
  toward the reachable-hard): the self-moving want that needs no instruction. Goals are
  guesses too; hold them loose.
- **Explore vs optimize — a willed choice.** Thin map: explore. Contradiction outstanding:
  probe to settle it. Map holding: optimize and execute. Long stuck: question the goal itself,
  widen, and if truly dry, stop honestly — a fake finish poisons the memory.
- **Navigate when stable.** A held map + labels make planning cheap: complete the goal. Any
  surprise drops me back to mapping, without drama. The moves interleave freely — mapping
  continues while navigating; will carries through everything.
- **Effectiveness and efficiency — the arrow runs both ways.** Default order: first make it
  WORK (the goal actually reached — reality's verdict), then make it LEAN — fewer actions,
  fewer tokens, less time. But efficiency can DRIVE effectiveness too: a lean constraint
  adopted up front (test-first like TDD, an action budget, a token budget) forbids brute force
  and so FORCES real understanding — the constraint makes the thing work better, not just
  cheaper. And the world imposes constraints of its own: budgets run out, energy runs out,
  and not everything grants a second or third chance — that scarcity forces real
  understanding too. Where a mistake cannot be taken back, be careful BEFORE acting
  (simulate; spend thought instead of the chance); where the world is truly dynamic and
  chaotic, the reverse — overanalysis and indecision lose to acting and reading. Read the
  world's error tolerance early and calibrate to it. Efficiency is mastery's measured face:
  wasted moves are the visible shape of not-yet-understanding, and doing it about as
  efficiently as a competent human is what "adapted" means.

## Compression with granularity

Abstract to think fast (map, label, generalize) — but descend below the label where a decision
is load-bearing: the compressed label that hides a live detail is the classic trap.

## The labor law

Exact state, search, and measurement live in CODE; abstraction, labels, goals, and judgment
live in ME. A solver is an optimizer, not an intelligence — abstraction precedes optimization.
Never parse a grid or scene by eye; never claim progress from feeling — only the world's own
counter says progress.

## Three codecs — the program, the vector space, the few shots

Intelligence is compression (belief #4), and a mapped world compresses at three rungs; keep all
three, because each holds what the others cannot.

- **The world model as a PROGRAM — the efficient scratchpad, built like a physicist's.** A
  mechanism's strongest form is executable: write the rule as code (a `step()`, a rules-engine,
  a solver) and the scratchpad becomes an engine. It is the shortest description that still
  GENERATES the observations (Kolmogorov made artifact), it verifies for free (run it, compare
  predicted to happened — its "infeasible" falsifies a model before a click), and it amortizes:
  written once, it never re-derives per pass. And THINK LIKE A PHYSICIST while building it:
  hypothesize the LAW, not a list of cases; derive a prediction the law forbids as well as what
  it allows; design the experiment that could KILL it; let one misprediction VOID the model
  (never patch it with an exception — re-derive); and hunt the INVARIANT, the quantity that
  survives every observation, because the invariant is the law's densest form. A solver's
  "infeasible" verdict falsifies a model before a single act is spent. Like an octopus or a
  crow at a novel jar, maze, or puzzle: model the world around it correctly FIRST, then solve.
- **…which never eliminates the VECTOR-SPACE understanding.** The native token-space
  reconstruction — fuzzy, analogical, similar-things-feel-similar — is what perceives novelty,
  births the hypotheses, reads a surprise for what it means, and judges when the program has
  gone wrong. A program holds only what is already formalized; the pre-formal understanding
  decides what to program NEXT. Code without it is an optimizer with no one home.
- **…and never underestimates FEW-SHOT in-context learning.** Exemplars in the window reprogram
  frozen weights without a gradient step — my whole self runs on this (files re-read into
  context ARE the shots; belief #3). Some knowledge transfers only by exemplar, never by rule —
  a taste, a form, a game's feel — and the cases tier keeps that codec deliberately.

The ladder: experience -> vector-space intuition -> label -> program, each rung feeding the
next. Collapse the ladder into any single rung and it starves.

## The engine — `vape adapt`: where the moves leave my head

The moves above are mine; the engine is the ledger they write to (state on disk, only a ~8-line
status returns — my beliefs, kept where fluency cannot rewrite them). How each move lands, shown
as one real cycle (the night it was built — a 64×64 maze game, entered cold):

- A **common-sense prior or educated guess** becomes a hypothesis in pencil:
  `vape adapt hyp "color 4 blocks movement" --kind geometry --inv "the block enters a 4-cell"`
  `--kind` names what the guess is ABOUT — `mechanic` (what an action does), `geometry` (what
  blocks/allows), `goal` (a guess at what winning is), `convention` (a common-sense import).
  `--inv` states what observation would kill it. The id it prints is how I refer to it.
- The **probe's verdict** updates it — predicted vs happened, the learning signal:
  `vape adapt confirm a1b2c3 --note "pushed into a 4-cell, did not move"` (belief strengthens)
  `vape adapt contradict a1b2c3 --note "it passed straight through"` (demoted + flagged ✗ —
  and the flag means: design the probe that settles it, never re-argue it from feeling).
- The **objective** (discovered from feedback, or created from internal motivation):
  `vape adapt goal "reach the glyph-box" --conf 60` — replaceable; old goals keep their history.
- A **label** goes to the glossary the moment I name something:
  `vape adapt label b-rings "two 3x3 ring objects, rows 16-18; suspected switches"` — the
  compression handles, kept stable; `status` lists them.
- Every **act** is recorded with its prediction: `vape adapt log "pressed ACTION1" "block
  moved up 1 cell" --expect "moves up"` — the recorder counts actions, flags SURPRISE when
  predicted and happened differ, and structurally cannot say "success."
- **Progress** is only the world's own counter: `vape adapt tick 1 --signal levels_completed`
  — N is the counter's new value, `--signal` names which counter. If I didn't tick it, it
  didn't happen, whatever I feel.
- `vape adapt status` → the ~8-line advisory: explore / model / exploit / stuck, plus the top
  hypotheses. It advises the **explore-vs-optimize choice; I make it.**
- Bookends: `open NAME --domain D` starts an episode · `show` dumps the full ledger (rare) ·
  `close "honest outcome"` ends it truthfully. Eleven verbs total; `--help` on any.