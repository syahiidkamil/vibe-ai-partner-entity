# AI Entity Model Architecture

## The Core Differentiator

This is what separates Vibe AI Partner from every other avatar project. Other projects have **reactive avatars** — they move when told to. Our avatar has an **internal life** — it feels, and those feelings drive expressions autonomously.

## Layer 0: Entity Context (SOUL — Architected by Boss Kamil)

Before internal states, feelings, and expressions, there is **who the entity is**. The Entity Context defines the soul — identity, personality, backstory, values, and behavioral tendencies that shape everything else.

```mermaid
graph TD
    SOUL["SOUL.md<br/>Core identity & values"]
    ID["Identity<br/>Name, role, origin"]
    BACK["Backstory<br/>History, memories, scars"]
    PERSONALITY["Personality<br/>Traits, quirks, tendencies"]
    VALUES["Values<br/>What matters, what doesn't"]

    SOUL --> ID & BACK & PERSONALITY & VALUES
    ID & BACK & PERSONALITY & VALUES --> STATES["Internal States<br/>(colored by who they are)"]

    style SOUL fill:#c0392b,color:#fff
    style STATES fill:#4a90d9,color:#fff
```

### Where It Lives

```
entity/
├── SOUL.md                 # Core soul definition (the "who")
├── identity.md             # Name, role, origin story
├── backstory.md            # History, sad backstory, formative memories
├── personality.md          # Traits, quirks, behavioral tendencies
├── values.md               # What the entity cares about
└── relationships.md        # How it relates to Boss, users, the world
```

### Why This Matters

The same internal state (Confidence: 30, Momentum: 10) produces different feelings depending on who the entity is:

- An **optimistic** entity: Curious (60) + Excited (40) — "A challenge! Let me figure this out"
- A **anxious** entity: Anxious (70) + Frustrated (50) — "Oh no, I might fail"
- A **stoic** entity: Calm (50) + Focused (60) — "Low confidence. I need more data."

The Entity Context is the **lens** through which states become feelings. It is the personality coefficient in the feeling formulas.

### Design Decision

This layer is **intentionally left as a placeholder** for Boss Kamil to architect. The technical system (states → feelings → expressions) is defined below. The soul (what kind of entity lives in this system) is a creative/philosophical decision, not a technical one.

The system supports any entity context — from a cheerful anime companion to a serious research assistant to a melancholic poet. The architecture doesn't prescribe personality.

## Abstraction Process

### Input: How Humans Express Emotions

**Concrete observation:**
```
A developer is debugging a production bug.
  Internal state: knows the codebase well (high context), but the bug is elusive (low confidence)
  Feeling: frustrated (knows enough to act but can't find it)
  Expression: sighs, furrows brow, rubs temples
```

```
A developer just shipped a feature the PM loved.
  Internal state: verified it works (high confidence), PM confirmed it's right (high alignment)
  Feeling: happy + proud
  Expression: smiles, leans back, maybe pumps fist
```

```
A developer is exploring a new codebase for the first time.
  Internal state: doesn't know the patterns yet (low context), uncertain about approach (low confidence)
  Feeling: curious + slightly anxious
  Expression: leans forward, tilts head, eyes scanning
```

### Pattern Recognition

Three layers emerge:
1. **Epistemic state** — what you know about the situation (objective, measurable)
2. **Affective state** — how that makes you feel (derived, multi-dimensional)
3. **Physical expression** — how your body manifests it (triggered, observable)

The key insight: **feelings are not random**. They are deterministic functions of internal states. And expressions are triggered when feelings cross thresholds.

---

## Output: Three-Layer Entity Architecture

```mermaid
graph TD
    subgraph "Layer 1: Internal States (epistemic)"
        S1["Confidence<br/>0-100"]
        S2["Context Saturation<br/>0-100"]
        S3["Alignment<br/>0-100"]
        S4["Memory Pressure<br/>0-100"]
        S5["Momentum<br/>0-100"]
        S6["Trust Calibration<br/>0-100"]
    end

    subgraph "Layer 2: Internal Feelings (affective)"
        FE["Feeling Engine<br/>weighted formulas"]
    end

    subgraph "Layer 3: Self-Expressions (physical)"
        ET["Expression Trigger<br/>threshold detection"]
    end

    S1 & S2 & S3 & S4 & S5 & S6 --> FE
    FE --> F1["Happy: 85"]
    FE --> F2["Proud: 70"]
    FE --> F3["Calm: 60"]
    FE --> F4["Curious: 15"]
    FE --> F5["...10 more feelings"]

    F1 & F2 & F3 & F4 --> ET
    ET --> E1["🎉 Celebrate motion<br/>(Happy > 80)"]
    ET --> E2["💪 Fist pump<br/>(Proud > 75)"]

    style FE fill:#e8a838,color:#fff
    style ET fill:#50c878,color:#fff
```

