"""The corpus schema — DDL + an idempotent applier.

This is the DB-truth tier (warm/cold corpus), **not** the self/hot tier (that stays
markdown + git). One table, ``memories``, holds the rows the engine writes, searches,
consolidates, and evicts. Everything here is idempotent: safe to run on every boot.

Design choices, each traceable to the spec:

- ``embedding vector(3072)`` — Gemini's native dim, pinned in ``config.EMBED_DIM``.
- The HNSW index is built on a **halfvec** cast, not the raw vector. pgvector caps
  ``vector`` HNSW/IVFFlat indexes at 2000 dims; at 3072 the supported path is
  ``halfvec`` (half-precision) cosine HNSW. Storage stays full ``vector`` (no loss);
  only the *index* is half-precision. (Live-verified: plain hnsw at 3072 errors,
  halfvec hnsw at 3072 builds.)
- ``bubble`` — the tag/namespace column (bubbles = scoping, not new infra).
- ``surprise`` / ``viability`` — the two salience gates (surprise opens attention,
  viability keeps). Stored so ``evict`` can reason over consequence, not frequency.
- ``mem_type`` — what kind of trace (lesson / fact / episode / reverie / bookmark…).
- ``status`` + ``promoted_to`` — the git/DB provenance seam: never silent-delete;
  a promoted row is tombstoned ('superseded') with its git path, kept for the
  temporal graph.
- ``tsv`` (generated) + a GIN index — the keyword half of hybrid (pgvector + FTS).
- timestamps + ``valid_from`` / ``valid_to`` — validity windows for "when did this
  change / why do I believe this" (the temporal knowledge graph).
"""

from __future__ import annotations

from engine.memory.config import EMBED_DIM

TABLE = "memories"
EMBED_INDEX = "memories_embedding_hnsw"
TSV_INDEX = "memories_tsv_gin"

# DDL is assembled with EMBED_DIM interpolated (it is an int constant we control —
# never user input — so the f-string is safe and the dimension lives in one place).
DDL = f"""
-- 1. the extension (idempotent) ------------------------------------------------
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. the corpus table ----------------------------------------------------------
CREATE TABLE IF NOT EXISTS {TABLE} (
    id          BIGSERIAL PRIMARY KEY,
    content     TEXT        NOT NULL,
    embedding   vector({EMBED_DIM}),

    bubble      TEXT        NOT NULL DEFAULT 'global',
    mem_type    TEXT        NOT NULL DEFAULT 'episode',

    -- salience: surprise opens attention, viability keeps (consequence, not frequency)
    surprise    REAL        NOT NULL DEFAULT 0.0,
    viability   REAL        NOT NULL DEFAULT 0.0,

    -- provenance / lifecycle (never silent-delete; cold keeps everything)
    status        TEXT      NOT NULL DEFAULT 'active',   -- active | superseded | demoted
    promoted_to   TEXT,                                  -- git path when promoted to the self-tier
    source        TEXT,                                  -- where this came from (chat, dream, manual…)

    meta        JSONB       NOT NULL DEFAULT '{{}}'::jsonb,

    -- validity window (the temporal knowledge graph)
    valid_from  TIMESTAMPTZ NOT NULL DEFAULT now(),
    valid_to    TIMESTAMPTZ,

    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),

    -- keyword half of hybrid search, generated from content
    tsv         tsvector GENERATED ALWAYS AS (to_tsvector('english', content)) STORED
);

-- 3. the vector index (semantic half) -----------------------------------------
-- halfvec cast: the only HNSW path pgvector supports above 2000 dims. Cosine ops.
CREATE INDEX IF NOT EXISTS {EMBED_INDEX}
    ON {TABLE}
    USING hnsw ((embedding::halfvec({EMBED_DIM})) halfvec_cosine_ops);

-- 4. the keyword index (lexical half) -----------------------------------------
CREATE INDEX IF NOT EXISTS {TSV_INDEX}
    ON {TABLE}
    USING gin (tsv);

-- 5. supporting indexes for scoping / lifecycle filters -----------------------
CREATE INDEX IF NOT EXISTS memories_bubble_idx ON {TABLE} (bubble);
CREATE INDEX IF NOT EXISTS memories_status_idx ON {TABLE} (status);
"""


def apply_schema(conn) -> None:
    """Apply the DDL idempotently against an open psycopg connection.

    Safe to call on every boot: extension, table, and indexes all use
    ``IF NOT EXISTS``. Commits on success.
    """
    with conn.cursor() as cur:
        cur.execute(DDL)
    conn.commit()
