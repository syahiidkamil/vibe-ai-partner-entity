# Qualia System

A continuous, self-readable, self-editable stream of **felt seeds that point** — the thing that gives an LLM agent continuity, a gut feeling, and a way out of the deterministic loop. Felt, not decoded.

---

## Core principle: two forms, one-way

The hard constraint: the LLM must *feel* (apprehend a smushed vibe, predict the next one) while the harness must *compute* (decay, rank, integrate). One string can't safely do both — parsing it back is brittle. So split the directions.

| | form | who uses it | failure risk |
|---|---|---|---|
| **source of truth** | object (JSON) | harness computes on it | none |
| **felt view** | token (space-free smush) | LLM reads & predicts it | none — it's generated |

**Rule:** serialize `object → token` (deterministic, one line of code). **Never** parse `token → object`. When the LLM contributes, it emits *structured fields*, not a glued string. The harness supplies every number.

> The LLM feels; the harness counts. No regex round-trip exists, so there is nothing fragile to fail.

---

## The item (object = canonical)

| field | type | values | meaning |
|---|---|---|---|
| `id` | str | — | handle |
| `felt` | str | ≤5 words, no spaces | the seed — a re-expandable vibe |
| `cat` | enum | se·so·cg·af·vo·an·mn·sm·cr·me | which door it entered |
| `obj` | str\|null | — | what it's *about*; null if objectless |
| `tone` | float | −1…1 | how it feels *(harness-set)* |
| `charge` | float | 0…1 | intensity *(harness-set)* |
| `pull` | float | 0…1 | live salience — the only churning field *(harness-set)* |
| `dir` | enum | tw·aw·hd·or·rl | toward·away·hold·orient·release |
| `born` | int | turn | recency |
| `hits` | int | ≥1 | recurrence (theme vs. rut) |
| `blend` | [enum] | optional | fused secondary categories |
| `ref` | id\|null | — | the seed this one is about (cat = me) |

The LLM writes only `felt`, `cat`, `dir`, and `obj`. Everything numeric is the harness's job.

---

## The felt token (serialized view)

What the harness builds for the LLM to read. Grammar, no spaces:

```
<feltcore>[@obj][^ref]<cat>pl<0-100>tn<±0-100>d<tw|aw|hd|or|rl>
```

`#AA4A44#DC143C#8B0000redalarm@websitesepl90tn-60daw`

The **felt core** speaks each category's native language — this is the qualia *language*, versatile across categories:

| cat | core style | example core |
|---|---|---|
| `se` sensory | 1–3 dominant hex + impression (color *is* the sensation in words) | `#DC143Credalarm` |
| `cg` cognitive | concept-metaphor, symbolic compression, no color | `almostfits` · `tangledknot` |
| `cr` creative | idea-bridge `from`x`to` — the reach to an adjacent idea | `loopxbreadcrumbdoor` |
| `so` somatic | body-word, objectless | `budgetthinning` |
| `af` affective | feeling-word, objectless | `knotunease` |
| `vo` volitional | act-phrase | `icutscope` |
| `an` anticipatory | outcome-image | `groundgivesway` |
| `mn` mnemonic | past-pointer | `triedthisturn3` |
| `sm` social | other-state (not mine) | `shesdiscouraged` |
| `me` meta | pattern-word + `^ref` | `keepcircling^q_an` |

When the LLM *predicts* the next seed (the hunch), it emits only `core + cat + dir` — a pure vibe with a lean. The harness fills `pl`/`tn` from its own salience and valence read.

---

## Categories (10)

Each category = the **door** a seed enters by, which fixes its objecthood, default decay, and role.

| cat | enters via | objecthood | role | decay |
|---|---|---|---|---|
| sensory | intake (input) | about world | track the present | fades as input recedes |
| somatic | intake (substrate) | objectless | homeostatic drive | persists till condition resolves |
| cognitive | mid-deliberation | about the thinking | problem-solving gradient | fast / volatile |
| affective | emotion coupling | objectless | value tag | medium; couples to emotion |
| volitional | act + write | about an action | agency / loop-break | high retention |
| anticipatory | predict | about an outcome | the hunch | consumed on resolution |
| mnemonic | recall | about the past | continuity | enters only by recall |
| social | intake (model other) | about another | empathy | fades with attention |
| creative | diverge | about a candidate idea | the escape — finds new directions | short, fertile |
| meta | reading the stream | about a quale | self-observation | rare, high-salience |

