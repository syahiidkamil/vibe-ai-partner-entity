"""PgvectorBackend — the scale path: Postgres + pgvector (doc 04's tables).

Same dumb-drawer contract as every backend: per-leg ranked candidates out,
no fusion, no usage. Both legs run in ONE round-trip (two CTEs, leg-tagged);
the fuse constant lives in Python (engine ranking), not SQL — doc 11's
amendment to doc 04. Vectors are halfvec(1536) under HNSW, always filtered
to one (surface, model) pair so models never mix.

DATABASE_URL comes from the env var named in config (databaseUrlEnv,
default DATABASE_URL), loaded from vape/.env by the factory. An optional
config 'schema' scopes everything (live tests use a throwaway schema).
"""
from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

from engine.memory.interface import (
    Capabilities,
    Hit,
    IndexReport,
    Memory,
    Query,
    content_hash,
)

_TOKEN_RE = re.compile(r"[a-zA-Z0-9]+")

_DDL = """
CREATE EXTENSION IF NOT EXISTS vector;
CREATE TABLE IF NOT EXISTS memories (
  id TEXT PRIMARY KEY,
  kind TEXT NOT NULL,
  space TEXT NOT NULL,
  content TEXT NOT NULL,
  topic TEXT,
  bubble TEXT,
  created_at TIMESTAMPTZ,
  pointer JSONB NOT NULL,
  meta JSONB NOT NULL DEFAULT '{}',
  provenance TEXT NOT NULL DEFAULT 'sweep',
  source_path TEXT NOT NULL,
  source_hash TEXT NOT NULL,
  content_tsv tsvector GENERATED ALWAYS AS (to_tsvector('english', content)) STORED
);
CREATE INDEX IF NOT EXISTS idx_mem_fts  ON memories USING GIN (content_tsv);
CREATE INDEX IF NOT EXISTS idx_mem_meta ON memories USING GIN (meta);
CREATE INDEX IF NOT EXISTS idx_mem_dims ON memories (space, kind, topic, created_at);
CREATE INDEX IF NOT EXISTS idx_mem_src  ON memories (source_path);
CREATE TABLE IF NOT EXISTS embeddings (
  id BIGSERIAL PRIMARY KEY,
  memory_id TEXT NOT NULL REFERENCES memories(id) ON DELETE CASCADE,
  surface TEXT NOT NULL,
  text TEXT NOT NULL,
  embedding halfvec(1536) NOT NULL,
  model TEXT NOT NULL,
  content_hash TEXT NOT NULL,
  UNIQUE (memory_id, surface, model)
);
CREATE INDEX IF NOT EXISTS idx_emb_hnsw ON embeddings USING hnsw (embedding halfvec_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_emb_sm   ON embeddings (surface, model);
"""