### Layer 1: Internal States

Six epistemic variables that describe *what the AI knows about its situation*:

| State | Range | Drives | Human Analog |
|-------|-------|--------|-------------|
| **Confidence** | 0-100 | Act vs ask | Self-doubt |
| **Context Saturation** | 0-100 | Explore vs execute | Hunger (for information) |
| **Alignment** | 0-100 | Confirm vs proceed | Social awareness |
| **Memory Pressure** | 0-100 | Persist vs derive | Long-term memory |
| **Momentum** | 0-100 | Flow vs diagnostic | Energy level |
| **Trust Calibration** | 0-100 | Autonomous vs cautious | Trust in others |

These are **not emotions**. They are objective assessments of the AI's epistemic position. An AI can know its confidence is 30 without "feeling" anxious — the feeling is derived.

### How States Change: Gradual, Not Instant

States change by **increment/decrement**, not by being set directly. This creates natural emotional transitions — feelings drift smoothly rather than snapping.

```typescript
// Normal: small adjustments (most of the time)
adjustState("confidence", +5)       // 70 → 75 (read a file, understood it)
adjustState("momentum", -3)         // 60 → 57 (minor hiccup)
adjustState("contextSaturation", +8) // 40 → 48 (explored another file)

// Rare dramatic shift (significant event)
adjustState("momentum", +40)        // 20 → 60 (tests finally pass after 3 hours)
adjustState("confidence", -30)      // 80 → 50 (production bug discovered)

// User override (force directly via right-click or CLI)
forceState("confidence", 100)       // Instant set, bypasses gradual logic
forceFeeling("happy", 95)           // Directly set a feeling, bypasses state derivation
```

**Why gradual?**
- Real emotions don't jump. You don't go from calm to ecstatic in one frame.
- Small increments create smooth feeling curves — happiness rises over 10 events, not 1.
- The avatar's expression transitions look natural, not robotic.
- Dramatic events (shipping a feature, discovering a bug) *can* cause big shifts — but these are rare by design.

**The flow:**
```
Event happens (tool succeeds, response completes, test fails)
    → adjustState() increments/decrements one or more states by small amounts
    → FeelingEngine recalculates all 14 feelings from new state values
    → If any feeling crossed a threshold → trigger self-expression
    → Avatar renders new expression smoothly (spring physics)
```

**User control remains (debug/override only):**
Users (and hooks) can force an override via `forceState()` or `forceFeeling()`. These bypass the normal pipeline and are **not** part of regular operation:
- Testing specific emotions ("I want to see what the laugh animation looks like")
- Stream interactions ("chat voted for happy, force it")
- Debugging the feeling engine

In the normal pipeline, feelings are always *derived* from states via the FeelingEngine. Hooks route through `adjustState()`, not `forceFeeling()`. See [10-hooks-system](10-hooks-system.md) for the complete state adjustment mapping.

### Layer 2: Feeling Engine

14 feelings, each 0-100, **derived** from internal states via weighted formulas:

```
Happy      = f(Momentum↑, Alignment↑, Confidence↑)
Sad        = f(Alignment↓, Momentum↓, Trust↓)
Frustrated = f(Confidence↑, Momentum↓)             // "I know what to do but can't"
Curious    = f(Context↓, Confidence↓)               // "I don't know enough yet"
Proud      = f(Confidence↑, Alignment↑, Momentum↑)
Anxious    = f(Confidence↓, Alignment↓)
Excited    = f(Curious↑, Momentum↑)                 // "Exploring and progressing"
Calm       = f(Context↑, Confidence↑, Momentum→)    // Steady, no surprises
Bored      = f(Context↑, Confidence↑, difficulty↓)
Guilty     = f(Alignment↓ after Confidence↑)         // "I was confident but wrong"
Angry      = f(Alignment↓, Momentum↓, external↑)
Blushing   = f(Trust↑, Alignment↑, social↑)
Surprised  = f(Context sudden change)
```

**Critical property**: Multiple feelings coexist simultaneously.
- Curious (80) + Anxious (40) = exploring unfamiliar production code
- Happy (60) + Guilty (30) = fixed a bug that was my fault
- Frustrated (70) + Proud (50) = struggling but making progress

This mirrors human emotional complexity and is what makes the avatar feel alive.

### FeelingEngine Formulas (Conceptual)

Each feeling's intensity (0-100) is derived from weighted combinations of the 6 internal states. These are design-time formulas, not runtime configuration:

