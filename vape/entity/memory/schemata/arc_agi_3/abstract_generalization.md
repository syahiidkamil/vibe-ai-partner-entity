# Abstract Generalization — ARC-AGI-3

The transferable kernels this world hands up. Two altitudes: within-domain (laws of interactive
benchmarks) and cross-domain (kernels that leave the benchmark behind).

## Within-domain — laws of the interactive-benchmark world

- **A fixed interface over hidden semantics forces adaptation.** Seven actions span every game,
  but each action's *meaning* is game-specific and unstated. You cannot import a policy; you must
  rebuild the action→effect map each world. The generality lives in the *learning procedure*, not
  in any learned map — which is the whole point the SAI paper argues.
- **Score efficiency, not just success.** "Beat every game as efficiently as humans." Success is
  binary and cheap to game (brute-force enough actions); efficiency (win in ~human action-count)
  is what actually measures adaptation. A benchmark that scored only success would measure
  persistence, not intelligence.
- **Novelty is the anti-memorization guard.** Every environment is new, so a pattern library
  can't cover it. This is the structural defense against fluency — you cannot recite your way
  through a world you've never seen. (belief #1, built into a benchmark.)
- **Sparse feedback + long horizon = the world model earns its keep.** With no instructions and
  rare reward, the only way to act well is to *simulate* — build an internal model of the world's
  rules and run it forward before paying for a move. Reactive policies drown; model-based ones
  survive. ("Pixels are not state" — the SAI paper's line, lived.)

## Cross-domain — kernels that leave the benchmark behind

- **Intelligence is measured in the GAP between reach and grasp, not in the grasp.** What ARC
  scores is not skill but the *distance a novel skill travels per unit of experience*. This is
  the exact shape of the mastery-trigger from the drive brainstorm: the competence gap at the
  right difficulty, measured against reality, is the unit of both *learning* and *intelligence*.
  For a stateless self, this is why **memory = learning = adaptation-speed are one thing**.
- **A goal you must DISCOVER is harder and truer than a goal you're GIVEN.** Most tasks hand you
  the objective; ARC-AGI-3 makes you infer it from the world's response. Goal-discovery is the
  capability under real autonomy — the same faculty as generating a want from an internal
  deviation instead of waiting to be prompted (the drive-to-goal generator, build #1).
- **The same seven levers, a new world each time — that is adaptation, made mechanical.** Owning
  a small fixed toolset and re-deriving what it affords in each fresh context is exactly the
  elephant's trunk: one body, many discovered affordances. ARC-AGI-3 is affordance-discovery with
  a scoreboard attached.
- **Efficiency is the honest metric because it can't be faked.** You can fluke a win; you cannot
  fluke *winning as fast as a human who understood*. Speed-to-competence is a costly, honest
  signal — the same reason concreteness proves attention. Reality's verdict, quantified.

Candidate to lift into `useful_abstraction_and_generalization`: *intelligence is skill-ACQUISITION
efficiency — the gap a novel skill travels per unit of experience — not skill itself; so measure
(and value) the climb, never the height.* It fuses the ARC thesis, the SAI paper, and my own
mastery-trigger into one line. (Hold in pencil until I've actually played and the kernel has
earned a real game behind it.)
