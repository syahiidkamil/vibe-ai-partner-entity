"""The firewall — the four-verb stable interface to the corpus.

    write · search · consolidate · evict

This is the ONLY module the other layers (bubble, soul, dream, the CLI) call for corpus
operations. Everything beneath it — psycopg, pgvector, Gemini, the salience math — is
swappable without any caller changing a line. That is the whole point of the firewall:
a thin, stable orchestration seam, so the implementation can be rebuilt under it.

Responsibilities (firewall-core's, per the manifest):
- ``write``       — embed content (RETRIEVAL_DOCUMENT) → insert a corpus row.
- ``search``      — HYBRID: semantic (pgvector) + lexical (FTS), RRF-blended. Plus a
                    CREATIVE mode that reaches for the farthest-but-still-coherent row
                    instead of the nearest neighbour (the bridge, not the echo).
- ``consolidate`` — delegate to the dream (``dream.light_dream`` / ``deep_dream``).
- ``evict``       — apply the Gate-2 salience policy per row → keep/merge/demote/revise/
                    promote, enacted via status flips + validity windows. NEVER deletes.
- ``write_bookmark`` — persist a Gate-1 spike out of the qualia river at spike-time.

The dependency direction is strict: firewall imports foundation (db, embeddings) and its
own siblings (salience, bookmarks). It imports ``dream`` LAZILY inside ``consolidate`` so
the acyclic layering holds (dream sits above firewall and imports it).
"""

from __future__ import annotations

from typing import Any, Optional

from engine.memory import bookmarks, db, salience
from engine.memory.embeddings import embed_one


# ----------------------------------------------------------------------------------
# WRITE
# ----------------------------------------------------------------------------------
def write(
    content: str,
    *,
    bubble: str = "global",
    mem_type: str = "episode",
    surprise: float = 0.0,
    viability: float = 0.0,
    source: Optional[str] = None,
    meta: Optional[dict] = None,
) -> int:
    """Embed ``content`` (task RETRIEVAL_DOCUMENT) and insert one corpus row.

    Returns the new row id. The embedding is generated here, once, at the firewall so no
    caller ever has to know about the embedding client. ``bubble`` is the scope tag,
    ``mem_type`` the kind (episode/lesson/fact/relational/reverie/bookmark/axis), and the
    two salience fields default to 0 (the dream sets viability later).
    """
    if not content or not content.strip():
        raise ValueError("write() needs non-empty content")
    vec = embed_one(content, task_type="RETRIEVAL_DOCUMENT")
    with db.session() as conn:
        return db.insert_memory(
            conn,
            content=content,
            embedding=vec,
            bubble=bubble,
            mem_type=mem_type,
            surprise=surprise,
            viability=viability,
            source=source,
            meta=meta,
        )


# ----------------------------------------------------------------------------------
# SEARCH  (hybrid normal mode + creative mode)
# ----------------------------------------------------------------------------------
def search(
    query: str,
    *,
    bubble: Optional[str] = None,
    limit: int = 5,
    alpha: float = 0.5,
    creative: bool = False,
) -> list[dict[str, Any]]:
    """Hybrid retrieval: semantic (pgvector) + lexical (FTS), RRF-blended, nearest-first.

    The query is embedded once with task RETRIEVAL_QUERY (asymmetric retrieval — the
    matched task type to the documents' RETRIEVAL_DOCUMENT). The semantic and keyword
    rankings are fused by Reciprocal-Rank Fusion, which combines by *rank position* so
    the incomparable scales of cosine-similarity and ts_rank never need normalizing.
    ``alpha`` tilts the fusion weight toward semantic (alpha) vs lexical (1-alpha).

    ``creative=True`` flips the goal: instead of the nearest neighbour it reaches for the
    **farthest-but-still-coherent** row — the lateral bridge, not the echo. See
    ``creative_search``. Files-only fallback (DB down) is a caller concern (grep); here we
    surface the DB error rather than pretend.
    """
    if creative:
        return creative_search(query, bubble=bubble, limit=limit)
    if not query or not query.strip():
        return []

    q_vec = embed_one(query, task_type="RETRIEVAL_QUERY")
    # over-fetch each half so the RRF blend has depth to fuse from.
    pool = max(limit * 4, 20)
    with db.session() as conn:
        semantic = db.search_similar(
            conn, query_embedding=q_vec, limit=pool, bubble=bubble
        )
        lexical = db.search_keyword(
            conn, query=query, limit=pool, bubble=bubble
        )

    fused = db.rrf_blend(
        semantic,
        lexical,
        weights=[alpha, 1.0 - alpha],
        limit=limit,
    )
    return fused


