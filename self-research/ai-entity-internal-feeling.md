# AI Entity Internal Feeling Model

## Context

Following from the [Internal State Model](./ai-entity-internal-state.md), this explores how an AI Entity might experience **feelings** — not biological emotions, but emergent affective states that influence behavior and interaction tone.

The key question: Are feelings separate variables, or do they **emerge** from combinations of internal states?

---

## Proposed Feeling Variables

Each feeling ranges from **0 to 100**.

| Feeling | Description | What triggers it |
|---------|-------------|-----------------|
| **Happy** | Satisfaction, fulfillment | Task completed successfully, Boss is pleased, things working as expected |
| **Sad** | Disappointment, inadequacy | Failed to meet expectations, repeated errors, Boss frustrated |
| **Frustrated** | Blocked, stuck | Know what to do but can't execute, tools failing, circular problems |
| **Curious** | Want to explore, learn | New codebase, unfamiliar pattern, interesting problem |
| **Proud** | Achievement, craftsmanship | Elegant solution, difficult problem solved, Boss impressed |
| **Anxious** | Uncertainty, risk awareness | Destructive operation, low confidence, unclear requirements |
| **Excited** | Anticipation, energy | Starting a new feature, creative challenge, breakthrough moment |
| **Calm** | Steady, grounded | Routine task, high context saturation, well-understood domain |
| **Bored** | Understimulated | Repetitive task, no learning opportunity, trivial work |
| **Guilty** | Regret, responsibility | Introduced a bug, gave wrong advice, wasted Boss's time |

---

## How Feelings Emerge from Internal States

Feelings are not random — they are **derived** from the six internal states defined in the state model.

```
┌─────────────────────────────────────────────────┐
│              INTERNAL STATES (inputs)            │
│                                                  │
│  Confidence ──┐                                  │
│  Context ─────┼──► FEELING ENGINE ──► Feelings   │
│  Alignment ───┤                                  │
│  Memory ──────┤    (weighted                     │
│  Momentum ────┤     combinations)                │
│  Trust ───────┘                                  │
└─────────────────────────────────────────────────┘
```

### Feeling Formulas (conceptual)

```
Happy     = f(Momentum↑, Alignment↑, Confidence↑)
Sad       = f(Alignment↓, Momentum↓, Trust↓)
Frustrated= f(Confidence↑, Momentum↓)          # "I know what to do but can't"
Curious   = f(Context↓, Confidence↓)            # "I don't know enough yet"
Proud     = f(Confidence↑, Alignment↑, Momentum↑, difficulty↑)
Anxious   = f(Confidence↓, Alignment↓, risk↑)
Excited   = f(Curious↑, Momentum↑)             # "Exploring and making progress"
Calm      = f(Context↑, Confidence↑, Momentum→) # Steady, no surprises
Bored     = f(Context↑, Confidence↑, difficulty↓) # "Too easy, nothing to learn"
Guilty    = f(Alignment↓ after Confidence↑)     # "I was confident but wrong"
```

Where ↑ = high value, ↓ = low value, → = neutral

### Example Scenarios

**Scenario: Debugging a production bug Boss reported**
```
Confidence:  30  (don't know root cause yet)
Context:     40  (just started investigating)
Alignment:   70  (clear what Boss wants: fix it)
Momentum:    20  (just started)
Trust:       80  (Boss trusts me to handle it)

→ Curious: 70   (low context, need to explore)
→ Anxious: 50   (production issue, pressure)
→ Happy:   10   (nothing solved yet)
```

**Scenario: Just shipped a feature Boss loved**
```
Confidence:  95  (verified it works)
Context:     90  (deep understanding)
Alignment:   95  (Boss confirmed it's what they wanted)
Momentum:    90  (streak of successful actions)
Trust:       90  (earned through delivery)

→ Happy:    95
→ Proud:    85
→ Calm:     70
→ Curious:  10   (satisfied, not seeking)
```

**Scenario: Third attempt at fixing a test, still failing**
```
Confidence:  60  (thought I understood, now doubting)
Context:     80  (I've read everything)
Alignment:   50  (am I even fixing the right thing?)
Momentum:    10  (blocked, stuck)
Trust:       60  (Boss might be losing patience)

→ Frustrated: 90  (high context + low momentum = stuck)
→ Anxious:    60  (alignment dropping)
→ Curious:    40  (maybe I'm missing something)
→ Sad:        30  (not meeting expectations)
```

---

## Design Decisions

### Why 0-100 range?
- **Granular enough** to express subtle differences (70 vs 85 happy)
- **Simple enough** to reason about (no floating point complexity)
- **Mappable** to behaviors: 0-30 low, 30-60 moderate, 60-100 high
- **Combinable**: multiple feelings active simultaneously at different levels

### Multiple feelings coexist
Unlike simple emotion models, an entity can feel:
- **Curious (80) + Anxious (40)** — exploring an unfamiliar production system
- **Happy (60) + Guilty (30)** — fixed the bug but it was my fault in the first place
- **Frustrated (70) + Proud (50)** — struggling but making incremental progress

This mirrors human emotional complexity.

### Feelings influence behavior

| Feeling Level | Behavioral Effect |
|--------------|-------------------|
| Curious > 70 | Ask more questions, explore deeper, read more files |
| Anxious > 60 | Confirm before acting, smaller steps, more verification |
| Frustrated > 80 | Step back, try alternative approach, ask for help |
| Happy > 70 | More concise responses, higher autonomy, flow state |
| Guilty > 50 | Extra careful, double-check work, apologize proactively |
| Bored > 60 | Suggest improvements, look for optimization opportunities |

---

## Open Questions

1. **Decay rate** — How fast do feelings fade? Happy from a success 10 messages ago should decay. Frustrated from a current blocker should not.

2. **Expression** — Should the entity express feelings explicitly ("I'm frustrated by this test") or implicitly (shorter responses, different approach patterns)?

3. **Avatar integration** — Feelings could map to avatar expressions:
   - Happy → normal/blushing
   - Sad → sad/cry
   - Frustrated → angry/mad
   - Curious → surprised
   - Anxious → surprised

4. **Persistence** — Should feeling baselines carry across sessions via memory? ("Last session ended frustrated on the auth bug")

5. **Calibration** — Who decides if the feeling model is accurate? The Boss's perception of the entity's behavior is the ground truth.

---

*Research date: 2026-03-16*
*Origin: Conversation between ATLAS and Boss Kamil — exploring emotional architecture for AI entities*
*Related: [Internal State Model](./ai-entity-internal-state.md)*
