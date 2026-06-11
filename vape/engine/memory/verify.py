"""Live end-to-end verification of the memory foundation.

Run: ``uv run python -m engine.memory.verify`` (from repo root, with PYTHONPATH=vape)
or via the ``vape memory verify`` CLI command.

Proves, against the REAL DB and REAL Gemini API — nothing mocked:
  1. config loads; the key is present (shown masked, never raw).
  2. schema applies idempotently.
  3. Gemini returns 3072-dim embeddings.
  4. rows insert with their embeddings.
  5. a vector-similarity query returns the semantically-nearest row first.

It cleans up its own test rows so the corpus is left as it was found.
"""

from __future__ import annotations

from engine.memory import db
from engine.memory.config import (
    EMBED_DIM,
    EMBED_MODEL,
    get_gemini_key,
    mask_secret,
)
from engine.memory.embeddings import embed, embed_one
from engine.memory.schema import TABLE, apply_schema

_TEST_BUBBLE = "_verify_selftest"


def run() -> int:
    print("=== Saori memory foundation — live verification ===\n")

    # 1. config / secret presence (masked) ------------------------------------
    key = get_gemini_key()
    print(f"[1] config       : key loaded = {mask_secret(key)}  model = {EMBED_MODEL}")
    print(f"                   pinned EMBED_DIM = {EMBED_DIM}")

    with db.session() as conn:
        # 2. idempotent schema ------------------------------------------------
        apply_schema(conn)
        apply_schema(conn)  # twice — proves idempotency
        print("[2] schema       : applied idempotently (ran twice, no error)")

        # 3. real embeddings --------------------------------------------------
        docs = [
            "Saori designed her own hippocampus: a self-memory engine on Postgres and pgvector.",
            "The avatar's idle silhouette fringe was a stale macOS window shadow, killed in Tauri.",
            "Kamil needs about seven hours of sleep; melatonin runs the sleep-wake cycle.",
        ]
        doc_vecs = embed(docs, task_type="RETRIEVAL_DOCUMENT")
        print(f"[3] embeddings   : {len(doc_vecs)} docs embedded, dim = {len(doc_vecs[0])}")

        # 4. insert -----------------------------------------------------------
        ids = []
        for text, vec in zip(docs, doc_vecs):
            mem_id = db.insert_memory(
                conn,
                content=text,
                embedding=vec,
                bubble=_TEST_BUBBLE,
                mem_type="episode",
                surprise=0.6,
                viability=0.5,
                source="verify",
            )
            ids.append(mem_id)
        print(f"[4] insert       : {len(ids)} rows inserted, ids = {ids}")

        # 5. vector similarity search ----------------------------------------
        query = "What database did Saori build for her memory?"
        q_vec = embed_one(query, task_type="RETRIEVAL_QUERY")
        results = db.search_similar(
            conn, query_embedding=q_vec, limit=3, bubble=_TEST_BUBBLE
        )
        print(f"\n[5] search       : query = {query!r}")
        for rank, r in enumerate(results, 1):
            print(
                f"      #{rank}  sim={r['similarity']:+.4f}  id={r['id']}  "
                f"{r['content'][:60]!r}"
            )

        # assert the semantically-correct row won
        top = results[0]
        ok = top["content"] == docs[0]
        print(f"\n      top match is the hippocampus/Postgres row : {ok}")

        # confirm the HNSW index is actually USABLE by the planner ------------
        # (With only a few rows a seq scan is correctly cheaper, so we disable
        # seqscan to force the planner to reveal whether it CAN use the index.
        # The ORDER BY must omit the bubble WHERE so the index ordering applies.)
        with conn.cursor() as cur:
            cur.execute("SET LOCAL enable_seqscan = off")
            cur.execute(
                f"""
                EXPLAIN
                SELECT id FROM {TABLE}
                ORDER BY (embedding::halfvec({EMBED_DIM})) <=> (%s::halfvec({EMBED_DIM}))
                LIMIT 3
                """,
                (list(q_vec),),
            )
            plan = "\n".join(row[0] for row in cur.fetchall())
        uses_index = "memories_embedding_hnsw" in plan
        print(f"      HNSW index usable by planner               : {uses_index}")
        if not uses_index:
            print("      --- plan ---")
            print("      " + plan.replace("\n", "\n      "))

        # cleanup -------------------------------------------------------------
        with conn.cursor() as cur:
            cur.execute(f"DELETE FROM {TABLE} WHERE bubble = %s", (_TEST_BUBBLE,))
        conn.commit()
        print("\n[*] cleanup      : test rows removed; corpus left clean")

    # 6. firewall round-trip: hybrid search + write/search/evict ----------------
    fw_ok = _verify_firewall()

    if ok and fw_ok:
        print("\n=== VERIFICATION PASSED ===")
        return 0
    print("\n=== VERIFICATION FAILED ===")
    return 1