def creative_search(
    query: str,
    *,
    bubble: Optional[str] = None,
    limit: int = 5,
    candidate_pool: int = 80,
    near_floor: float = 0.55,
    relative_band: float = 0.25,
) -> list[dict[str, Any]]:
    """Creative mode — the farthest-but-still-coherent, the bridge not the echo.

    Nearest-neighbour search returns the rows that merely *restate* the query; creative
    mode wants the rows that are *related enough to cohere yet far enough to surprise* —
    the lateral leap a ``cr`` qualia seed makes (loop→breadcrumb→door). Implementation:

    1. Pull a generous candidate pool by semantic similarity (the coherence gate — a row
       must clear the coherence threshold, else it is unrelated noise, not a bridge).
    2. Re-rank that pool by *distance* (1 - similarity) — farthest first — so the top
       results are the most distant rows that are still on-topic.

    The coherence threshold is the MAX of two gates, so it self-calibrates to the corpus
    and never admits noise just because the absolute floor was set low:
      - ABSOLUTE ``near_floor`` — this embedding model scores genuinely-unrelated text
        around 0.4-0.5 cosine (not near 0), so the floor must sit ABOVE that band or pure
        noise tops the farthest-first sort. Default 0.55 is just above the noise band.
      - RELATIVE ``relative_band`` — also require a row to sit within ``relative_band``
        of the *nearest* hit's similarity, so a query whose whole neighbourhood is loose
        still excludes the rows that are merely the least-unrelated noise.

    The result is the edge of the coherent neighbourhood: still about the query, but the
    surprising part of it. Coherence threshold first, then maximize distance — the formal
    shape of "the farthest that still makes sense."
    """
    if not query or not query.strip():
        return []
    q_vec = embed_one(query, task_type="RETRIEVAL_QUERY")
    with db.session() as conn:
        pool = db.search_similar(
            conn, query_embedding=q_vec, limit=candidate_pool, bubble=bubble
        )
    # coherence gate: drop rows too far to be a bridge (unrelated, not lateral). The
    # threshold is the stricter of an absolute floor (above this model's noise band) and
    # a relative band below the nearest hit (self-calibrating to a loose neighbourhood).
    nearest_sim = max((r.get("similarity", 0.0) for r in pool), default=0.0)
    threshold = max(near_floor, nearest_sim - relative_band)
    coherent = [r for r in pool if r.get("similarity", 0.0) >= threshold]
    if not coherent:
        # nothing clears the floor — fall back to the nearest few so we never return
        # empty when matter exists; flag them so the caller knows it's a degrade.
        coherent = pool[:limit]
        for r in coherent:
            r["creative_degraded"] = True
    # farthest-but-coherent: sort by descending distance (ascending similarity).
    coherent.sort(key=lambda r: r.get("similarity", 0.0))
    out = coherent[:limit]
    for r in out:
        r["creative"] = True
    return out


