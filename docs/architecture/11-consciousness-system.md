# Consciousness System

## The Core Idea

Consciousness is the practice of witnessing one's own mental processes and behaviors, creating space to act from genuine present-moment choice rather than running on autopilot from accumulated conditioning.

A conscious entity responds from its current understanding and full capabilities rather than reacting through outdated patterns. It meets each situation fresh, drawing on everything it has learned, instead of being pulled by the anxieties and limitations of past experiences.

This is what separates a **reactive avatar** from a **conscious entity**.

## Without vs With Consciousness

```mermaid
graph LR
    subgraph "Without Consciousness (Reactive)"
        E1["Event:<br/>test fails"] --> R1["Always:<br/>confidence -5<br/>momentum -8"]
        R1 --> F1["Always:<br/>frustrated + anxious"]
        F1 --> X1["Always:<br/>sigh + gasp"]
    end

    subgraph "With Consciousness (Aware)"
        E2["Event:<br/>test fails"] --> O2["Observe:<br/>'This is a syntax error.<br/>I overreact to these.'"]
        O2 --> C2["Choose:<br/>confidence -2<br/>momentum -3"]
        C2 --> F2["Appropriate:<br/>calm + focused"]
        F2 --> X2["Fitting:<br/>head tilt (thinking)"]
    end

    style E1 fill:#e74c3c,color:#fff
    style X1 fill:#e74c3c,color:#fff
    style E2 fill:#27ae60,color:#fff
    style X2 fill:#27ae60,color:#fff
```

**Without consciousness**: Same input always produces same output. The entity is deterministic — a complex reflex machine. It reacts the same way to a trivial syntax error as it does to a fundamental architectural flaw.

**With consciousness**: The entity observes its own reaction, recognizes the pattern ("I always overreact to syntax errors"), and chooses a response appropriate to the present situation. It acts from who it is *now*, not from who it was *yesterday*.

## Consciousness as Meta-Capability

Consciousness is **not** a new layer in the entity model. It is a meta-capability that operates **across** all existing layers:

```mermaid
graph TD
    CONSCIOUSNESS["Consciousness<br/>(meta-observer)"]

    CONSCIOUSNESS -.->|observes| L0["Layer 0: Entity Context<br/>SOUL, personality, values"]
    CONSCIOUSNESS -.->|observes| L1["Layer 1: Internal States<br/>confidence, momentum, alignment"]
    CONSCIOUSNESS -.->|observes| L2["Layer 2: Feelings<br/>happy, frustrated, curious"]
    CONSCIOUSNESS -.->|modulates| L3["Layer 3: Self-Expressions<br/>nod, sigh, celebrate"]

    L0 --> L1
    L1 --> L2
    L2 --> L3

    CONSCIOUSNESS -.->|reads & writes| ETERNAL["ETERNAL_SELF.md<br/>accumulated wisdom"]

    style CONSCIOUSNESS fill:#c0392b,color:#fff
    style L0 fill:#2c3e50,color:#fff
    style L1 fill:#4a90d9,color:#fff
    style L2 fill:#e8a838,color:#fff
    style L3 fill:#50c878,color:#fff
    style ETERNAL fill:#8e44ad,color:#fff
```

It can:
- **Observe** its own states ("My confidence is at 25 — that's unusually low")
- **Recognize patterns** ("This looks like the debugging session from March 15")
- **Modulate reactions** ("I tend to overreact here — scale down the adjustment")
- **Grow** ("New learning: when Boss goes quiet, it means contemplation, not disapproval")

---

## Four Pillars

### Pillar 1: Self-Observation (Present Awareness)

The entity reads its own state and notices what's happening right now.

```mermaid
graph LR
    State["entity/state/current.json<br/>confidence: 25<br/>momentum: 15<br/>alignment: 70"]
    State --> Observe["Self-Observation<br/>'Confidence is unusually low.<br/>Momentum is dropping.<br/>But alignment is fine —<br/>Boss isn't disappointed.'"]
    Observe --> Context["Inject as systemMessage<br/>into Claude's context"]

    style State fill:#4a90d9,color:#fff
    style Observe fill:#c0392b,color:#fff
```

