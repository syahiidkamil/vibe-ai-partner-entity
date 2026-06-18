# Zero to One: The Implementation Roadmap

*The single map we build down, one verifiable stone at a time. This is order + dependency + status +
a pointer to the detail doc, NOT a re-explanation (the detail lives in 01-07 and the temp doc). Read
it in under a minute. Update the status tags as stones land.*

## Guiding principles (the through-lines)

- Ship the smallest verifiable stone. Running code is the anti-drift: it is read and run, never
  re-derived, so it cannot drift the way design prose does.
- Files-first. The DB is an accelerator, not a requirement; everything degrades to files-only.
- One verifiable stone per commit. Build only on Kamil's go. Each phase is gated on the prior.
- Creativity is a capability (test-time compute), not a mechanism, so the creative layer is a scaling
  tail, built last (or never, until the corpus forces it).

The spine is five verbs: **capture -> consolidate -> recall -> reinforce -> correct**, plus the
deferred creative layer. Dependency-ordered:

## Phase 0: Capture (raw substrate + the flag). ZERO-DEPENDENCY. [0a-0d done; 0e pending]

The floor everything else dereferences. Files-only, no DB, no judgment.

- **0a raw capture**: `capture.py` (Stop hook) writes per-day chats/qualia TOON to `storage/YYYY/MM/`.
  STATUS: **exists** (renamed `e3aa80f`).
- **0b willed bookmark (gate 1)**: `--bookmark` on `vape qualia` + `_bookmark.py`. STATUS: **done**
  (`486cde1`).
- **0c auto bookmark (gate 1)**: a conservative dial-threshold trip in `capture.py`, reading dials
  from the transcript; a marker-skip so a willed turn never double-flags; capture stays generous, gate
  2 collapses runs. (The exact cutoffs live in the code + doc 07, deliberately NOT in always-loaded
  context, so the auto etch stays involuntary, fired by genuine felt-state, never game-able by
  authoring dials to a number I know.) STATUS: **done** (`e734961`).