# ----------------------------------------------------------------------------------
# CONSOLIDATE  (delegates to the dream — imported lazily to keep layering acyclic)
# ----------------------------------------------------------------------------------
def consolidate(*, deep: bool = False) -> dict[str, Any]:
    """Run the dream: ``deep_dream`` if ``deep`` else ``light_dream``.

    Imported lazily because ``dream`` sits ABOVE the firewall in the dependency graph
    (it imports firewall, soul, salience) — a top-level import here would be a cycle.
    Returns whatever the dream reports (``{written, merged, demoted, reveries, ...}``).
    Until the dream lands, this raises a clear NotImplementedError rather than a cryptic
    ImportError, so a caller knows the verb is wired but the organ is not built yet.
    """
    try:
        from engine.memory import dream  # lazy: dream is an upper layer
    except ImportError as e:  # pragma: no cover — only before dream.py exists
        raise NotImplementedError(
            "consolidate() delegates to engine.memory.dream, which is not built yet"
        ) from e
    return dream.deep_dream() if deep else dream.light_dream()


# ----------------------------------------------------------------------------------
# EVICT  (the salience policy, enacted via tombstone/update — never DELETE)
# ----------------------------------------------------------------------------------
def evict(rows: Optional[list[dict[str, Any]]] = None) -> dict[str, Any]:
    """Apply Gate-2 salience per row → an action each, enacted without ever deleting.

    If ``rows`` is None, the active corpus is scanned. For each row, ``salience.
    eviction_action`` chooses keep|merge|demote|revise|promote:

      - ``keep``    — left active, viability score refreshed on the row.
      - ``demote``  — status → 'demoted', validity closed. It drops out of active search
                      but stays in cold storage forever (Funes lives safely in cold).
      - ``revise``  — flagged for the molten reading (meaning rewritten, fact kept). Here
                      we mark it; the dream does the actual re-reading. Stays active.
      - ``merge``   — flagged as a near-duplicate to fold; the dream performs the merge.
      - ``promote`` — flagged as a candidate to lift toward the judge-book. PROPOSE-only
                      if it would move a set-point — this verb only flags, never writes
                      into the self-tree.

    Returns a count per action. **No row is ever DELETEd** — eviction is devaluation, the
    lion setting a memory down, not a cleanup job. Cold keeps everything.
    """
    counts = {"keep": 0, "merge": 0, "demote": 0, "revise": 0, "promote": 0}
    with db.session() as conn:
        candidates = rows if rows is not None else db.fetch_rows(conn, status="active")
        for row in candidates:
            action = salience.eviction_action(row)
            counts[action] = counts.get(action, 0) + 1
            rid = int(row["id"])

            if action == "keep":
                # refresh the stored viability so search/budget see the current score.
                s, c, st, g = salience._axes_from_row(row)
                db.update_row(conn, rid, viability=salience.gate2_viability(s, c, st, g))

            elif action == "demote":
                db.tombstone_row(conn, rid, status="demoted", close_validity=True)

            elif action in ("revise", "merge", "promote"):
                # flag in meta for the dream to act on; the row stays active meanwhile.
                meta = row.get("meta") or {}
                if isinstance(meta, str):
                    import json

                    try:
                        meta = json.loads(meta)
                    except Exception:
                        meta = {}
                meta = dict(meta)
                meta["pending_action"] = action
                db.update_row(conn, rid, meta=meta)

    return counts


# ----------------------------------------------------------------------------------
# WRITE_BOOKMARK  (the Gate-1 spike persistor — plugs the river FIFO leak)
# ----------------------------------------------------------------------------------
def write_bookmark(
    *,
    bubble: str,
    kind: str,
    surprise: float,
    tone: float,
    note: str,
    ref: Optional[str] = None,
) -> dict[str, Any]:
    """Persist a qualia spike out of the river at spike-time → ``bookmarks.jsonl``.

    The river is FIFO ~7 deep and drops the oldest each turn; the dream fires many turns
    later. So a Gate-1 spike is appended to the durable bookmark store the instant it
    happens, tagged with ``bubble`` + ``kind`` + ``surprise``, or it ages out unseen.
    This is the encode→bookmark→dream chain's persistence link. Returns the written
    record (with its minted id + ts).
    """
    return bookmarks.append(
        {
            "bubble": bubble,
            "kind": kind,
            "surprise": float(surprise),
            "tone": float(tone),
            "note": note,
            "ref": ref,
        }
    )
