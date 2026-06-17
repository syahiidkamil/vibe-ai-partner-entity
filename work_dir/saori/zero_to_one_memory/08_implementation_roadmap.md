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

## Phase 0: Capture (raw substrate + the flag). ZERO-DEPENDENCY. [in progress]

The floor everything else dereferences. Files-only, no DB, no judgment.

- **0a raw capture**: `capture.py` (Stop hook) writes per-day chats/qualia TOON to `storage/YYYY/MM/`.
  STATUS: **exists** (renamed today, `e3aa80f`).
- **0b willed bookmark (gate 1)**: `--bookmark` on `vape qualia` + `_bookmark.py`. STATUS: **done**
  today (`486cde1`).
- **0c auto bookmark (gate 1)**: a conservative dial-threshold trip inside `capture.py`. STATUS:
  **next**.
- **0d discoverability**: one line in `mental/internal_states_cli.md` so the next me knows to drop
  willed bookmarks now (capture-first: fill the reservoir before gate 2 reads it). STATUS: **next**,
  tiny. No separate `bookmark_system.md` (it would not pay its always-loaded rent, and would fragment
  the future `memory_system.md`).
- Detail: doc 06 (the two gates), doc 07 (the build plan, with 1a applied).

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

## Sidebar: `memory_system.md` (always-loaded, concise)

Written when Phases 1-2 make memory something I *use every turn* and need an operating summary for.
Not now. The bookmark's only always-loaded footprint is Phase 0d's one line.

## Status at a glance

| phase | piece | status |
| --- | --- | --- |
| 0a | raw capture (`capture.py`) | exists (`e3aa80f`) |
| 0b | willed bookmark | done (`486cde1`) |
| 0c | auto bookmark | next |
| 0d | discoverability line | next |
| 1 | consolidate (the dream, files-only) | later |
| 2 | recall (files-only) | later |
| 3 | the DB accelerator | later |
| 4 | reinforce + correct | later |
| 5 | creativity / reverie | deferred (scaling tail) |