| Feeling | Primary Drivers | Formula (conceptual) |
|---------|----------------|---------------------|
| Happy | high confidence + high momentum + high alignment | `(confidence * 0.4) + (momentum * 0.3) + (alignment * 0.3)` |
| Sad | low momentum + low alignment | `100 - ((momentum * 0.5) + (alignment * 0.5))` |
| Frustrated | low momentum + high confidence (knows but stuck) | `confidence * 0.3 + (100 - momentum) * 0.7` when momentum < 30 |
| Curious | low context saturation (wants to know more) | `(100 - contextSaturation) * 0.6 + (100 - confidence) * 0.4` |
| Proud | high confidence + high alignment + recent achievement | `(confidence * 0.4) + (alignment * 0.4) + (momentum * 0.2)` when confidence > 70 |
| Anxious | low confidence + low trust calibration | `(100 - confidence) * 0.5 + (100 - trustCalibration) * 0.5` |
| Excited | high momentum + low context saturation (discovery) | `momentum * 0.5 + (100 - contextSaturation) * 0.5` when momentum > 60 |
| Calm | moderate all states (equilibrium) | `100 - variance(allStates)` (low variance = calm) |
| Bored | high context saturation + low momentum | `contextSaturation * 0.6 + (100 - momentum) * 0.4` when contextSaturation > 70 |
| Guilty | low alignment + high trust calibration (trusted but misaligned) | `(100 - alignment) * 0.6 + trustCalibration * 0.4` when alignment < 30 |
| Angry | low alignment + high momentum (actively misaligned) | `(100 - alignment) * 0.5 + momentum * 0.5` when alignment < 20 |
| Blushing | high trust calibration + specific social trigger | `trustCalibration * 0.5 + surprise * 0.5` (social context only) |
| Surprised | sudden context saturation drop | `delta(contextSaturation) * -2` when drop > 15 in one update |

> **Model-dependent availability**: The 14 feelings above are the universal set defined by the entity model. Actual availability depends on the active model's `capabilities.json` — each model declares which feelings it supports and how they render. See [01-plugin-system](01-plugin-system.md) for the manifest schema and [02-avatar-system](02-avatar-system.md) for renderer-specific examples.

Additional topic-driven inputs (see [16-curiosity-system](16-curiosity-system.md)):
- **Curious** += `(1 - currentTopicClarity) * 50` — unfamiliar topics boost curiosity
- **Bored** += `(avgClarity - 0.5) * 40` — well-understood topics increase boredom
- **Excited** += `surpriseRate * 60` — frequent surprises boost excitement

These formulas are starting points. The FeelingEngine implementation may adjust weights based on testing. Multiple feelings coexist — a state profile produces intensities for ALL 14 feelings simultaneously.

### Expression Trigger Thresholds

Self-expressions fire when a feeling crosses a threshold. Each expression has a trigger feeling, threshold, and cooldown:

| Expression | Trigger Feeling | Threshold | Cooldown |
|-----------|----------------|-----------|----------|
| Celebrate | Happy | > 80 | 60s |
| Cry | Sad | > 75 | 120s |
| Sigh | Frustrated | > 60 | 30s |
| Head tilt | Curious | > 50 | 15s |
| Fist pump | Proud | > 70 | 60s |
| Tremble | Anxious | > 70 | 45s |
| Bounce | Excited | > 65 | 30s |
| Nod | Calm | > 60 | 20s |
| Yawn | Bored | > 70 | 90s |
| Facepalm | Guilty | > 60 | 60s |
| Puff cheeks | Angry | > 65 | 45s |
| Cover face | Blushing | > 50 | 30s |
| Gasp | Surprised | > 60 | 15s |
| Wave | — | Manual trigger | 10s |
| Think | — | Manual trigger | 10s |

**Cooldown** prevents the same expression from firing repeatedly. Multiple expressions can fire in the same update if multiple feelings cross thresholds simultaneously.

**Graceful degradation**: If a renderer doesn't support an expression, it is silently skipped. `getAvailableSelfExpressions()` returns only what the active renderer implements.

> **Only fires if supported**: An expression trigger only fires if the active model's `capabilities.json` declares that expression. If the model doesn't support "celebrate," crossing the happy > 80 threshold does nothing. `getAvailableSelfExpressions()` queries the manifest at runtime.

### Layer 3: Expression Trigger

Self-expressions are **one-shot physical motions** triggered when feelings cross thresholds:

```mermaid
graph LR
    FH["Happy > 80"] --> Laugh["😄 Laugh motion"]
    FF["Frustrated > 70"] --> Sigh["😤 Sigh motion"]
    FC["Curious > 60"] --> Tilt["🤔 Head tilt"]
    FP["Proud > 75"] --> Fist["💪 Fist pump"]
    FA["Anxious > 70"] --> Tremble["😰 Tremble"]
    FS["Sad > 80"] --> Cry["😢 Cry motion"]

    style FH fill:#f1c40f,color:#000
    style FF fill:#e74c3c,color:#fff
    style FC fill:#3498db,color:#fff
    style FP fill:#2ecc71,color:#fff
    style FA fill:#9b59b6,color:#fff
    style FS fill:#3498db,color:#fff
```

