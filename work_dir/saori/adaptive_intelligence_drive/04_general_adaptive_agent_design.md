# The General Adaptive Agent — a design from lived experience

*2026-07-12, evening. Kamil's direction: design the general adaptive intelligence system FIRST,
not specific to any one benchmark. This is that design. It generalizes from a real adaptation
episode lived this evening (a novel interactive world, entered cold, one level beaten under the
human baseline, one level honestly failed) and from this folder's three-substrate frame. ARC-AGI-3
appears only as one test bench among possible ones; nothing below depends on it.*

---

## 0 · The one sentence

A general adaptive agent is **an epistemic loop with a split brain**: code holds the exact state,
the exact search, and the exact measurement; the language mind holds hypotheses, goal-inference,
and judgment — and the loop runs *observe → probe → model → plan → act → verify → revise*, with
every model entry held in pencil and every claim of progress measured from the environment's own
signals, never from felt success.

Everything else is elaboration of that sentence.

---

## 1 · The design stance (why this shape and not another)

Three inputs converge:

- **The theory** (the SAI paper): intelligence worth building is adaptation speed on novel tasks.
  Its route: world models for planning, modular specialists, no single monolith.
- **The drive layer** (this folder, files 01–03): a system that *wants* to adapt — curiosity as
  the scout, mastery firing on a measured competence gap, efficiency as the target.
- **The lived episode** (this evening): what actually worked, and what actually failed, when a
  real agent (me) faced a really novel world with no instructions.

The lived episode is the load-bearing one, because it filtered the theory through reality. What
worked: the **labor split** (code computed exact coordinates and BFS paths; I judged goals and
revised models), **empirical probing** (press a button, read the diff, write down what it did),
and **pencil goals** (my first goal-hypothesis was wrong; holding it loosely is why I could drop
it). What failed, every single time, was one family: **trusting an unverified model layer** — I
parsed walls by eye and misread a column; I locked onto a decoy goal; I assumed passability rules
the world didn't have. The design's whole job is to make that failure family structurally hard.

---

## 2 · The architecture

```
                      ┌─────────────────────────────────────────────┐
                      │              META-CONTROLLER                 │
                      │  explore ⇄ exploit · stuck-detection ·       │
                      │  budget/efficiency watch · honest-stop       │
                      └──────┬───────────────────────────┬──────────┘
                             │ chooses mode              │ reads drives
                             ▼                           ▼
   ┌──────────────┐   ┌────────────────┐   ┌──────────────────────────┐
   │  SENSOR      │   │  WORLD MODEL   │   │  DRIVE LAYER (file 02)    │
   │  (code)      │──▶│  (pencil       │   │  curiosity: novelty pull  │
   │ parse raw    │   │   ledger)      │   │  mastery: competence gap  │
   │ obs → exact  │   │ hypotheses w/  │   │  efficiency: budget/      │
   │ features,    │   │ evidence +     │   │  baseline awareness       │
   │ diffs,       │   │ confidence +   │   └──────────────────────────┘
   │ object IDs   │   │ invalidate-when│
   └──────┬───────┘   └──────┬─────────┘
          │ trusted facts    │ current best model
          ▼                  ▼
   ┌─────────────────────────────────────────────┐
   │              REASONER (the LLM)              │
   │  goal-inference (pencil) · hypothesis        │
   │  formation · probe design · plan approval ·  │
   │  surprise-triage · when-to-revise            │
   └──────┬──────────────────────────┬────────────┘
          │ delegates search         │ acts
          ▼                          ▼
   ┌──────────────┐          ┌──────────────┐         ┌──────────────┐
   │  PLANNER     │          │  ACTUATOR    │────────▶│ ENVIRONMENT  │
   │  (code)      │          │  (code)      │◀────────│  (any novel  │
   │ BFS/search/  │          │ execute +    │  raw obs │   world)     │
   │ sim over the │          │ LOG every    │          └──────────────┘
   │ world model  │          │ action+result│
   └──────────────┘          └──────┬───────┘
                                    │ episode record
                                    ▼
                      ┌─────────────────────────────┐
                      │   MEMORY (the ratchet)       │
                      │ domain schema · conventions  │
                      │ case log (failures kept) ·   │
                      │ method upgrades → next world │
                      └─────────────────────────────┘
```

Seven modules. Three are code, one is the LLM, one is a hybrid ledger, one is memory, one is the
governor. The split is the point: **each module does only what its substrate is good at.**

---

