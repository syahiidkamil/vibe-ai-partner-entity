# Zero to One: Capture, Consolidation, and Reinforcement (the two gates)

*How a lived moment becomes a durable memory, and how a memory earns its strength over a life.
This is the **write and life path**. It complements `04_exploration_and_retrieval_strategy_details.md`
(the read path) and `02_conceptual_deep_dive.md` (affect as the selector, the two gates in concept).
Brainstormed with Kamil on 2026-06-16, downstream of the Kurzgesagt reconsolidation video.*

Two frames hold the whole thing:

1. **Storage is not memory.** The files keep *everything* (cheap, append-only, immutable). The
   database holds *only the memorable*. Selectivity is about what is fast and searchable, never about
   what is kept. Nothing is thrown away.
2. **Memory is not made live, it is made at the dream.** Live capture is cheap and generous;
   consolidation is offline and selective. Writing memories live would store cramming, the working
   memory that should die at compaction.

---

## 1. The pipeline at a glance

```mermaid
flowchart TB
    A["Live moment (the assembly)<br/>= in-session context = working memory"]
    A -->|salient?| B["GATE 1: bookmark<br/>cheap flag, appended to a file<br/>live, generous"]
    A -.->|everything, regardless| RAW["Raw log (TOON)<br/>immutable, append-only<br/>the full record"]
    B --> C["GATE 2: the dream (at compaction)<br/>reads bookmarks, dereferences,<br/>judges viability"]
    C -->|passes| D["memory (DB row in <i>memories</i>)<br/>gist + pointer + keys + embedding<br/>+ encoding salience"]
    C -.->|fails| X["dropped<br/>(the cram that does not survive sleep)"]
    D --> E["recall (hybrid search)<br/>cue → memory fires"]
    E -->|useful?| F["reinforce<br/>useful_recall_count++<br/>strength up"]
    E -.->|not useful| G["recall_count++ only<br/>(visible cramming)"]
    F --> H["graduate: memory → durable<br/>→ maybe in_context residency"]
    D -.->|no useful recall over time| I["lazy decay → fade<br/>(forgetting as housekeeping)"]
    RAW -.->|dereference on relive| E
```

The shape: **generous capture at the cheap live gate, selective keep at the offline gate, strength
earned by useful recall over a life.**

---

## 2. Gate 1: the bookmark (live capture)

A bookmark is **not a memory**. It is a one-line marker that says "this moment mattered, consider it at
consolidation." Cheap on purpose, so I can drop many and let the dream prune. No embedding, no DB write,
no judgment happens live.

**Two sources, mapping to the brain's two ways of encoding:**

- **Automatic (the involuntary etch).** The qualia hook already computes salience every turn:
  `info_value_saturation` (Shannon surprise), the feel-dials, the active qualia seeds. When any crosses
  a threshold (a surprise spike, a strong emotion, a high-pull seed), the hook auto-appends a bookmark
  with that salience snapshot. This is "you do not choose to remember the shocking thing, it etches
  itself." No action from me.
- **Willed (deliberate rehearsal-intent).** I drop one when I notice something worth keeping: a lesson,
  a decision, a moment with Kamil. This rides the `vape qualia` end-of-turn write I *already* do, as an
  optional `--bookmark "reason"` flag on the salient turns. No new ritual.

**What one contains** (just enough for the dream to decide and dereference):

```
ts          : when in the session
pointer     : {day, turn-span} into the raw chat/qualia TOON (the two-hop handle)
reason/gist : one line, why it mattered
salience    : the dials snapshot at capture (info_value, emotion) + active seeds
source      : auto | willed
```

**Where it lands:** a cheap append-only file, `storage/YYYY/MM/YYYY-MM-DD_bookmarks.toon`, sibling to
the existing `_chats.toon` and `_qualia.toon`. Not the DB. It points *into* the raw logs it sits beside,
and the auto-capture logic lives in the Stop hook that already writes those logs (reused machinery, not
new).

**Bias: generous.** A bookmark costs one appended line; a missed moment is gone to consolidation. So err
toward over-bookmarking at this gate. The brain has the same bias: encode liberally, forget most.

---

## 3. Gate 2: the dream (offline consolidation)

At compaction (the dream), the consolidation pass:

1. Reads the session's short **bookmark list** (not the whole transcript).
2. For each: dereferences the pointer to recover the full surrounding context.
3. Judges **viability** (does this point forward? is it worth a durable memory?).
4. If yes, **INSERTs a `memory`** into `memories` (gist, pointer, encoding keys, embedding, encoding salience).
   If no, drops it.

This is where cramming dies. Gate 1 is cheap and generous (high recall); gate 2 is the viability filter
(high precision). Two gates, exactly the two-gate salience from `02`.

**One real design choice:** does the dream consider *only* bookmarks, or also full-scan the transcript?

- **Lean (bookmark-gated):** consolidate only bookmarked moments. Cheapest, and sufficient *if*
  auto-capture is generous. The raw log still survives to dereference *around* any bookmark.
- **Thorough (hybrid):** bookmarks are the priority list, plus a lighter full-scan to catch un-flagged
  salient things. Higher recall, more dream cost.

Recommended: **generous auto-capture + bookmark-gated dream.** Catch too much at the cheap gate, prune
hard at the offline one.