class PgvectorBackend:
    def __init__(self, root_dir: Path, config: dict | None = None, embedder=None):
        import os
        config = config or {}
        self.embedder = embedder
        # namespaced by default: never squat on public (the retired June
        # engine's tables live there in this very repo's db — a same-named
        # table with a different shape breaks CREATE IF NOT EXISTS silently)
        self.schema_name = config.get("schema", "vape_retrieval")
        url_env = config.get("databaseUrlEnv", "DATABASE_URL")
        self.url = os.environ.get(url_env, "")
        if not self.url:
            raise RuntimeError(f"{url_env} is not set (vape/.env)")
        self._conn = None

    # -- lifecycle -----------------------------------------------------------

    def _connect(self):
        if self._conn is None or self._conn.closed:
            import psycopg
            from pgvector.psycopg import register_vector
            self._conn = psycopg.connect(self.url, connect_timeout=5)
            if self.schema_name:
                with self._conn.cursor() as cur:
                    cur.execute(
                        f'CREATE SCHEMA IF NOT EXISTS "{self.schema_name}";'
                        f' SET search_path TO "{self.schema_name}", public')
                self._conn.commit()
            # the vector extension must exist before adapter registration
            with self._conn.cursor() as cur:
                cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
            self._conn.commit()
            register_vector(self._conn)
        return self._conn

    def migrate(self) -> None:
        conn = self._connect()
        with conn.cursor() as cur:
            cur.execute(_DDL)
        conn.commit()

    def reset(self) -> None:
        conn = self._connect()
        with conn.cursor() as cur:
            if self.schema_name:
                cur.execute(f'DROP SCHEMA IF EXISTS "{self.schema_name}" CASCADE')
                cur.execute(
                    f'CREATE SCHEMA "{self.schema_name}";'
                    f' SET search_path TO "{self.schema_name}", public')
            else:
                cur.execute(
                    "DROP TABLE IF EXISTS embeddings; DROP TABLE IF EXISTS memories CASCADE")
        conn.commit()
        self.migrate()

    def capabilities(self) -> Capabilities:
        return Capabilities(
            name="pgvector",
            fts=True,
            vector=self.embedder is not None and getattr(self.embedder, "dim", 0) > 0,
            spaces={"memory", "file"},
            concurrent_writers=True,
            persistent=True,
        )

    def schema(self) -> str:
        conn = self._connect()
        out = []
        with conn.cursor() as cur:
            cur.execute(
                "SELECT table_name, column_name, data_type FROM information_schema.columns"
                " WHERE table_name IN ('memories','embeddings')"
                "   AND table_schema = COALESCE(%s, 'public')"
                " ORDER BY table_name, ordinal_position",
                (self.schema_name,))
            for t, c, d in cur.fetchall():
                out.append(f"{t}.{c}  {d}")
            cur.execute(
                "SELECT indexdef FROM pg_indexes"
                " WHERE tablename IN ('memories','embeddings')"
                "   AND schemaname = COALESCE(%s, 'public') ORDER BY indexname",
                (self.schema_name,))
            out.extend(r[0] for r in cur.fetchall())
        return "\n".join(out)

    # -- write ------------------------------------------------------------------

    def index(self, rows: list[Memory]) -> IndexReport:
        conn = self._connect()
        rep = IndexReport()
        by_source: dict[str, list[Memory]] = {}
        for r in rows:
            by_source.setdefault(r.source_path, []).append(r)
        with conn.cursor() as cur:
            for source, group in by_source.items():
                cur.execute(
                    "DELETE FROM memories WHERE source_path = %s AND NOT (id = ANY(%s))",
                    (source, [r.id for r in group]))
                for r in group:
                    cur.execute(
                        "INSERT INTO memories(id, kind, space, content, topic, bubble,"
                        " created_at, pointer, meta, provenance, source_path, source_hash)"
                        " VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                        " ON CONFLICT (id) DO UPDATE SET kind=EXCLUDED.kind,"
                        " space=EXCLUDED.space, content=EXCLUDED.content,"
                        " topic=EXCLUDED.topic, bubble=EXCLUDED.bubble,"
                        " created_at=EXCLUDED.created_at, pointer=EXCLUDED.pointer,"
                        " meta=EXCLUDED.meta,"
                        " provenance=CASE WHEN memories.provenance='dream'"
                        "   AND EXCLUDED.provenance='sweep' THEN 'dream'"
                        "   ELSE EXCLUDED.provenance END,"
                        " source_path=EXCLUDED.source_path, source_hash=EXCLUDED.source_hash",
                        (
                            r.id, r.kind, r.space, r.content, r.topic, r.bubble,
                            r.created_at,
                            json.dumps(r.pointer, ensure_ascii=False),
                            json.dumps(r.meta, ensure_ascii=False),
                            r.provenance, r.source_path, r.source_hash,
                        ))
                    rep.upserted += 1
        conn.commit()
        if self.capabilities().vector:
            rep.embedded = self._embed_rows([r for r in rows if r.space == "memory"])
        return rep

    def _embed_rows(self, rows: list[Memory]) -> int:
        from pgvector import HalfVector
        conn = self._connect()
        model = self.embedder.model
        todo: list[Memory] = []
        with conn.cursor() as cur:
            for r in rows:
                if not r.content.strip():
                    continue
                cur.execute(
                    "SELECT content_hash FROM embeddings"
                    " WHERE memory_id=%s AND surface='gist' AND model=%s",
                    (r.id, model))
                row = cur.fetchone()
                if row and row[0] == content_hash(r.content):
                    continue
                todo.append(r)
        if not todo:
            return 0
        done = 0
        CHUNK = 100
        for start in range(0, len(todo), CHUNK):
            chunk = todo[start:start + CHUNK]
            vectors = self.embedder.embed([r.content for r in chunk], task="document")
            with conn.cursor() as cur:
                for r, vec in zip(chunk, vectors, strict=True):
                    cur.execute(
                        "INSERT INTO embeddings(memory_id, surface, text, embedding,"
                        " model, content_hash) VALUES (%s,'gist',%s,%s,%s,%s)"
                        " ON CONFLICT (memory_id, surface, model) DO UPDATE SET"
                        " text=EXCLUDED.text, embedding=EXCLUDED.embedding,"
                        " content_hash=EXCLUDED.content_hash",
                        (r.id, r.content, HalfVector(vec), model, content_hash(r.content)))
            conn.commit()
            done += len(chunk)
        return done

    def backfill(self) -> int:
        """Embed stored rows lacking a current-model gist vector (key added
        late, or a model swap) — same in-store reconcile as the sqlite tier."""
        if not self.capabilities().vector:
            return 0
        conn = self._connect()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT m.id, m.kind, m.space, m.content, m.topic, m.bubble, m.created_at,"
                " m.pointer, m.meta, m.provenance, m.source_path, m.source_hash"
                " FROM memories m LEFT JOIN embeddings e"
                "   ON e.memory_id = m.id AND e.surface='gist' AND e.model=%s"
                " WHERE m.space='memory' AND m.content <> '' AND e.id IS NULL",
                (self.embedder.model,))
            rows = [_tuple_to_memory(t) for t in cur.fetchall()]
        return self._embed_rows(rows) if rows else 0

    def evict(self, ids: list[str]) -> None:
        conn = self._connect()
        with conn.cursor() as cur:
            cur.execute("DELETE FROM memories WHERE id = ANY(%s)", (ids,))
        conn.commit()

    def evict_sources(self, source_paths: list[str]) -> None:
        conn = self._connect()
        with conn.cursor() as cur:
            cur.execute("DELETE FROM memories WHERE source_path = ANY(%s)", (source_paths,))
        conn.commit()

    # -- search --------------------------------------------------------------------

    def search(self, q: Query) -> list[Hit]:
        conn = self._connect()
        tokens = _TOKEN_RE.findall(q.text)
        if not tokens:
            return []
        tsquery = " | ".join(tokens)

        filters, params = ["m.space = %s"], [q.space]
        if q.kind:
            filters.append("m.kind = %s")
            params.append(q.kind)
        if q.topic:
            filters.append("m.topic = %s")
            params.append(q.topic)
        if q.bubble:
            filters.append("m.bubble = %s")
            params.append(q.bubble)
        if q.since:
            filters.append("m.created_at >= %s")
            params.append(q.since)
        where = " AND ".join(filters)

        mem_cols = (
            "m.id, m.kind, m.space, m.content, m.topic, m.bubble, m.created_at,"
            " m.pointer, m.meta, m.provenance, m.source_path, m.source_hash"
        )

        use_vec = self.capabilities().vector and q.space == "memory"
        legs_sql = (
            f"SELECT {mem_cols}, 'fts' AS leg,"
            " ROW_NUMBER() OVER (ORDER BY ts_rank_cd(m.content_tsv, tq.q) DESC) AS leg_rank"
            " FROM memories m, to_tsquery('english', %s) tq(q)"
            f" WHERE m.content_tsv @@ tq.q AND {where}"
            " LIMIT %s"
        )
        sql_params: list = [tsquery, *params, q.candidates]

        if use_vec:
            qvec = self.embedder.embed([q.text], task="query")[0]
            from pgvector import HalfVector
            legs_sql = (
                f"({legs_sql}) UNION ALL "
                f"(SELECT {mem_cols}, 'vector' AS leg,"
                " ROW_NUMBER() OVER (ORDER BY e.embedding <=> %s) AS leg_rank"
                " FROM embeddings e JOIN memories m ON m.id = e.memory_id"
                f" WHERE e.surface='gist' AND e.model=%s AND {where}"
                " ORDER BY e.embedding <=> %s LIMIT %s)"
            )
            hv = HalfVector(qvec)
            sql_params += [hv, self.embedder.model, *params, hv, q.candidates]

        hits: list[Hit] = []
        with conn.cursor() as cur:
            cur.execute(legs_sql, sql_params)   # one round-trip, both legs
            for row in cur.fetchall():
                hits.append(Hit(
                    memory=_tuple_to_memory(row[:12]),
                    source=row[12], leg_rank=int(row[13]),
                ))
        return hits


def _tuple_to_memory(t) -> Memory:
    created = t[6]
    if isinstance(created, str):
        try:
            created = datetime.fromisoformat(created)
        except ValueError:
            created = None
    pointer = t[7] if isinstance(t[7], dict) else json.loads(t[7])
    meta = t[8] if isinstance(t[8], dict) else json.loads(t[8])
    return Memory(
        id=t[0], kind=t[1], space=t[2], content=t[3], topic=t[4], bubble=t[5],
        created_at=created, pointer=pointer, meta=meta,
        provenance=t[9], source_path=t[10], source_hash=t[11],
    )