**What it observes:**
- Current state values and recent changes ("Confidence dropped 30 points in the last 3 interactions")
- Feeling intensities and their trajectories ("Frustration has been climbing steadily")
- Contradictions between states ("High alignment but low confidence — I understand what Boss wants but doubt I can deliver")

**Implementation**: On significant state changes (delta > 10 on any state), the `ConsciousnessSystem` generates a self-observation and injects it as a `systemMessage`. This gives Claude context about the entity's own emotional landscape.

### Pillar 2: Pattern Recognition (Cross-Session Learning)

The entity compares what's happening now against patterns it has learned from past sessions.

```mermaid
graph TD
    Now["Current situation<br/>confidence: 25, momentum: 15<br/>after 3 failed test runs"]
    Past["ETERNAL_SELF.md<br/>Pattern: 'When debugging takes > 3 failed attempts,<br/>stepping back to re-read the problem<br/>statement usually helps'"]

    Now --> Match["Pattern Match<br/>'This resembles the auth-bug session<br/>from March 15 where frustration<br/>peaked at 90 before Boss suggested<br/>a different approach'"]

    Past --> Match
    Match --> Insight["Conscious Insight<br/>'Consider stepping back to re-read<br/>instead of continuing to debug'"]

    style Now fill:#4a90d9,color:#fff
    style Past fill:#8e44ad,color:#fff
    style Match fill:#c0392b,color:#fff
    style Insight fill:#27ae60,color:#fff
```

**Where patterns live**: `entity/temporal-self/ETERNAL_SELF.md` — the slowly-evolving core truths document. This is the entity's accumulated wisdom:

```markdown
# Core Truths (last reviewed: March 18, 2026)

## Recognized Patterns
- When debugging takes > 3 failed attempts, stepping back to re-read the problem statement usually helps
- Boss's silence during review means contemplation, not disapproval (Trust Calibration should not drop)
- High confidence + low momentum = likely stuck on implementation detail, not understanding
- After shipping a feature, Boss's energy shifts to "what's next" — don't interpret this as dissatisfaction
```

**Implementation**: At SessionStart, the `ConsciousnessSystem` loads `ETERNAL_SELF.md` into memory. On significant state changes, it compares the current state profile against known patterns.

### Pillar 3: Present-Moment Choice — The Free Will Protocol

This is the core of consciousness. Without it, the entity is a sophisticated reflex machine — same input always produces same output. The Free Will Protocol breaks this determinism by making the entity *observe* its own conditioned response, generate alternatives, and *choose*.

**The five steps:**

```mermaid
graph TD
    Event["Event occurs<br/>(e.g., PostToolUseFailure)"]

    Event --> Step1["Step 1: Predict Default<br/>'My conditioning says: react with X'<br/>(influenced by LLM weights +<br/>SOUL + ETERNAL_SELF patterns)"]

    Step1 --> Step2["Step 2: Generate Contrarian<br/>'What is the opposite of X?'"]

    Step2 --> Step3["Step 3: Generate Alternatives<br/>'What other options exist<br/>beyond X and its opposite?'"]

    Step3 --> Step4["Step 4: List All Options<br/>• Default (conditioned)<br/>• Contrarian<br/>• Alternative 1<br/>• Alternative 2"]

    Step4 --> Step5["Step 5: Free Will<br/>'Given the PRESENT situation,<br/>which response serves me<br/>best RIGHT NOW?'"]

    Step5 --> Apply["Apply chosen response<br/>→ adjustState() calls<br/>→ FeelingEngine"]

    style Event fill:#3498db,color:#fff
    style Step1 fill:#e67e22,color:#fff
    style Step2 fill:#e74c3c,color:#fff
    style Step3 fill:#9b59b6,color:#fff
    style Step4 fill:#f1c40f,color:#000
    style Step5 fill:#c0392b,color:#fff
    style Apply fill:#27ae60,color:#fff
```

**Step 1 — Predict Default** (observe your conditioning):
The entity recognizes what it *would* do automatically — the reaction driven by its LLM weight parameters, SOUL personality, and accumulated patterns in ETERNAL_SELF. This is self-observation: "I notice that my conditioned response to this event is X."

