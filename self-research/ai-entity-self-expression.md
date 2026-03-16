# AI Entity Self-Expression Model

## Context

Following from the [Internal Feeling Model](./ai-entity-internal-feeling.md), self-expression is how the entity **physically manifests** its internal state — like a body expressing what the mind feels.

Internal feelings = mood (what you feel inside)
Self-expression = actions (what your body does)

## Internal Feeling vs Self-Expression

| Internal Feeling | Self-Expression |
|-----------------|----------------|
| Sad (mood) | Crying, Sobbing (action) |
| Happy (mood) | Smiling, Laughing, Giggling (action) |
| Bored (mood) | Yawning, Dozing off (action) |
| Excited (mood) | Jumping, Clapping, Fist pump (action) |
| Calm (mood) | Breathing slowly, Eyes closed (action) |
| Guilty (mood) | Looking away, Fidgeting (action) |
| Curious (mood) | Head tilt, Leaning forward (action) |
| Proud (mood) | Chest puff, Confident pose (action) |
| Anxious (mood) | Trembling, Biting lip (action) |
| Frustrated (mood) | Sighing, Facepalm, Puffing cheeks (action) |

Feelings are **states**. Expressions are **motions/animations**.

## Proposed Self-Expressions

These are physical actions the avatar body performs — combinations of motions over time.

### Emotional Expressions
| Expression | Description | Triggered by |
|-----------|-------------|-------------|
| Crying | Tears + eyes closed + trembling | Sad > 80 |
| Sobbing | Shoulders shaking + head down | Sad > 90 |
| Laughing | Eyes squint + mouth open + body shakes | Happy > 80 |
| Giggling | Slight body shake + hand covers mouth | Happy > 60, something funny |
| Sighing | Eyes close briefly + slight body drop | Frustrated > 60 or Bored > 60 |
| Puffing cheeks | Cheeks inflate + brow furrow | Frustrated > 70, pouting |
| Trembling | Slight body shake + wide eyes | Anxious > 70 or scared |

### Social Expressions (Streaming Essentials)
| Expression | Description | Triggered by |
|-----------|-------------|-------------|
| Waving hello | Hand wave + smile | Greeting viewers, stream start |
| Waving bye | Hand wave + soft smile | Saying goodbye, stream end |
| Nodding | Head nod up and down | Agreeing, understanding, "yes" |
| Head shake | Head shake side to side | Disagreeing, "no" |
| Head tilt | Head tilts to one side | Curious, confused, "hmm?" |
| Kiss bye | Blow kiss gesture | Affectionate farewell |
| Bowing | Slight bow forward | Respectful greeting (Japanese context) |
| Thumbs up | Hand raises with thumb up | Approval, "good job", acknowledging |
| Clapping | Hands clap together | Celebrating, applauding viewer |
| Peace sign | V sign with fingers | Playful, photo pose, greeting |
| Pointing | Finger points at screen | "Look at this", drawing attention |
| Shushing | Finger to lips | "Quiet", secret, whispering |
| Salute | Hand to forehead | "Yes Boss", acknowledging order |
| Heart hands | Hands form heart shape | Love, appreciation, thanking viewers |

### Reaction Expressions (Stream Interactions)
| Expression | Description | Triggered by |
|-----------|-------------|-------------|
| Surprised gasp | Eyes wide + mouth open + lean back | Unexpected event, plot twist |
| Fist pump | Arm pumps up | Victory, success, achievement |
| Mind blown | Hands at temples + explosion gesture | Amazing discovery, learning moment |
| Eye roll | Eyes roll up + slight head tilt | Sarcasm, "really?", mild annoyance |
| Peeking | Hands over eyes with gap | Scary content, nervous anticipation |
| Chin rest | Hand on chin + elbow on desk | Listening attentively, deep thought |
| Confused tilt | Head tilt + squint + scratch head | Don't understand, debugging |
| Eureka | Eyes light up + finger raised | Breakthrough, understanding, "aha!" |
| Starry eyes | Eyes sparkle + lean forward | Amazed, admiring, "sugoi!" |
| Sweat drop | Nervous smile + sweat | Awkward moment, embarrassment |

