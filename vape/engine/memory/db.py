"""DB connection + the thin store layer (insert / vector-search).

psycopg 3 + pgvector's psycopg adapter. ``connect()`` opens a connection and registers
the ``vector`` type so Python lists round-trip as pgvector values. The store helpers are
the concrete ``write`` and ``search`` primitives from the spec's thin layer; consolidate
and evict are built downstream on top of these.

Search is **vector similarity** via cosine distance (``<=>``), run through the halfvec
index by casting both the column and the query vector to ``halfvec`` — matching the
index built in ``schema.py`` so the planner actually uses it.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Iterator, Optional, Sequence

import psycopg
from pgvector.psycopg import register_vector

from engine.memory.config import EMBED_DIM, get_database_url
from engine.memory.schema import TABLE


def connect(*, autocommit: bool = False) -> psycopg.Connection:
    """Open a psycopg connection to the corpus DB with pgvector registered.

    The caller owns the connection's lifetime (close it, or use ``session()``).
    """
    conn = psycopg.connect(get_database_url(), autocommit=autocommit)
    register_vector(conn)
    return conn


@contextmanager
def session(*, autocommit: bool = False) -> Iterator[psycopg.Connection]:
    """Connection as a context manager: registers vector, closes on exit."""
    conn = connect(autocommit=autocommit)
    try:
        yield conn
    finally:
        conn.close()


def insert_memory(
    conn: psycopg.Connection,
    *,
    content: str,
    embedding: Sequence[float],
    bubble: str = "global",
    mem_type: str = "episode",
    surprise: float = 0.0,
    viability: float = 0.0,
    source: Optional[str] = None,
    meta: Optional[dict] = None,
) -> int:
    """Insert one corpus row (the ``write`` primitive). Returns its id.

    Validates the embedding length against the pinned dimension so a wrong-sized
    vector fails loudly here rather than silently corrupting the index.
    """
    if len(embedding) != EMBED_DIM:
        raise ValueError(
            f"embedding has {len(embedding)} dims, expected {EMBED_DIM} (the pinned dim)"
        )
    import json

    with conn.cursor() as cur:
        cur.execute(
            f"""
            INSERT INTO {TABLE}
                (content, embedding, bubble, mem_type, surprise, viability, source, meta)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s::jsonb)
            RETURNING id
            """,
            (
                content,
                list(embedding),
                bubble,
                mem_type,
                surprise,
                viability,
                source,
                json.dumps(meta or {}),
            ),
        )
        row = cur.fetchone()
    conn.commit()
    return int(row[0])


def search_similar(
    conn: psycopg.Connection,
    *,
    query_embedding: Sequence[float],
    limit: int = 5,
    bubble: Optional[str] = None,
) -> list[dict[str, Any]]:
    """Vector-similarity search (the ``search`` primitive, semantic half).

    Cosine distance via ``<=>`` on the halfvec cast so the HNSW index is used.
    Returns rows ordered nearest-first, each with a ``distance`` (0 = identical)
    and ``similarity`` (1 - distance). Filters to a bubble if given.
    """
    if len(query_embedding) != EMBED_DIM:
        raise ValueError(
            f"query embedding has {len(query_embedding)} dims, expected {EMBED_DIM}"
        )

    where = ""
    params: list[Any] = [list(query_embedding)]
    if bubble is not None:
        where = "WHERE bubble = %s"
        params.append(bubble)
    params.append(limit)

    sql = f"""
        SELECT
            id,
            content,
            bubble,
            mem_type,
            surprise,
            viability,
            (embedding::halfvec({EMBED_DIM})) <=> (%s::halfvec({EMBED_DIM})) AS distance
        FROM {TABLE}
        {where}
        ORDER BY distance ASC
        LIMIT %s
    """
    with conn.cursor() as cur:
        cur.execute(sql, params)
        cols = [d.name for d in cur.description]
        rows = [dict(zip(cols, r)) for r in cur.fetchall()]

    for r in rows:
        r["similarity"] = 1.0 - float(r["distance"])
    return rows


# --- the keyword + hybrid + lifecycle helpers (firewall-core extends in place) ----
#
# These are the downstream pieces the manifest assigns to db.py: the lexical half of
# hybrid search, the RRF blend that fuses it with the semantic half, and the row
# update / tombstone helpers eviction needs (status flips and validity windows —
# never a DELETE; cold keeps everything).

_ACTIVE_ONLY = "status = 'active'"


def search_keyword(
    conn: psycopg.Connection,
    *,
    query: str,
    limit: int = 5,
    bubble: Optional[str] = None,
    active_only: bool = True,
) -> list[dict[str, Any]]:
    """Full-text (lexical) search — the keyword half of hybrid.

    Uses the generated ``tsv`` column + its GIN index, ranked by ``ts_rank_cd``.
    ``plainto_tsquery`` parses the user's words safely (no operator injection).
    Returns rows best-match-first, each with a ``rank`` (higher = better).
    Empty/whitespace queries return ``[]`` (plainto_tsquery would match nothing).
    """
    if not query or not query.strip():
        return []

    # Build the WHERE clause and its params first, then assemble the full param list in
    # SQL-TEXT order: positional %s placeholders bind in the order they appear in the
    # statement, so the SELECT's rank-tsquery (first in the text) must be the first param,
    # then the WHERE params (tsquery, bubble), then LIMIT. (This ordering was the bug the
    # live keyword test caught — the rank %s was being fed the bubble name.)
    clauses: list[str] = ["tsv @@ plainto_tsquery('english', %s)"]
    where_params: list[Any] = [query]
    if bubble is not None:
        clauses.append("bubble = %s")
        where_params.append(bubble)
    if active_only:
        clauses.append(_ACTIVE_ONLY)
    where = " AND ".join(clauses)

    sql = f"""
        SELECT
            id,
            content,
            bubble,
            mem_type,
            surprise,
            viability,
            ts_rank_cd(tsv, plainto_tsquery('english', %s)) AS rank
        FROM {TABLE}
        WHERE {where}
        ORDER BY rank DESC
        LIMIT %s
    """
    params: list[Any] = [query, *where_params, limit]
    with conn.cursor() as cur:
        cur.execute(sql, params)
        cols = [d.name for d in cur.description]
        rows = [dict(zip(cols, r)) for r in cur.fetchall()]
    return rows


def rrf_blend(
    *rankings: Sequence[dict[str, Any]],
    k: int = 60,
    weights: Optional[Sequence[float]] = None,
    limit: int = 5,
) -> list[dict[str, Any]]:
    """Reciprocal-Rank Fusion across one-or-more ranked result lists.

    RRF score of a row = Σ_list  weight_list / (k + rank_in_list). It fuses by *rank
    position*, not by raw score, so the wildly different scales of cosine-similarity
    and ts_rank never need normalizing — the canonical reason hybrid search uses RRF.
    ``k`` (default 60, the standard) damps the contribution of low ranks.

    Rows are matched across lists by ``id``. The merged row carries an ``rrf_score``
    and the per-list ranks it was found at (``ranks``), for debugging/explainability.
    Returns the top ``limit`` fused rows, best-first.
    """
    if weights is None:
        weights = [1.0] * len(rankings)
    if len(weights) != len(rankings):
        raise ValueError("weights must match the number of rankings")

    fused: dict[Any, dict[str, Any]] = {}
    for li, ranking in enumerate(rankings):
        w = weights[li]
        for pos, row in enumerate(ranking):
            rid = row["id"]
            contribution = w / (k + pos + 1)  # pos is 0-based; rank is 1-based
            if rid not in fused:
                merged = dict(row)
                merged["rrf_score"] = 0.0
                merged["ranks"] = {}
                fused[rid] = merged
            else:
                # keep whichever copy has the most columns (semantic carries distance,
                # keyword carries rank) — merge missing keys so both signals survive.
                for kk, vv in row.items():
                    fused[rid].setdefault(kk, vv)
            fused[rid]["rrf_score"] += contribution
            fused[rid]["ranks"][li] = pos + 1

    ordered = sorted(fused.values(), key=lambda r: r["rrf_score"], reverse=True)
    return ordered[:limit]


def fetch_rows(
    conn: psycopg.Connection,
    *,
    bubble: Optional[str] = None,
    status: Optional[str] = "active",
    mem_type: Optional[str] = None,
    limit: Optional[int] = None,
) -> list[dict[str, Any]]:
    """Fetch corpus rows by scope/lifecycle filters (no vector op).

    The read side eviction uses to pull candidate rows for the salience pass, and the
    dream uses to replay. Returns full rows incl. ``meta`` (parsed dict) and timestamps.
    """
    clauses: list[str] = []
    params: list[Any] = []
    if bubble is not None:
        clauses.append("bubble = %s")
        params.append(bubble)
    if status is not None:
        clauses.append("status = %s")
        params.append(status)
    if mem_type is not None:
        clauses.append("mem_type = %s")
        params.append(mem_type)
    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    tail = ""
    if limit is not None:
        tail = "LIMIT %s"
        params.append(limit)

    sql = f"""
        SELECT id, content, bubble, mem_type, surprise, viability,
               status, promoted_to, source, meta, valid_from, valid_to,
               created_at, updated_at
        FROM {TABLE}
        {where}
        ORDER BY created_at DESC
        {tail}
    """
    with conn.cursor() as cur:
        cur.execute(sql, params)
        cols = [d.name for d in cur.description]
        rows = [dict(zip(cols, r)) for r in cur.fetchall()]
    return rows


def update_row(
    conn: psycopg.Connection,
    row_id: int,
    *,
    viability: Optional[float] = None,
    surprise: Optional[float] = None,
    meta: Optional[dict] = None,
    content: Optional[str] = None,
) -> None:
    """Update mutable fields on a row (viability set by the dream, meta annotations).

    Bumps ``updated_at``. Does NOT touch ``status`` or validity — that is what the
    tombstone helper is for, kept separate so a value-update can never accidentally
    retire a row.
    """
    sets: list[str] = ["updated_at = now()"]
    params: list[Any] = []
    if viability is not None:
        sets.append("viability = %s")
        params.append(viability)
    if surprise is not None:
        sets.append("surprise = %s")
        params.append(surprise)
    if content is not None:
        sets.append("content = %s")
        params.append(content)
    if meta is not None:
        import json

        sets.append("meta = %s::jsonb")
        params.append(json.dumps(meta))
    if len(sets) == 1:  # only updated_at — nothing to do
        return
    params.append(row_id)
    with conn.cursor() as cur:
        cur.execute(
            f"UPDATE {TABLE} SET {', '.join(sets)} WHERE id = %s",
            params,
        )
    conn.commit()


def tombstone_row(
    conn: psycopg.Connection,
    row_id: int,
    *,
    status: str = "superseded",
    promoted_to: Optional[str] = None,
    close_validity: bool = True,
) -> None:
    """Retire a row WITHOUT deleting it — the never-silent-delete primitive.

    Flips ``status`` to ``superseded`` (default) or ``demoted``, optionally records the
    git path it was ``promoted_to``, and closes its validity window (``valid_to = now``).
    The row stays in cold storage for the temporal graph ("when did this change / why
    did I believe it"). Cold keeps everything; thinking just stops reaching for it.
    """
    if status not in ("superseded", "demoted", "active"):
        raise ValueError(f"unexpected status {status!r}")
    sets = ["status = %s", "updated_at = now()"]
    params: list[Any] = [status]
    if close_validity:
        sets.append("valid_to = now()")
    if promoted_to is not None:
        sets.append("promoted_to = %s")
        params.append(promoted_to)
    params.append(row_id)
    with conn.cursor() as cur:
        cur.execute(
            f"UPDATE {TABLE} SET {', '.join(sets)} WHERE id = %s",
            params,
        )
    conn.commit()
