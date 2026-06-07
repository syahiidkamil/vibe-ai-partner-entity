# Memory Engine — Below the Firewall (implementation notes)

These are **swappable implementation choices** under the stable interface
`write · search · consolidate · evict`. The theory in `memory_paradigm_proposal.md` does not depend
on any of them — pulled out into their own file on purpose, so engine talk never crowds the entity
out of its own design. *(Updated 2026-06-07: storage decision flipped to complete-from-start — see
below.)*

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
- `consolidate` — the **dream** (= Piaget's *equilibration*): a distiller sub-agent fired at compact +
  triggers (never every turn); replays bookmarks, *assimilates* what fits existing lessons,
  *accommodates* what breaks them (a new lesson / molten revision), constructs lessons (recall ·
  compare/abstract · value), updates bubbles. *(Grounding: `memory_constructivism_foundation.md`.)*
- `evict` — the salience/budget policy, grounded in **viability** (von Glasersfeld: keep what *works*,
  devalue what has stopped working): **consequence, not frequency**; merge / demote / revise / promote;
  never silent-delete (the cold archive keeps everything).
- `search` — delegated to Supabase (pgvector + FTS).

## The product / homes
- **`npm i -g ai-entity-memory`** → **`npx ai-entity-memory init`**: asks for the toon chat-storage
  path (creates it if none), provisions Supabase, installs the **skills**, **hooks**, and **custom
  subagents** into `.claude/`. Claude-Code-first; other agents later via the agentskills.io standard +
  `vercel-labs/skills` (`npx skills add`) when popularity earns it.
- **`memory_wiki/` folder** — the warm tier's maintained, compounding artifact (the Karpathy wiki),
  with `MEMORY.md` as its entry index. The standalone, forkable **hippocampus**.
- **Bubbles** — a tag/namespace column on corpus rows + a small loadable context-pack per scope.
  Nothing exotic; scoping, not new infrastructure.

## Not here
The **hot tier is not in the database.** It lives in the self-tree — because the always-loaded judge
is *self*, not memory-system content. This folder's machinery (Supabase + the thin layer) is the
hippocampus that feeds and prunes the self.