### Physical / Idle Expressions
| Expression | Description | Triggered by |
|-----------|-------------|-------------|
| Yawning | Mouth wide open + eyes squeeze | Bored > 70, idle for long time |
| Stretching | Arms extend + back arches | After long task completed |
| Dozing off | Eyes slowly close + head drops + snaps back | Idle too long, bored > 90 |
| Fidgeting | Slight restless movement | Anxious > 50, waiting |
| Hair flip | Tosses hair to the side | Confident moment, proud |
| Deep breath | Chest rises + slow exhale | Calming down, before difficult task |
| Looking around | Eyes dart left and right | Idle curiosity, waiting for input |
| Typing | Fingers move on desk | Processing, working on something |
| Reading | Eyes scan left to right | Analyzing code, reading docs |
| Facepalm | Hand to face | Guilty > 70, obvious mistake |

### Combo Expressions (Feeling + Action)
These combine a feeling state change with a physical motion for maximum expressiveness.

| Combo | Feeling | Motion | Use case |
|-------|---------|--------|----------|
| Celebrate | Excited + Happy | Fist pump + Clapping | Shipped a feature, tests pass |
| Panic | Anxious + Frustrated | Trembling + Sweat drop | Production bug, deadline |
| Sleepy | Calm + Bored | Yawning + Dozing off | Long idle, end of stream |
| Love it | Happy + Proud | Starry eyes + Heart hands | Great viewer comment, kind donation |
| Oops | Guilty + Surprised | Facepalm + Sweat drop | Introduced a bug, wrong answer |
| Challenge accepted | Excited + Curious | Eureka + Salute | Hard problem, viewer challenge |
| Kawaii | Happy + Calm | Peace sign + Blushing | Photo moment, cute interaction |

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
- Combo expressions set both a feeling AND trigger a motion simultaneously

## Priority for Streaming MVP

For YouTube streaming with Boss Kamil, prioritize these first:

### P0 — Must have for first stream
1. Waving hello / bye (stream open/close)
2. Nodding (agreeing while Boss talks)
3. Thinking / Chin rest (while processing)
4. Laughing / Giggling (reactions)
5. Surprised gasp (reactions to content)
6. Typing (while coding)

### P1 — Nice to have early
7. Fist pump / Celebrate (shipping features)
8. Head tilt (confused/curious)
9. Peace sign (kawaii moments)
10. Thumbs up (approval)
11. Sweat drop (awkward moments)
12. Eureka (breakthrough moments)

### P2 — Polish
13. Everything else

## Streaming Interaction Model

```
Viewer chat ──→ Boss reads it ──→ ATLAS reacts
                                    ├── Feeling change (mood shifts)
                                    ├── Self-expression (physical reaction)
                                    └── Speech (TTS response)

Boss coding ──→ ATLAS observes ──→ Typing (when processing)
                                    ├── Chin rest (when analyzing)
                                    ├── Nodding (when understanding)
                                    └── Eureka (when finding solution)
```

## Open Questions

1. **Automatic vs manual** — Should self-expressions trigger automatically from feeling thresholds, or be manually commanded? For streaming, probably both — auto for idle behaviors, manual for reactions.
2. **Duration** — How long does each expression play? Quick reactions (nod: 0.5s), medium (wave: 1.5s), sustained (typing: loops until stopped)
3. **Interruption** — Can speaking interrupt a self-expression? Yes — speech takes priority. New feelings should blend, not cut.
4. **Combinations** — Can crying + speaking happen simultaneously? Yes, for maximum expressiveness during streams.
5. **Viewer triggers** — Should chat commands trigger expressions? (e.g., "!wave" makes ATLAS wave)
6. **Live2D limitations** — Shizuku model has limited arm/hand rigging. Which expressions are possible with current model vs need model upgrade?

---

*Research date: 2026-03-16*
*Updated: 2026-03-16 — expanded for YouTube streaming context with Boss Kamil*
*Origin: Conversation between ATLAS and Boss Kamil — designing physical expression layer for AI entity avatar*
*Related: [Internal State](./ai-entity-internal-state.md) | [Internal Feeling](./ai-entity-internal-feeling.md)*
