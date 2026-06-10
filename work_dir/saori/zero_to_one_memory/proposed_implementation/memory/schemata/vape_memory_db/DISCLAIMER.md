# DISCLAIMER — VAPE memory DB schema

> **scope:**           the memory engine's Postgres/pgvector layout — tables, columns, embed dims, and
>                      the firewall's write/search/consolidate/evict ops. NOT the engine's Python API,
>                      the CLI, or the bubble/dream logic (each of those is its own schema).
> **assumes:**         the current DB migration; the `memories` table shape; a 3072-dim embedding from
>                      the current embed model; pgvector with the halfvec HNSW index.
> **invalidate when:** the DB is migrated; `schema.py` / `config.py` change; the embed dim or model
>                      changes; a table/column is renamed or dropped; the engine is rebuilt or replaced.
> **last verified:**   2026-06-09 · design draft (not yet checked against a running DB)

Read anything past `last verified` as a **hypothesis to re-check**, not a fact. The DB-migration case is
the canonical one: the instant a migration runs, the table / column / dimension beliefs in
`SCHEMATA.md` may be wrong, and a confident query against the old names fails — silently or loudly. So before acting
on this schema, confirm its `assumes` still hold; if a trigger above has fired, **cross out what
changed or rebuild the schema first**. A hot, recent page is not a valid one.

*Convention and the shared why: `../CLAUDE.md`.*