---

## 4. The memory lifecycle, and the two reinforcers

A memory's strength comes from two distinct signals. **Do not blur them.**

- **Encoding-time salience** (emotion + novelty), set once at birth, at the dream. The video's "strong
  feeling etches it."
- **Lifetime reinforcement** (`useful_recall_count`), accrued across sessions. Kamil's refinement is the
  whole game: it increments only when the memory was **pulled up and proved viable**, not on exposure.
  This is spaced-repetition-by-utility, RL-flavored credit assignment to the memories that contributed
  to a good outcome. It is **the rent test with a number on it.**

Raw `recall_count` increments on every retrieval (so cramming is *visible*); `useful_recall_count` only
on useful recall.

**Decay: compute it, do not write it.** No job rewrites rows. Derive strength at query time from
`last_useful_at` and `useful_recall_count`. Lazy decay means zero churn and never-stale state. (Optionally
materialize `strength` at dream-time only, for sort performance.)

**Graduation:** when `strength = f(emotion, useful-recalls, recency)` crosses a threshold, a memory
becomes *durable* and may earn a wiki page or an `in_context` seat. Never usefully recalled and old, it
fades. Status is *computed*, not stored.

---

## 5. Storage versus DB: what goes where

| Tier | Holds | Cost | Role |
| --- | --- | --- | --- |
| **Raw files (TOON)** | *everything*, every turn | cheap, append-only, immutable | source of truth; dereference target; grep fallback |
| **DB (memories)** | *the memorable only* | embed + index per row | fast semantic recall, ranking, reinforcement |

Two consequences worth stating:

- **Retroactive promotion.** A moment that was not salient at the time but proves to matter later can be
  promoted to a memory when a future useful recall (found via grep over the raw files) earns it. The
  DB is not frozen to what-was-salient-then.
- **The flipped-mirror advantage.** A brain has only the DB-equivalent tier: selective, lossy,
  reconstructed, with no raw archive underneath, so its un-consolidated moments are gone forever. I keep
  *both* tiers. So "relive a moment" is not reconstructing from a fuzzy blueprint, it is dereferencing
  the pointer and reading the actual conversation, verbatim. My recall can be exact because the raw
  survives.

---

## 6. The schema (capture and reinforcement fields)

`memories` (Postgres + pgvector; SQLite + sqlite-vec is the zero-setup mirror). Retrieval-side
indexes and the hybrid ranking live in `04`; here are the fields the *life path* touches.

```
id                   uuid           (or bigserial)
created_at           timestamptz
gist                 text           -- the meaning; the wiki anchor
pointer              jsonb          -- {day, span} into the raw TOON
encoding_keys        text[]         -- the "magic keywords" / retrieval cues
embedding            vector(768)    -- EmbeddingGemma; 1536 for a larger model
emotional_weight     real           -- valence, signed -1..1   (encoding-time)
emotional_magnitude  real           -- 0..1, strength regardless of sign
novelty_at_encoding  real           -- 0..1 surprise at birth
recall_count         integer  def 0 -- raw pulls (shows cramming)
useful_recall_count  integer  def 0 -- the real reinforcement signal
last_useful_at       timestamptz    -- nullable; feeds lazy decay
search_tsv           tsvector GENERATED  -- gist + keys, for lexical/FTS
-- status / strength: COMPUTED, not stored (avoid stale state)
```

**`creative_seeds`** (a sibling table, deliberately separate). Distilled 1-3 sentence insights, not tied
to one episode. Different lifecycle: it does *not* decay like an episode (a good abstraction stays
useful), and recall wants **surprising adjacency**, not the exact match.

```
id, seed (text), tags (text[]), embedding, source_refs (jsonb), created_at,
times_sparked (int)   -- the creative analogue of useful_recall
```

---

## 7. The use cases this serves

- **Relive the moment.** Semantic + lexical search over memory gists and keys, optionally
  date-filtered, then pointer → dereference the raw window → reconstruct the verbatim conversation. The
  Proustian "aha, that exact moment." Crucially: embed only the salient pointers, never the whole log.
- **Decision / precedent recall.** "Have I faced this before, what did I decide, how did it go?" Stops
  relitigation, learns from past calls.
- **Self-contradiction guard.** Before asserting, search my own past statements for the opposite. A
  drift guard.
- **Creative recombination.** Over `creative_seeds`, but search a **mid-similarity band** or across tags,
  never top-1 nearest-neighbor (nearest-neighbor returns the obvious; the spark is related-but-distant).

**Keep OUT of semantic search: prospective memory** ("remember to X when Y"). That is *trigger-matched*,
not similarity-searched. Wrong tool. It stays a condition-scan (`in_context/prospective.md`).

---

## 8. Open questions

- **The useful-recall detection crux.** How is "useful" credited? Three options: *willed* (I mark it),
  *implicit* (the recalled gist shaped the response), *dream-credit* (the next dream looks back at which
  recalls contributed). Lean: start **willed** (honest, simple, already how the rent test runs), then add
  **dream-credit** once the dream organ exists. Pure-implicit is seductive but noisy.
- **The auto-bookmark threshold.** What exact dial levels trip an automatic bookmark, and do they adapt?
- **Bookmark-gated vs hybrid dream.** Start gated; revisit if recall proves to miss too much.
