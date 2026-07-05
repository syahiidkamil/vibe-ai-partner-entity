# retrieval-qmd — and how to write your own retrieval plugin

This is the exemplar third-party adapter for VAPE's retrieval socket: it wraps a
user-installed [qmd](https://github.com/tobi/qmd) binary to give **keyless local
vector search** over the memory files. It is deliberately partial — file-space
only — to prove the socket's honesty model: declare what you serve, and the
firewall routes the rest to the files floor.

> ⚠ qmd downloads ~0.3–2 GB of GGUF models and holds them in RAM per query,
> and needs Node ≥ 22. That is its niche: semantic search with zero API keys.

## Using it

```bash
bun install -g https://github.com/tobi/qmd   # or the install path qmd documents
uv sync --extra retrieval-qmd
# config.json: { "memory": { "retrieval": "qmd", "embedder": "none" } }
uv run vape memory index    # maps to qmd update + embed
uv run vape recall "that thing about widget gears" --space file
```

`--space memory` still answers — from the files floor, not qmd. `vape memory
doctor` tells you which binary and version it found.

## Writing your own plugin (the tutorial part)

A retrieval plugin is ~100 lines. The whole contract:

1. **A folder** `vape/plugins/retrieval-<name>/` with:
   - `plugin.json` — `name`, `displayName`, `description`, `uvExtra` (setup
     reads these; add `ramWarning`/`note` if users should know something).
   - `pyproject.toml` — a workspace package named `vibe-plugin-retrieval-<name>`
     exposing an entry point in the group **`vibe.retrieval.providers`**:
     ```toml
     [project.entry-points."vibe.retrieval.providers"]
     <name> = "vibe_plugin_retrieval_<name>:YourBackend"
     ```
   - `src/vibe_plugin_retrieval_<name>/` — the package.
2. **A class** satisfying `engine.memory.interface.RetrievalBackend`:
   `capabilities() · migrate() · reset() · schema() · index(rows) ·
   search(q) · evict(ids) · evict_sources(paths)` — constructor
   `YourBackend(root_dir, config, embedder|None)`. Optional: `backfill()`.
3. **The rules that keep every backend honest** (the socket enforces the rest):
   - You are the index-card drawer, never the librarian: derive from files,
     never write file-ward, never hold un-rebuildable state.
   - Return per-leg ranked candidates (`Hit.source` + `leg_rank`); the engine
     fuses, ranks, mixes challengers, counts usage — not you.
   - Declare `capabilities` truthfully; a partial backend (like this one) is
     fine — unserved spaces fall to the floor.
   - Never compare vectors across models; record `model` beside every vector.
4. **Register in the root `pyproject.toml`**: the workspace glob
   `vape/plugins/retrieval-*` already matches your folder; add an extra +
   `[tool.uv.sources]` entry, `uv sync --extra retrieval-<name>`, done —
   `config.json`'s `memory.retrieval: "<name>"` selects you.

The sqlite plugin (`../retrieval-sqlite/`) is the fuller reference: stores,
FTS, hash-gated embeddings, reconcile semantics.