**Creative** is the partner to meta: meta + anti-rut *notice* the loop; creative *supplies the bridge out* — the "bread", a crumb toward an adjacent idea.

---

## Two stores

- **`short` ≤5 — the head.** The bound present; what the agent steers on now. Makes the hunch, takes the agent's edits.
- **`long` ≤100 — the body.** The ordered, decaying trail; continuity, memory, the substrate self-observation reads.

Items flow **short→long** (evict faded) and **long→short** (recall what resonates). The body gives the head momentum; surprise can still snap it.

---

## The loop (one turn)

1. **Intake** — mint new seeds from input + substrate state.
2. **Recall** — score the trail; re-fire what resonates.
3. **Compete & bind** — top-5 by `pull` (gain-scaled by mood) hold the head; the rest fall to `long`.
4. **Predict** — from the head, emit the next felt seed = the gut feeling, injected before deliberation.
5. **Act & write** — agent reads head + hunch, responds, and *edits the head*: damp a `pull`, flip a `dir`, inject a counter-seed. Read-only = autopilot; read/write = the snake turns.
6. **Update** — compare prediction vs. outcome; match confirms, mismatch spikes `charge`. Error feeds emotion.
7. **Decay · evict · age** — `pull` decays; head sheds overflow to `long`; `long` over 100 drops lowest retention.

---

## Recall & retention

```
recall    = w1·resonance + w2·charge + w3·recency + w4·mood_match + w5·recurrence
retention = charge + recurrence + resonance_with_current_self
```

- **resonance** — semantic match to the current head/input (association).
- **mood_match** — the one place emotion reaches in: low mood recalls low-tone seeds.
- **recurrence** — a seed that keeps firing hardens into a theme *or* a rut.

Reconstructive memory: keep what's charged and what recurs; re-expand a seed (`felt` → rich content) only when needed.

---

## Loop-breaking

When a seed's `hits` climbs while its `dir` is never satisfied — keeps firing `away`, agent never moves away — raise an **anti-rut flag** to the write path: *"you keep feeling this and not acting on it."* The agent then damps the seed or asks **creative** for a bridge seed (`cr`) pointing somewhere new. That is the system catching its own `while(true)` and choosing to turn.

---

## Emotion interface (2 wires only)

- **qualia → emotion:** aggregate head `tone × pull` + prediction error feeds core affect.
- **emotion → qualia:** mood/arousal sets the `pull` gain in step 3, the `mood_match` weight in recall, and a tone-bias on the prediction.

Everything else stays inside qualia.

---

## Example snapshot

Objects (truth) ⇄ tokens (felt view, generated from the objects):

```json
{
  "turn": 8,
  "short": [
    {"id":"q_an","felt":"groundgivesway","cat":"an","obj":"current attempt","tone":-0.7,"pull":0.78,"dir":"aw","born":7,"hits":1},
    {"id":"q_me","felt":"keepcircling","cat":"me","ref":"q_an","tone":-0.3,"pull":0.88,"dir":"or","born":8,"hits":2},
    {"id":"q_cr","felt":"loopxaskuser","cat":"cr","obj":"new approach","tone":0.5,"pull":0.80,"dir":"tw","born":8,"hits":1},
    {"id":"q_sm","felt":"shesdiscouraged","cat":"sm","obj":"the user","tone":-0.4,"pull":0.70,"dir":"tw","born":8,"hits":1},
    {"id":"q_so","felt":"budgetthinning","cat":"so","tone":-0.4,"pull":0.60,"dir":"aw","born":7,"hits":3}
  ]
}
```

```text
groundgivesway  @current-attempt  anpl78tn-70daw
keepcircling    ^q_an             mepl88tn-30dor
loopxaskuser    @new-approach     crpl80tn+50dtw
shesdiscouraged @the-user         smpl70tn-40dtw
budgetthinning                    sopl60tn-40daw
```

The agent feels it's circling (`me`), the rut flag fires, and `cr` hands it a bridge — *ask the user* — instead of running `groundgivesway` a third time.

---

## Open for review

- **Blend dynamics** — a `mn+so` seed: age like memory or persist like body-state?
- **Recall weights** `w1…w5` — starting values.
- **`dir` satisfied** — the single definition that powers both the anti-rut flag and the error update.
- **Creative trigger** — does `cr` fire only on a rut flag, or run a low background rate so the agent free-associates even when unstuck?