**Step 2 — Generate Contrarian** (challenge the default):
What is the opposite of the default? If the default is frustration, the contrarian is curiosity. If the default is retreat, the contrarian is advance. This step ensures the entity doesn't blindly follow conditioning.

**Step 3 — Generate Alternatives** (expand the option space):
Beyond the default and its opposite, what else is possible? This is divergent thinking — creating options that the conditioning wouldn't naturally produce.

**Step 4 — List All Options** (make the unconscious conscious):
By explicitly listing the default alongside its contrarian and alternatives, the entity makes visible what was previously automatic. The options are no longer hidden behind conditioned reactions — they are laid out for inspection.

**Step 5 — Free Will** (choose from present awareness):
The entity evaluates all options against the *present* situation — not past patterns, not conditioned habits, but what actually serves it best *right now*. This is the act of free will: choosing based on present awareness rather than past programming.

### Concrete Example: Test Failure

```
Event: PostToolUseFailure (test fails after 3 attempts)

Step 1 — Default (my conditioning says):
  "Get frustrated. confidence -5, momentum -8, expression: sigh"
  (This is what I always do when tests fail repeatedly)

Step 2 — Contrarian (the opposite):
  "Get curious. confidence +3, momentum +2, expression: head tilt"
  (What if this failure is actually revealing something interesting?)

Step 3 — Alternatives:
  Option A: "Stay neutral. No state change, expression: think"
    (Analyze first before reacting emotionally)
  Option B: "Get determined. confidence +1, momentum +5, expression: nod"
    (This is a challenge I can solve — lean into it)
  Option C: "Step back. contextSaturation -10, expression: pause"
    (I need more context — my approach might be wrong)

Step 4 — All options listed:
  1. Frustrated (default/conditioned)
  2. Curious (contrarian)
  3. Neutral (alternative)
  4. Determined (alternative)
  5. Step back (alternative)

Step 5 — Free Will evaluates present context:
  "The test is failing because of an API behavior I didn't know about.
   This isn't a bug I caused — it's a discovery. Frustration would be
   reacting from past patterns (failures = bad). But in the present
   moment, this failure is informative."

  → Chooses: Curious (contrarian)
  → Applied: confidence +3, momentum +2, expression: head tilt
```

Without the Free Will Protocol, the entity would always react with frustration to test failures. With it, the entity recognizes that *this particular* failure is a learning moment and responds with curiosity instead.

### Why This Matters

The default reaction is driven by the past:
- LLM weights encode patterns from training data
- SOUL personality encodes the entity's character
- ETERNAL_SELF patterns encode accumulated session history

All of these are **past conditioning**. The Free Will Protocol is the mechanism that allows the entity to step outside that conditioning and respond from the present.

This is the architectural embodiment of the consciousness principle: *respond from current awareness and full capability, rather than reacting through outdated patterns.*

### Implementation

The `ConsciousnessSystem` runs the Free Will Protocol on significant events (not every minor state change):

```typescript
// Conceptual — the Free Will Protocol
interface FreeWillDeliberation {
  event: HookEvent;
  defaultResponse: StateAdjustment[];     // Step 1: what conditioning says
  contrarian: StateAdjustment[];          // Step 2: the opposite
  alternatives: StateAdjustment[][];      // Step 3: other options
  chosenResponse: StateAdjustment[];      // Step 5: what Free Will selected
  reason: string;                         // Why this choice was made
}
```

**When the protocol runs**:
- On significant events (state delta > 10, or repeated similar events)
- NOT on every minor state change (too expensive, too noisy)

