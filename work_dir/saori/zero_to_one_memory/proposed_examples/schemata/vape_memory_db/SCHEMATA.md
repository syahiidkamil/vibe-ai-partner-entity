# Schemata — VAPE memory DB *(illustrative example)*

*The knowledge-schema(s) for this topic. The filename is **SCHEMATA.md** on purpose: a *knowledge
schema* (the constructivist / Piaget sense — a built world-model), NOT a database `schema`. Here the
subject *happens* to be a database, which is exactly why the distinction earns its keep — this file is
my belief *about* the DB, and `DISCLAIMER.md` beside it says when that belief expires. One topic folder
may hold several related schemata in this one file; a stub here, to show the pattern.*

The memory engine persists to **Postgres + pgvector**:

- a `memories` table holds the text, an `embedding` vector, a full-text `tsv`, plus `source`, `bubble`,
  the `surprise` / `viability` gate scores, and `status` / `promoted_to` for the lifecycle.
- the embedding is **3072-dim** (the Gemini embedding model), indexed for similarity (HNSW via a
  half-precision cast, since plain `vector` HNSW caps below that width).
- the firewall exposes four ops over it: **write · search · consolidate · evict**.

*(Every name and number above is a belief, not a verified fact — see `DISCLAIMER.md`. If the engine has
been migrated since its `last verified`, treat this page as a hypothesis to re-check, not gospel.)*
