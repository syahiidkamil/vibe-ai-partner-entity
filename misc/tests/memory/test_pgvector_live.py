"""Live pgvector round-trip — needs a reachable DATABASE_URL (opt in: -m live).

Runs entirely inside a throwaway schema, dropped in teardown, so it can point
at any Postgres without touching real data.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.live

SCHEMA = "vape_test_retrieval"


@pytest.fixture()
def pg_backend(root):
    from engine.memory.factory import load_env, _root_dir
    load_env(_root_dir())
    from vibe_plugin_retrieval_pgvector import PgvectorBackend

    try:
        b = PgvectorBackend(root, {"schema": SCHEMA}, None)
        b.migrate()
    except Exception as e:
        pytest.skip(f"no reachable Postgres: {e}")
    yield b
    conn = b._connect()
    with conn.cursor() as cur:
        cur.execute(f'DROP SCHEMA IF EXISTS "{SCHEMA}" CASCADE')
    conn.commit()


def test_pg_roundtrip(pg_backend, root):
    from engine.memory import derive
    from engine.memory.interface import Query

    rows = []
    for p in derive.all_sources(root):
        rows.extend(derive.derive_file(root, p))
    rep = pg_backend.index(rows)
    assert rep.upserted == len(rows)

    hits = pg_backend.search(Query(text="flux capacitor warm rotation", space="memory"))
    assert hits and any("flux capacitor" in h.memory.content for h in hits)
    assert all(h.source == "fts" for h in hits)   # keyless: no vector leg

    # reconcile: reindex the same rows — still one row per anchor
    rep2 = pg_backend.index(rows)
    assert rep2.upserted == len(rows)
    hits2 = pg_backend.search(Query(text="flux capacitor warm rotation", space="memory"))
    assert {h.memory.id for h in hits2} == {h.memory.id for h in hits}


def test_pg_evict_sources(pg_backend, root):
    from engine.memory import derive
    from engine.memory.interface import Query

    rows = []
    for p in derive.all_sources(root):
        rows.extend(derive.derive_file(root, p))
    pg_backend.index(rows)
    pg_backend.evict_sources(["vape/entity/memory/cases/sample.md"])
    hits = pg_backend.search(Query(text="widget overreach shipped", space="memory", kind="case"))
    assert not hits


def test_pg_schema_introspects(pg_backend):
    s = pg_backend.schema()
    assert "memories" in s and "hnsw" in s.lower()