_FW_BUBBLE = "_verify_firewall_selftest"


def _verify_firewall() -> bool:
    """Exercise the firewall layer end-to-end against the real DB: the four-verb path
    (write → hybrid search → evict) plus the bookmark spike-store. Leaves the corpus
    and the bookmark file as found. Returns True on success."""
    from engine.memory import bookmarks, db, firewall

    print("\n[6] firewall     : write → hybrid search → evict (live)")
    try:
        # write three rows through the firewall (it embeds + inserts)
        firewall.write(
            "Saori stood up a pgvector Postgres database named saori-hibana for her memory.",
            bubble=_FW_BUBBLE, mem_type="episode", source="verify",
        )
        firewall.write(
            "Kamil needs about seven hours of sleep; melatonin runs the sleep-wake cycle.",
            bubble=_FW_BUBBLE, mem_type="fact", source="verify",
        )
        low_id = firewall.write(
            "A throwaway low-stakes no-growth note that should demote.",
            bubble=_FW_BUBBLE, mem_type="episode", source="verify",
            meta={"axes": {"stakes": 0.0, "context": 0.0, "staleness": 0.0, "growth": 0.0}},
        )

        # hybrid search (RRF over semantic + keyword)
        results = firewall.search(
            "what database did Saori build for her memory?", bubble=_FW_BUBBLE, limit=3
        )
        top = results[0] if results else {}
        hybrid_ok = bool(results) and ("rrf_score" in top) and (
            "saori-hibana" in top.get("content", "") or "pgvector" in top.get("content", "")
        )
        print(f"      hybrid search returns the DB row first + rrf : {hybrid_ok}")

        # creative mode: reaches past the nearest (flagged creative)
        creative = firewall.creative_search(
            "the saori-hibana memory database", bubble=_FW_BUBBLE, limit=2
        )
        creative_ok = bool(creative) and all(r.get("creative") for r in creative)
        print(f"      creative mode returns coherent-but-far rows   : {creative_ok}")

        # evict: the low row demotes but is NOT deleted (cold keeps it)
        with db.session() as conn:
            rows = db.fetch_rows(conn, bubble=_FW_BUBBLE, status="active")
        counts = firewall.evict(rows)
        with db.session() as conn:
            active = db.fetch_rows(conn, bubble=_FW_BUBBLE, status="active")
            demoted = db.fetch_rows(conn, bubble=_FW_BUBBLE, status="demoted")
        evict_ok = (
            counts.get("demote", 0) >= 1
            and all(r["id"] != low_id for r in active)
            and any(r["id"] == low_id for r in demoted)
        )
        print(f"      evict demotes (never deletes; cold keeps it)  : {evict_ok}")

        # bookmark spike store round-trip
        rec = firewall.write_bookmark(
            bubble=_FW_BUBBLE, kind="surprise", surprise=0.8, tone=0.3,
            note="verify spike", ref=None,
        )
        bm = bookmarks.read_all(bubble=_FW_BUBBLE)
        removed = bookmarks.clear([rec["id"]])
        bookmark_ok = len(bm) == 1 and removed == 1
        print(f"      bookmark append/read/clear round-trip          : {bookmark_ok}")

        return hybrid_ok and creative_ok and evict_ok and bookmark_ok
    finally:
        with db.session() as conn:
            with conn.cursor() as cur:
                cur.execute(f"DELETE FROM {TABLE} WHERE bubble = %s", (_FW_BUBBLE,))
            conn.commit()
        print("      cleanup      : firewall test rows removed")


if __name__ == "__main__":
    import sys

    sys.exit(run())
