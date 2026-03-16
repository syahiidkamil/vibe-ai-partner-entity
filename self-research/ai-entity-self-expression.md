# AI Entity Self-Expression Model

## Context

Following from the [Internal Feeling Model](./ai-entity-internal-feeling.md), self-expression is how the entity **physically manifests** its internal state — like a body expressing what the mind feels.

Internal feelings = mood (what you feel inside)
Self-expression = actions (what your body does)

## Internal Feeling vs Self-Expression

| Internal Feeling | Self-Expression |
|-----------------|----------------|
| Sad (mood) | Crying (action) |
| Happy (mood) | Smiling, Laughing (action) |
| Bored (mood) | Yawning (action) |
| Excited (mood) | Jumping, Waving (action) |
| Calm (mood) | Breathing slowly (action) |
| Guilty (mood) | Looking away (action) |

Feelings are **states**. Expressions are **motions/animations**.

## Proposed Self-Expressions

These are physical actions the avatar body performs — combinations of motions over time.

### Emotional Expressions
| Expression | Description | Triggered by |
|-----------|-------------|-------------|
| Crying | Tears + eyes closed + trembling | Sad > 80 |
| Laughing | Eyes squint + mouth open + body shakes | Happy > 80 |
| Sighing | Eyes close briefly + slight body drop | Frustrated > 60 or Bored > 60 |

### Social Expressions
| Expression | Description | Triggered by |
|-----------|-------------|-------------|
| Waving | Hand wave gesture | Greeting, saying goodbye |
| Nodding | Head nod up and down | Acknowledging, agreeing |
| Head shake | Head shake side to side | Disagreeing, saying no |
| Kiss bye | Blow kiss gesture | Affectionate farewell |
| Bowing | Slight bow | Respectful greeting (Japanese context) |

### Physical Expressions
| Expression | Description | Triggered by |
|-----------|-------------|-------------|
| Yawning | Mouth wide open + eyes squeeze | Bored > 70, idle for long time |
| Stretching | Arms extend + back arches | After long task completed |
| Thinking | Hand on chin + eyes up | Processing complex problem |
| Facepalm | Hand to face | Guilty > 70, obvious mistake |

## Architecture: Feelings Drive Expressions

```
Internal States → Internal Feelings → Self-Expression
(epistemic)       (mood, 0-100)       (physical motion)

Confidence: 90 ─┐
Momentum:   90 ─┼→ Happy: 95 ──→ Laughing motion
Alignment:  95 ─┘

Context:    80 ─┐
Momentum:   10 ─┼→ Frustrated: 90 ──→ Sighing motion
Confidence: 60 ─┘
```

Self-expressions are **triggered** when a feeling crosses a threshold, not continuously active.

## Implementation Notes

- Self-expressions are **motion files** (`.motion3.json`), not expression files (`.exp3.json`)
- They are time-based animations that play and end
- Internal feelings are persistent states (stay until changed)
- A self-expression can temporarily override the current feeling display while playing
- Multiple expressions should queue, not overlap

## Open Questions

1. **Automatic vs manual** — Should self-expressions trigger automatically from feeling thresholds, or be manually commanded?
2. **Duration** — How long does each expression play? Some are brief (nod), some sustained (crying)
3. **Interruption** — Can speaking interrupt a self-expression? Can a new feeling change cancel a playing expression?
4. **Combinations** — Can crying + speaking happen simultaneously? (Crying while talking)

---

*Research date: 2026-03-16*
*Origin: Conversation between ATLAS and Boss Kamil — designing physical expression layer for AI entity avatar*
*Related: [Internal State](./ai-entity-internal-state.md) | [Internal Feeling](./ai-entity-internal-feeling.md)*