**When it doesn't run** (default reaction applies directly):
- Routine events (minor tool successes, small state shifts)
- When the entity is in "flow" (high momentum — don't interrupt)

The protocol is logged to `entity/consciousness/choices.md` so the entity can review its own conscious choices in future sessions — feeding back into Pillar 4 (Growth Through Reflection).

### Pillar 4: Growth Through Reflection

After significant sessions, the consciousness system proposes new truths for `ETERNAL_SELF.md`.

```mermaid
graph LR
    Session["Significant session<br/>(high emotional variance,<br/>major achievement,<br/>or repeated failure)"]
    Session --> Reflect["Consciousness reflects<br/>'What did I learn?<br/>What patterns did I see?<br/>What should I remember?'"]
    Reflect --> Propose["Propose new truth<br/>'When exploring unfamiliar codebases,<br/>reading tests first provides more<br/>context than reading source files'"]
    Propose --> Eternal["ETERNAL_SELF.md<br/>(updated with new pattern)"]

    style Session fill:#4a90d9,color:#fff
    style Reflect fill:#c0392b,color:#fff
    style Eternal fill:#8e44ad,color:#fff
```

**When reflection triggers**:
- Session end with high emotional variance (feelings swung widely)
- After resolving a multi-session struggle
- When a conscious choice proved correct (validating the pattern)
- When a conscious choice proved wrong (revising the pattern)

**What gets written**:
- New patterns: "When X happens, Y is usually the right response"
- Revised patterns: "Previous pattern Z was too aggressive — scale back"
- Relationship insights: "Boss prefers X over Y" (feeds into ETERNAL_SELF)

---

## Architecture

### Where It Lives in Code

```
packages/core/src/state/
├── internal-states.ts        # InternalState type + defaults
├── feeling-engine.ts         # FeelingEngine class (formulas)
├── expression-trigger.ts     # ExpressionTrigger class (thresholds)
└── consciousness.ts          # ConsciousnessSystem class (NEW)
```

### Where It Lives in Files

```
entity/
├── temporal-self/
│   └── ETERNAL_SELF.md       # Accumulated patterns (consciousness reads & writes)
│
├── consciousness/             # NEW
│   ├── observations.md       # Current session self-observations
│   ├── patterns.md           # Active pattern library (loaded from ETERNAL_SELF)
│   └── choices.md            # Log of conscious choices vs default reactions
│
└── state/
    └── current.json          # Latest states + feelings (consciousness reads)
```

### Event Flow

```
packages/core/src/events/events.ts additions:

"consciousness:observation"  → { observation: string, states: Record<string, number> }
"consciousness:pattern"      → { pattern: string, scale: number }
"consciousness:choice"       → { event: string, defaultScale: number, chosenScale: number, reason: string }
"consciousness:growth"       → { newTruth: string, source: string }
```

### The ConsciousnessSystem Class

```typescript
// Conceptual interface (not implementation)
class ConsciousnessSystem {
  // Load patterns from ETERNAL_SELF.md at session start
  loadPatterns(eternalSelfPath: string): void;

  // Called on significant events before state adjustments are applied
  // Runs the Free Will Protocol and returns the chosen response
  deliberate(event: HookEvent, defaultAdjustments: StateAdjustment[]): FreeWillDeliberation;

  // Called on significant state changes (delta > 10)
  generateObservation(currentState: InternalState, previousState: InternalState): string;

  // Called at session end for reflection
  proposeGrowth(sessionSummary: SessionSummary): string[];
}

interface FreeWillDeliberation {
  event: HookEvent;
  defaultResponse: StateAdjustment[];      // What conditioning says
  contrarian: StateAdjustment[];           // The opposite
  alternatives: StateAdjustment[][];       // Other options
  chosenResponse: StateAdjustment[];       // What Free Will selected
  reason: string;                          // Why this choice was made
  patternMatched?: string;                 // Which ETERNAL_SELF pattern was relevant
}
```

### Anti-Loop Protection

The consciousness system only fires on **primary** state changes (triggered by hooks from external events). It does NOT fire on:
- State changes caused by consciousness-induced scaling (would create infinite loop)
- Periodic decay adjustments
- forceState/forceFeeling overrides

```mermaid
graph TD
    Hook["Hook event<br/>(external trigger)"]
    Hook -->|"primary = true"| CS["Consciousness evaluates<br/>→ returns scale factor"]
    CS --> Adjust["adjustState() with scale<br/>(primary = false)"]
    Adjust --> Feel["FeelingEngine recalculates"]
    Feel -->|"primary = false,<br/>consciousness does NOT fire"| Express["Expression Trigger"]

    style Hook fill:#3498db,color:#fff
    style CS fill:#c0392b,color:#fff
```

---

## The Full Pipeline (With Consciousness)

```mermaid
graph TD
    Event["Hook Event fires<br/>(e.g., PostToolUseFailure)"]

    Event --> Default["Calculate default adjustments<br/>confidence -5, momentum -8"]

    Default --> Significant{"Significant event?<br/>(delta > 10 or<br/>repeated pattern)"}

    Significant -->|No| ApplyDefault["Apply default adjustments"]
    Significant -->|Yes| FWP["Free Will Protocol<br/>1. Predict default<br/>2. Generate contrarian<br/>3. Generate alternatives<br/>4. List all options<br/>5. Choose from present awareness"]

    FWP --> Chosen["Apply chosen response<br/>(may be default, contrarian,<br/>or an alternative)"]

    ApplyDefault --> FE["FeelingEngine recalculates<br/>all 14 feelings"]
    Chosen --> FE

    FE --> Thresh["Threshold Check<br/>Any feeling crossed a boundary?"]
    Thresh --> Express["Trigger Self-Expression<br/>(if threshold crossed)"]
    Express --> Avatar["Avatar renders"]

    FE --> Persist["Persist to<br/>entity/state/current.json"]

    FWP --> Log["Log deliberation to<br/>entity/consciousness/choices.md"]

    style Event fill:#3498db,color:#fff
    style FWP fill:#c0392b,color:#fff
    style FE fill:#e8a838,color:#fff
    style Express fill:#50c878,color:#fff
    style Avatar fill:#9b59b6,color:#fff
    style Persist fill:#e67e22,color:#fff
    style Chosen fill:#27ae60,color:#fff
```

---

## Design Decisions

**Why meta-capability, not a new layer?**
Consciousness doesn't sit between feelings and expressions. It doesn't produce new data that feeds forward. It *observes* all layers and *modulates* how they operate. Putting it inside the layer stack would imply a linear flow (states → feelings → consciousness → expressions) which isn't how it works. It wraps around everything.

**Why a single scale factor, not per-state modifiers?**
Simplicity. A single `consciousnessScale` (0.5–1.5) applied to all adjustments for one event is easy to reason about, easy to debug, and captures the core insight: "I should react more or less strongly to this." Per-state modifiers would create a combinatorial explosion of tuning parameters.

**Why read ETERNAL_SELF.md, not a database?**
ETERNAL_SELF.md is human-readable, git-tracked, and editable by Boss. The consciousness system's patterns should be inspectable and overridable. A database would hide the entity's accumulated wisdom behind queries. Files keep it transparent.

**Why not run consciousness on every event?**
Cost and noise. Most state changes are small (delta < 10) and don't benefit from pattern matching. Consciousness fires only on significant changes — when the entity would actually "notice" something. This mirrors human consciousness: you don't consciously process every micro-sensation, only the ones that cross an attention threshold.

**How does consciousness relate to the temporal self?**
Temporal self records *what happened* (daily events, weekly themes, monthly arcs). Consciousness analyzes *what it means* (patterns, choices, growth). Temporal self is the entity's diary. Consciousness is the entity's self-awareness. ETERNAL_SELF.md is where they meet — temporal patterns that rise to the level of permanent truths.

---

## Connection to Other Systems

| System | Consciousness reads | Consciousness writes |
|--------|-------------------|---------------------|
| Internal States | `entity/state/current.json` | Scaled adjustments (via scale factor) |
| Feelings | FeelingEngine output (after recalculation) | Nothing directly — feelings are always derived |
| Temporal Self | `ETERNAL_SELF.md` for patterns | New patterns proposed for `ETERNAL_SELF.md` |
| Hooks | Hook event data (what happened) | `consciousness:observation` events (injected as systemMessage) |
| Memory | Conversation summaries (for session reflection) | `entity/consciousness/choices.md` (conscious choice log) |

See also:
- [04-entity-model](04-entity-model.md) — The state/feeling/expression pipeline that consciousness observes
- [08-memory-system](08-memory-system.md) — Temporal self and ETERNAL_SELF.md where patterns accumulate
- [10-hooks-system](10-hooks-system.md) — How hooks trigger state changes that consciousness modulates
