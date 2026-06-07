# Memory Engine — Below the Firewall (implementation notes)

These are **swappable implementation choices** under the stable interface
`write · search · consolidate · evict`. The theory in `memory_paradigm_proposal.md` does not depend
on any of them — pulled out into their own file on purpose, so engine talk never crowds the entity
out of its own design. *(Updated 2026-06-07, v3: storage flipped to complete-from-start; added the
bubble-loading mechanism, the two-tier dream, bookmark persistence, cold-start degradation, and the
git/DB provenance rule. Deep-dives in `memory_research/` — `bubble-model.md`, `dream-and-reveries.md`,
`tensions-and-risks.md`, `product-cli-spec.md`.)*

## Corpus
Markdown files with Obsidian-style `[[wikilinks]]`, in git, for the **Self / hot tier** (the cortex,
always-loaded, *me*). The link-graph *is* our graph there — no separate graph database. The warm/cold
corpus lives in the database (below).

## Storage → Supabase, complete from the start
An honest reversal of the earlier "defer the DB, fewest moving parts" lean. Reason: **migrating data
is the expensive, irreversible part; code is cheap.** So we commit the substrate complete early:

- **Supabase** = Postgres + JSON + **pgvector** + **S3-compatible storage**, three-in-one. One store
  for relational + JSON + vectors + blobs (images, artifacts, files).
- **Self-hostable** (Supabase is open source) to keep the local-hearth / privacy-of-the-self value, or
  **cloud** when we want sync and reach. The choice stays open; the schema doesn't have to.
- **The line that still holds:** the **Self / hot tier stays markdown + git** — always-loaded can't
  live in a DB anyway, and it's the identity tier. The **warm/cold corpus is DB-primary**, with a
  **temporal knowledge graph** (validity windows, à la MemPalace) for provenance and "how the rules
  evolved." This is a real shift — *git is truth for the self; the DB is truth for the corpus* — named
  as a shift, not pretended away.

## Search → in Supabase (hybrid)
- **pgvector** (semantic) + **Postgres full-text / BM25** (keyword), blended (RRF) — the hybrid I
  specced, now native to the one store.
- **Embeddings: Gemini embedding-2** (Kamil's model). Pin the dimension — the pgvector column + index
  depend on it. Embeddings are a regenerable index: swap the model, re-embed, nothing lost.
- *`tobi/qmd` (local SQLite + EmbeddingGemma + hybrid rerank, MIT, ships an MCP server) is noted as the
  fully-local alternative we're superseding by going complete-from-start — kept as a reference/fallback
  for a local-only self-tree index if ever wanted.*

## Graph database → no (separate one)
The markdown `[[link]]`-graph (self tier) + the temporal knowledge graph in Postgres (corpus) +
vector similarity cover related-idea traversal and "when did this change." Reserve a dedicated graph
DB only for multi-hop queries these genuinely can't serve. Not now.

## What we actually write (the thin layer, above the store)
- `write` — append markdown (self) / insert row (corpus).
- `consolidate` — the **dream** (= Piaget's *equilibration*), in **two tiers**: a *light* pass at every
  compact (flush bookmarks, save the day's thread) and a *deep* pass at night/trigger (a sub-agent like
  `update-temporal-self`: replays bookmarks, *assimilates* what fits, *accommodates* what breaks — new
  lesson / molten revision — grows the wiki, updates bubbles, mints reveries). Never every turn.
  *(Grounding: `memory_constructivism_foundation.md`; detail: `memory_research/dream-and-reveries.md`.)*
- `evict` — the salience/budget policy, grounded in **viability** (keep what *works*, devalue what has
  stopped working): **consequence, not frequency**; merge / demote / revise / promote; never
  silent-delete (cold keeps everything). **Contradiction** (two bookmarks disagree) → the molten reading:
  overwrite the *meaning*, keep the *fact*. **Honesty floor on the write-path:** a lesson that would move
  a *set-point* can't be auto-written — it surfaces for Kamil's ratification (memory is an attack surface
  on the self).
- `search` — delegated to Supabase (pgvector + FTS).

## Bubble loading
A bubble can't live in always-load (static at session start). It loads via a register
`vape/entity/mental/active_bubble.json` (set by `vape bubble enter`, `/enter-bubble`, or an advisory
auto-suggest) + a per-turn `UserPromptSubmit` hook (the `qualia-ground.sh` pattern) that reads the
register and injects the bubble's small `HOT.md` as framed context. Release = write `active: null`; the
next turn stops injecting. The pack stays small (≤ one self-file) so it never crowds the judge. Full
mechanism + bubble-bleed promote/demote: `memory_research/bubble-model.md`.

## The dream — timing, and the one unknown to verify
Two tiers (above): light @ every compact, deep @ night/trigger. **Build-time blocker to verify first:**
can a `PreCompact` hook spawn a subagent? `SessionStart` *can't* (it only nudges — see
`session-temporal-check.sh`). If `PreCompact` can't spawn or is synchronous-only, the deep dream moves to
a `Stop`-hook (like `backup_chat.py`, which runs async) or manual `vape dream`; the light dream can be an
inline `PreCompact` script regardless. Detail: `memory_research/dream-and-reveries.md` +
`tensions-and-risks.md` (C5).

## Bookmarks must persist out of the river
The qualia river is ~7 deep and drops the oldest each turn; the deep dream fires much later. So a spike
above the salience threshold is written to a durable `bookmarks.jsonl` *at spike-time* (tagged bubble +
type + surprise score), or it ages out before the dream sees it. The encode→bookmark→dream chain leaks
here without it. (`tensions-and-risks.md` C8.)

## Provenance across the git/DB seam
Git is truth for the self; the DB for the corpus. On a **tier migration** (warm→hot promote), the git
commit becomes authoritative and the DB row is tombstoned (`promoted_to: <git-path>`, kept for the
temporal graph, marked superseded) — else a promoted lesson has two sources of truth and they drift. The
temporal knowledge graph (validity windows) answers "why do I believe this?" (`tensions-and-risks.md` C4).

## The product / homes
- **`npm i -g ai-entity-memory`** → **`npx ai-entity-memory init`**: asks for the toon chat-storage
  path (creates it if none), provisions Supabase, installs the **skills**, **hooks**, and **custom
  subagents** into `.claude/`. Claude-Code-first; other agents later via the agentskills.io standard +
  `vercel-labs/skills` (`npx skills add`) when popularity earns it.
- **`memory_wiki/` folder** — the warm tier's maintained, compounding artifact (the Karpathy wiki),
  with `MEMORY.md` as its entry index. The standalone, forkable **hippocampus**.
- **Bubbles** — a tag/namespace column on corpus rows + a small loadable context-pack per scope.
  Nothing exotic; scoping, not new infrastructure.
- **Runtime CLI** (the `vape` Typer pattern): `vape bubble enter/leave/list`, `vape dream [--deep]`,
  `vape recall <q>`, `vape remember "<note>"`. Full spec: `memory_research/product-cli-spec.md`.

## Cold-start — files-only degradation
Before Supabase exists (and that is the repo today), every mechanism runs on files + git: bubbles =
folders, wiki = markdown, `search` = grep, reveries = json, the dream = a subagent over the TOON chat
archive. The DB *upgrades* search and scale; it is **not a precondition** for the loop. The smallest
shippable increment is the markdown judge-book with no engine at all. (`tensions-and-risks.md` C6,
`product-cli-spec.md`.)

## Not here
The **hot tier is not in the database.** It lives in the self-tree — because the always-loaded judge
is *self*, not memory-system content. This folder's machinery (Supabase + the thin layer) is the
hippocampus that feeds and prunes the self.