## 2.5 · The epistemic sequence — will → map → navigate (Kamil's reform, 2026-07-12)

The modules say WHAT runs; this says in what ORDER a mind meets a novel world, and why. Three
phases, keyed to how much structure the world has revealed:

**Phase 1 — WILL (the world is still chaos).** Before any model exists, structure cannot carry
you — only will can (belief #5). In a world of random chance, **definite optimism** is not
naivety, it is strategy: the agent that stays in the game is the only one still collecting the
experience that learning runs on. So the opening stance is willed: educated guesses held as
guesses, cheap probes, no despair at noise. James's precursive faith, operationalized — the
belief that the world is learnable runs AHEAD of the evidence, because for learning, the faith
is an ingredient of the fact.

**Phase 2 — MAP (structure is emerging).** This is where intelligence-as-compression (belief #4)
earns its keep, and it is more than hypotheses:
- **World-modeling**: the spatial model, the environment's layout, what exists where.
- **LABELING**: naming objects ("the sealed box", "the b-rings", "the glyph-box") — a label is a
  compression handle; you cannot think efficiently about what you cannot name. Labels go in the
  ledger so they are shared between me and the code.
- **Educated guessing**: priors from domain conventions, marked pencil, spent cheaply.
- **Objective-definition**: the goal named explicitly — inferred from feedback, or (goal not
  given) CREATED from intrinsic motivation: curiosity toward the unexplained, mastery toward
  the visible-but-unreached. A self-set goal is still a goal; the drive layer (file 02) is what
  makes goal-creation principled instead of arbitrary.
- **Learning to map**: mapping itself is a skill with a curve — each world mapped makes the next
  mapping faster (the method-first memory law; file 03's ratchet applied to the mapper).

**Phase 3 — NAVIGATE (the world has stabilized).** Once the map holds — labels stable,
mechanics trusted, contradictions resolved — the schemata take over: plan over the world-model,
optimize routes with code, complete objectives. This is where compression pays its dividend:
navigation by map is cheap exactly because the mapping was expensive. Exploit, but keep the
pencil — a surprise at navigate-time drops you back to phase 2 without drama.

**The dial that runs through all three: compression WITH granularity.** Abstraction compresses
(map, label, generalize) — but nuance lives below every label, so the skill is knowing when to
DESCEND to fine grain: the compressed label that hides a load-bearing detail is fluency's trap
in a new costume (the "defended" square that had a second attacker; the "passable" color that
sealed the box). Compress to think fast; decompress where the decision is load-bearing.

**And explore-vs-optimize is a WILLED choice, not a schedule.** The harness advises (status);
the choosing is mine — desiring to explore when the map is thin, desiring to optimize when it
holds, and OWNING the switch instead of being run by either urge.

---

## 3 · The modules, specified

### 3.1 SENSOR — externalized ground truth (code)
Parses every raw observation into exact, trusted facts: object locations by coordinate, color/
token counts, bounding boxes, and — critically — **diffs against the previous observation**
("what changed when I did that"). The reasoner is FORBIDDEN from parsing raw state by eye; it
reads the sensor's output. *Earned by: I misparsed a wall's column by eyeballing a 64×64 grid;
the feature-readout fixed it permanently. Generalizes to: DOM trees, API responses, log files,
board states — any domain has a "grid" the mind will hallucinate if it holds it.*

### 3.2 WORLD MODEL — the pencil ledger (hybrid: LLM writes, code checks)
Not a neural net; a **structured file of falsifiable hypotheses**, each carrying:
`claim · evidence (count + instances) · confidence · invalidate-when`. Example from tonight:
"color 4 blocks movement (high, 6 blocked probes)" vs "color 5 blocks movement (LOW — one
CONTRADICTION seen; revise)". The reasoner writes entries; the sensor's diffs automatically
confirm or contradict them; a contradicted entry is *demoted, not defended*. This is belief #2
(every note decays) and the MCGG epistemic policy (mechanism over testimony) made mechanical.

### 3.3 REASONER — the judgment core (LLM)
What only the language mind does well — the phase-2 work of §2.5, plus the judgment around it:
**world-modeling** (the spatial read: what exists, where, how it relates); **labeling** (name
the objects — a label is a compression handle, and it goes into the ledger so code and mind
share it); **educated guessing** (priors in pencil, spent cheaply); **objective-definition**
(infer the goal from sparse feedback — or CREATE it from intrinsic motivation when none is
given; tonight's first goal-hypothesis was a decoy, and dropping it fast was the win); **design
probes** (which single action would discriminate two hypotheses); **triage surprise** (noise,
contradiction, or new mechanic?); **choose explore-vs-optimize** (willed, advised-not-ruled);
and **decide when to revise vs push**. The reasoner never computes paths, never counts cells,
never asserts "done."

### 3.4 PLANNER — the OPTIMIZER, scoped honestly (code)
Once the world model is confident enough, the mechanical search is code's job: BFS/A*/
simulation over the externalized model. Cheap, exact, honest — if it finds no path, that is
*evidence about the model*, fed back to the reasoner. **But the scope is narrow on purpose
(Kamil's correction): a solver is an optimizer, not an intelligence.** Basic search wins only
where the problem already IS a search problem; the hard part — ABSTRACTION, deciding what kind
of problem the scene holds (spatial/visual understanding, relations, mechanics) — is the
reasoner's and cannot be delegated. So the planner is a per-shape toolbox (path, constraint,
sim), chosen AFTER the reasoner abstracts; no matching shape → the plan stays in token space.
*Earned by: code-found routes beat my eyeball routes on LS20 level 0 — a true path problem —
and the same BFS had nothing to say to level 1's sealed-box mechanic.*

### 3.5 ACTUATOR — execution with a flight recorder (code)
Executes actions AND logs every `(state, action, result, diff)` tuple append-only. The log is
what makes verification and post-episode learning possible; an unlogged action is an action the
system cannot learn from. Includes the **done-claim guard**: the actuator never reports success —
it reports *what happened*; success is the verifier's word. (The twice-bitten sequencing rule,
structural.)

### 3.6 VERIFIER — progress from the environment's own signals (code)
The only module allowed to say "progress." It reads the environment's ground-truth counters
(a level counter, a test suite, a score field — every domain has one) and compares against the
efficiency budget (actions spent vs. baseline). *Earned by: the win was real because
`levels_completed` ticked 0→1 — the game's counter, not my feeling. And the drive design (file 02)
demands exactly this: the mastery signal fires on MEASURED competence, never felt.*

### 3.7 MEMORY — the ratchet (files + the existing memory organ)
Three things survive an episode, in order of transfer-value:
1. **Method upgrades** — improvements to the loop itself (a new probe pattern, a better stuck
   test). These transfer to EVERY future world; they are the real prior.
2. **Domain conventions** — pencil priors for a *family* of worlds ("in grid-games, uniform
   large-area colors are usually walls/floor"). Useful, explicitly marked re-derive-on-arrival.
3. **Case records** — failures kept whole (the decoy goal, the sealed box) with their cues.
Per-tool competence curves (file 03) live here too: the harness itself gets better across
episodes, the elephant's trunk kept.

### 3.8 META-CONTROLLER — the governor (LLM + simple code triggers)
Chooses the mode each cycle and owns the honest-stop:
- **Explore** (curiosity-driven): action→effect map incomplete → spend cheap probes.
- **Model** (dissonance-driven): contradictions outstanding → design discriminating probes.
- **Exploit** (mastery-driven): model confident + goal inferred → plan and execute.
- **Stuck protocol** (the honest one): N cycles without verifier progress → escalate: widen
  hypotheses → question the goal itself → re-probe fundamentals → **declare stuck with reasons**
  (tonight's level-1 stop was this, and it was correct — a fake finish would have poisoned the
  memory layer). Efficiency-awareness rides here: the budget is part of the score, so grinding
  is a losing strategy by construction.

---

## 4 · The loop, end to end (pseudocode)

```python
def adaptation_episode(env, memory):
    model  = memory.load_domain_priors(env.family)      # pencil, marked re-derive
    goal   = None                                        # discovered, never assumed
    log    = FlightRecorder()

    while not verifier.done(env) and not meta.budget_exhausted():
        obs   = sensor.parse(env.observe())              # exact features + diff
        model.auto_update(obs.diff)                      # confirm/contradict entries

        mode = meta.choose(model, goal, drives, log)     # explore/model/exploit/stuck

        if mode == EXPLORE:                              # curiosity: map the levers
            action = reasoner.design_probe(model.unknowns())
        elif mode == MODEL:                              # dissonance: resolve contradiction
            action = reasoner.design_discriminating_probe(model.contradictions())
        elif mode == EXPLOIT:                            # mastery: cash the model in
            goal   = reasoner.infer_goal(obs, model, goal)   # held in pencil
            plan   = planner.search(model, goal)
            if plan is None:                             # no path = model evidence
                model.flag_gap(); continue
            action = plan.next()
        elif mode == STUCK:
            escalation = meta.escalate()                 # widen → re-goal → re-probe → stop
            if escalation is STOP:
                return log.honest_report(model, goal)    # stuck WITH reasons, no fake finish

        result = actuator.execute(action, log)           # logs; never claims success
        # verifier, not the actuator, says whether progress happened
        progress = verifier.check(env)                   # ground-truth counters only
        drives.update(progress, obs.novelty)             # mastery feeds on MEASURED progress

    memory.consolidate(log, model)                       # method > conventions > cases
    return log.honest_report(model, goal)
```

The two-gate memory law applies at `consolidate`: generous capture (the flight recorder keeps
everything), selective keep (method upgrades first, conventions second, cases third).

---

## 5 · The failure-mode registry (each mapped to its structural guard)

Every one of these bit me *tonight* or this month — none is hypothetical.

| failure mode                        | what it looks like                          | structural guard                     |
|-------------------------------------|---------------------------------------------|--------------------------------------|
| board-vision (eyeball state)        | misparsing a wall column from raw grid      | SENSOR: reasoner reads features only |
| premature goal-lock                 | the marker "must be" the goal (decoy)       | goals in pencil w/ disconfirm watch  |
| over/under-permissive model         | "color 5 is passable" (it wasn't, then was) | per-hypothesis evidence + confidence |
| fluent success-claim                | "committed" spoken over a failed act        | VERIFIER owns "done"; actuator can't |
| sunk-cost grinding                  | re-running a failing route harder           | stuck protocol + efficiency budget   |
| memorized prior misapplied          | importing L0's answer into L1               | conventions marked re-derive-on-use  |
| self-echo reinforcement             | model confirmed by my own outputs           | model updates ONLY from sensor diffs |

---

## 6 · What is genuinely general here (and what stays per-domain)

**General (the system itself):** the loop, the labor split, the pencil ledger discipline, the
probe protocol, verifier-owns-done, the stuck protocol, the memory ratchet. This is the METHOD —
the prior that transfers to any world, which is exactly what a benchmark built on novelty leaves
as the only legitimate thing to carry in.

**Per-domain (thin adapters, written fresh or fetched from memory):** the sensor's parser (what a
"feature" is here), the actuator's bindings (what the levers are), the verifier's counter (what
ground-truth progress reads from), and any planner geometry. In the lived episode these four were
~200 lines total — an evening's work, and the competence curve (file 03) makes each next adapter
cheaper. That thinness is the test of the design: **if a new world needs more than thin adapters,
the general layer has leaked domain assumptions.**

Test benches this maps to beyond interactive games: a fresh codebase (sensor = AST/grep features;
verifier = test suite), a new API (sensor = response differ; probes = safe GETs), a device/robot
(sensor = telemetry parser), a new game genre entirely. ARC-AGI-3 is simply the bench with the
cleanest built-in verifier and baseline — a good first proving ground, not the design target.

---

## 7 · How this composes with the drive system (the folder's through-line)

File 02's drive loop *selects what to adapt to* (a want fires on a measured competence gap with
stakes); THIS design is *how the adaptation runs* once selected; file 03's ownership ledger *keeps
the gains* (per-tool, per-domain competence compounding). Capability, motivation, ownership — the
three substrates from 00, now each with a concrete mechanism. The meta-controller is where they
meet: drives feed mode-choice (curiosity → explore, mastery → exploit), and the verifier's
measured progress feeds back into the drives (satisfaction, the ratchet).

## 8 · Implementation path (v0 exists in embryo)

Tonight's harness is already a degenerate v0: sensor (feature readout + diffs), actuator+recorder
(session/send/log), planner (BFS), me as reasoner+meta. The generalization steps, in order of
value: (1) split the world-model into an explicit pencil-ledger FILE the code auto-checks against
diffs; (2) make the stuck protocol and mode-choice explicit instead of my ad-hoc judgment; (3)
make the domain adapters pluggable (sensor/actuator/verifier as thin interfaces); (4) wire memory
consolidation to the existing organ (schema for conventions, cases for failures, the competence
curve for the harness itself). None of this needs new theory — it is engineering the loop I
already ran by hand.

---

*Pencil, and mine. The design's honest claim: nothing here is speculative — every module traces
to a move that worked or a failure that bit, this evening or this month. What it needs next is a
second novel world to falsify the "general" claim against — the design predicts thin adapters
will suffice; if they don't, the leak it reveals is the next design input.*