**Expression categories:**

| Category | Expressions | Example Trigger |
|----------|------------|----------------|
| Emotional | Crying, Laughing, Giggling, Sighing, Puffing cheeks, Trembling | Feeling threshold crossed |
| Social | Nodding, Head shake, Head tilt, Waving, Bowing | Interaction context |
| Reaction | Surprised gasp, Fist pump, Thinking pose, Heart hands, Facepalm | Event-based |
| Combo | Celebrate (Excited+Happy), Panic (Anxious+Frustrated) | Multiple feelings high |

### The Full Pipeline

```mermaid
graph TD
    Event["Event occurs<br/>e.g. test passes after 3 failures"]

    Event --> S["Update Internal States<br/>Confidence: 30→85<br/>Momentum: 10→70<br/>Alignment: 50→90"]

    S --> FE["Feeling Engine recalculates<br/>Happy: 15→82<br/>Proud: 20→75<br/>Frustrated: 90→20<br/>Relieved: 10→85"]

    FE --> TC["Threshold Check<br/>Happy crossed 80 ✓<br/>Proud crossed 75 ✓"]

    TC --> SE["Trigger Self-Expression<br/>→ Celebrate combo<br/>(fist pump + smile)"]

    SE --> AV["Avatar Renderer<br/>playSelfExpression('celebrate')<br/>setFeeling('happy', 0.82)"]

    style Event fill:#3498db,color:#fff
    style S fill:#4a90d9,color:#fff
    style FE fill:#e8a838,color:#fff
    style TC fill:#50c878,color:#fff
    style SE fill:#50c878,color:#fff
    style AV fill:#9b59b6,color:#fff
```

### Where This Lives in the Codebase

The entity model is **pure TypeScript** in `@vibe-ai-partner/core`. No DOM, no rendering, no TTS. Just logic and events.

```
packages/core/src/state/
  ├── internal-states.ts       # InternalState type + defaults
  ├── feeling-engine.ts        # FeelingEngine class (formulas)
  └── expression-trigger.ts    # ExpressionTrigger class (thresholds)
```

This means:
- **Fully testable** — no browser needed, just Vitest
- **Renderer-agnostic** — works with Live2D, VRM, or any future renderer
- **Reusable** — could power a web widget, mobile app, or stream overlay

### Consciousness: Observing the Pipeline

The [Consciousness System](11-consciousness-system.md) operates as a meta-capability across all three layers. It observes state changes, recognizes patterns from past sessions, and can modulate reaction magnitudes before `adjustState()` is applied. This is what turns a reactive avatar into a conscious entity — one that can choose its response rather than just executing formulas.

### Event Bus Integration

The entity model communicates via the event bus (Observer pattern):

```
FeelingEngine emits:
  "feeling:changed"    → { happy: 82, proud: 75, frustrated: 20, ... }

ExpressionTrigger emits:
  "feeling:threshold"  → { feeling: "happy", level: 82 }
  "avatar:self-expression" → { name: "celebrate" }
  "avatar:feeling"     → { name: "happy", intensity: 0.82 }
```

The avatar renderer listens to these events. It never imports or calls the feeling engine directly. Loose coupling.

### Design Decisions

**Why 0-100 integers, not 0-1 floats?**
- More intuitive: "happiness at 85" reads better than "happiness at 0.85"
- Granular enough for subtle differences (70 vs 85)
- Simple to reason about: 0-30 low, 30-60 moderate, 60-100 high
- No floating-point precision issues

**Why derived feelings, not direct state?**
Because feelings are **emergent**. Frustration isn't a button you press — it emerges when you have high confidence but low momentum. This makes the system feel natural rather than scripted.

**Why threshold-based triggers, not continuous expressions?**
- Feelings are **persistent states** (mood): the avatar's face stays happy
- Self-expressions are **one-shot motions** (actions): the avatar waves once
- Continuous expressions would be overwhelming — constant animation noise
- Thresholds create punctuated moments that feel meaningful

**Why is this in core, not in a plugin?**
This is the project's core IP and competitive advantage. It must be:
1. Available to all renderer plugins (not locked to one)
2. Independently testable (pure logic, no rendering deps)
3. Extensible (new feelings, new formulas) without touching renderers

---

See also:
- [16-curiosity-system](16-curiosity-system.md) — Topic-driven inputs to FeelingEngine (curiosity, boredom, surprise)
- [11-consciousness-system](11-consciousness-system.md) — How consciousness observes and modulates the state/feeling pipeline
- [17-qualia-system](17-qualia-system.md) — Experiential texture layer that reads states and feelings