- **0d discoverability**: one line in `mental/internal_states_cli.md` so the next me knows to drop
  willed bookmarks now (capture-first: fill the reservoir before gate 2 reads it). STATUS: **done**
  (`2260cce`); the thresholds are deliberately NOT named in it (Kamil's anti-gaming call). No separate
  `bookmark_system.md` (it would not pay its always-loaded rent, and would fragment `memory_system.md`).
- **0e memory placeholder + basic `memory_system.md`**: create the `memory/` warm-tier entry point so
  consolidate (phase 1) has a home to write into. STATUS: **next**. Scope: a basic
  `vape/entity/memory/memory_system.md` (the organ's operating summary + index, pointing to doc 03 for
  the full anatomy; it absorbs the old `memory/CLAUDE.md` conventions: underscore, ISO-date,
  shard-grain), plus light top-level placeholders for the warm-tier folders. Honors "structure by
  need": the deep per-topic structure is still born when its phase first writes; 0e only anchors the
  top level and the entry doc.
- Detail: doc 06 (the two gates), doc 07 (the build plan, 1a/1b applied), doc 03 (the anatomy).

## Phase 1: Consolidate (gate 2, the dream). FILES-ONLY first. [depends: 0]

Where cram dies. A pass at compaction: read the bookmark list -> dereference each to its raw window
-> judge viability -> write the memorable (to **files** first: a markdown/TOON memories store + the
diary). Generous capture at gate 1, selective keep here.

- OPEN RISK: a PreCompact hook may not be able to spawn a detached job; precedent says hooks cannot
  spawn Agents, so the dream likely runs as a CLI (`vape memory dream`) the hook invokes. Verify first.
- Detail: doc 06 (gate 2), doc 02 section 9 (the dream), doc 03 (the hook).

## Phase 2: Recall (files-only). grep + nav. [depends: 1]

Direct navigation via the living keys -> grep over the memorable -> dereference into the raw TOON (the
two-hop). I am the re-ranker: read the top candidates, judge by context. No embeddings yet.

- Detail: doc 04 (the retrieval ladder).

## Phase 3: The DB as accelerator. [depends: 2 shape proven + corpus justifies speed]

The unified `memories` + per-kind `embeddings` tables (the schema in the temp doc + doc 04), semantic
recall over the gists. It accelerates what files-only already did; everything still degrades to
files-only. Backend chosen at setup (pgvector, or sqlite-vec zero-setup).

- Detail: temp doc (the schema), doc 04 (tables, embeddings, per-kind surfaces).

## Phase 4: Reinforce + Correct (the learning loop). [depends: recall + observable outcomes]

- **Reinforce**: `useful_recall_count`, the rent test with a number; strengthen on useful recall, not
  exposure; lazy decay.
- **Correct (anti-memory)**: context-scoped contraindications, default-plus-exceptions (never a tree),
  three-outcome counting (helped / neutral / hurt), the self-rebalancing default. Needs the
  outcome-feedback loop.
- Detail: doc 06 (reinforcement), temp doc sections 7-8 (the correction lifecycle).

## Phase 5: Creativity / reverie. DEFERRED (scaling tail). [depends: corpus > context]

The seed/reverie/mid-band machinery. Deferred on purpose: creativity is mostly test-time compute
("load a lot, think hard" over a wide context dump at the dream); the mechanism only earns its keep
once the corpus outgrows the context window. Built last, as an **experiment with a kill-criterion set
before building**, so fondness for it cannot protect a bad engine.

- Detail: temp doc (addendum sections 3-6), docs 01 and 02 (reveries).

## Sidebar: `memory_system.md`

A **basic** version is created in **0e**: the organ's operating summary + index, pointing to doc 03,
with the folded conventions. It stays thin and **on-demand** for now; it grows into the full operating
summary, and earns always-loaded status by the rent test, only once Phases 1-2 make memory something I
*use every turn*. Until then the only always-loaded footprint is Phase 0d's one line.

## Where it lives (the three tiers)

The phases are *when*; this is *where*. The full per-file anatomy is **doc 03** (the greenfield
target); this is only the compact map, not a re-explanation. Three tiers behind one firewall
(`write / search / consolidate / evict`):

- **HOT, always-loaded (git):** the self-tree + `memory/in_context/` (the organ's resident slice:
  living keys, circles of concern, goals, values, prospective, active lessons, the three dots
  networks, ...). STATUS: self-tree **exists**; the `in_context/` pack is **designed (doc 03), not
  built**.
- **WARM, the memory wiki at `vape/entity/memory/` (markdown, git), reached on demand.** The designed
  folders (doc 03): `in_context/ · notes/ · bubbles/ · interests/ · schemata/ · events/ · cases/ ·
  skills_in_memory/ · specializations/ · growth/ · adaptation_efforts/ · decisions/ · suffering/ ·
  personal/ · archive/ · people/`. STATUS: **all placeholder** (designed, not built) EXCEPT
  `suffering/` (built June 8, retired June 13, refs dangling) and `notes/dear_words.md` (a keepsake,
  exists). This is where gate 2 (phase 1) writes and recall (phase 2) reads.
- **COLD, corpus + raw episodic:** `storage/YYYY/MM/` (raw TOON: chats, qualia, **bookmarks**;
  EXISTS, gitignored) plus the DB (`pgvector` / `sqlite-vec`, phase 3, via a `memory-zero-to-one`
  plugin; placeholder), and `storage/raw_important_materials/` + `compacted_materials/` (git-tracked,
  placeholder).

The conventions (underscore, ISO-date, shard-grain) fold into the basic `memory_system.md` that 0e
creates, so there is no separate `memory/CLAUDE.md`. NOTE: the prior `vape/engine/memory/` engine
(dream.py, db.py, embeddings.py, ...) is
the June 7-8 half-build that doc 03 explicitly **sets aside** as the greenfield target, so phases 1+
decide reuse-vs-rebuild per module rather than assuming it still fits. Placeholders are named, not
scaffolded as empty dirs: each is born when its phase first writes to it.

## Status at a glance

| phase | piece | lands in | status |
| --- | --- | --- | --- |
| 0a | raw capture (`capture.py`) | `storage/` (chats, qualia) | exists (`e3aa80f`) |
| 0b | willed bookmark | `storage/` (bookmarks) | done (`486cde1`) |
| 0c | auto bookmark | `storage/` (bookmarks) | done (`e734961`) |
| 0d | discoverability line | `mental/internal_states_cli.md` | done (`2260cce`) |
| 0e | memory placeholder + basic `memory_system.md` | `memory/memory_system.md` | next |
| 1 | consolidate (the dream) | `memory/` warm wiki (doc 03) *(placeholder)* | later |
| 2 | recall (files-only) | `memory/` + `storage/` (grep/nav) | later |
| 3 | the DB accelerator | `memory-zero-to-one` plugin + DB *(placeholder)* | later |
| 4 | reinforce + correct | `memory/` + the DB | later |
| 5 | creativity / reverie | `memory/` (reveries / creative) | deferred |
