"""Live round-trip tests for the firewall-core component.

Honesty floor (the task's hard rule): a claim that the firewall "works" is earned ONLY
by these passing against the REAL Postgres + pgvector + the REAL Gemini embedding API —
nothing mocked. The salience policy tests are pure (no I/O) and always run.

The DB-touching tests scope every row to a unique throwaway bubble and tear it down in a
fixture, so the live corpus is left exactly as found. If the DB or Gemini is unreachable
the live tests fail loudly (they do not silently skip) — a green run means the path was
exercised end to end.
"""

from __future__ import annotations

import uuid

import pytest

from engine.memory import bookmarks, db, firewall, salience


# ---------------------------------------------------------------------------------
# PURE — salience policy (no DB, always runs)
# ---------------------------------------------------------------------------------
def test_gate1_predicted_event_is_let_go():
    """A fully-predicted event (pred_error 0) keeps its pull and stays below threshold
    when that pull is modest — Gate 1 lets the un-surprising go."""
    boosted, should = salience.gate1_surprise(0.4, 0.0)
    assert boosted == pytest.approx(0.4)
    assert should is False


def test_gate1_surprise_boosts_and_crosses_threshold():
    """A surprising event boosts pull above the bookmark threshold."""
    boosted, should = salience.gate1_surprise(0.5, 1.0)
    assert boosted > 0.5
    assert should is True


def test_gate1_clips_to_unit_interval():
    boosted, _ = salience.gate1_surprise(0.9, 1.0)
    assert 0.0 <= boosted <= 1.0


def test_gate2_growth_weighted_highest():
    """Growth dominates: a high-growth/low-stakes row scores higher than a
    high-stakes/low-growth one, all else equal — the divergence from biology."""
    growth_heavy = salience.gate2_viability(stakes=0.1, context=0.5, staleness=0.0, growth=0.9)
    stakes_heavy = salience.gate2_viability(stakes=0.5, context=0.5, staleness=0.0, growth=0.1)
    assert growth_heavy > stakes_heavy


def test_gate2_staleness_subtracts():
    fresh = salience.gate2_viability(stakes=0.5, context=0.5, staleness=0.0, growth=0.5)
    stale = salience.gate2_viability(stakes=0.5, context=0.5, staleness=0.9, growth=0.5)
    assert stale < fresh


def test_gate2_high_stakes_is_floored():
    """A catastrophe-averter (stakes >= floor) never scores into eviction even if every
    other axis is zero."""
    score = salience.gate2_viability(stakes=0.95, context=0.0, staleness=0.0, growth=0.0)
    assert score >= salience.VIABILITY_KEEP


def test_eviction_actions_cover_the_fates():
    """eviction_action returns the right fate for each shaped row, and NEVER 'delete'."""
    # stale → revise (checked before the budget)
    assert salience.eviction_action({"meta": {"axes": {"staleness": 0.9}}}) == "revise"
    # floored stakes → keep
    assert salience.eviction_action({"meta": {"axes": {"stakes": 0.95}}}) == "keep"
    # low viability, thin → demote
    assert (
        salience.eviction_action(
            {"meta": {"axes": {"stakes": 0.0, "context": 0.0, "growth": 0.0, "staleness": 0.0}}}
        )
        == "demote"
    )
    # high viability + general scope → promote (axes must clear PROMOTE_VIABILITY=0.85)
    assert (
        salience.eviction_action(
            {"meta": {"scope": "any", "axes": {"stakes": 0.9, "context": 1.0, "growth": 1.0, "staleness": 0.0}}}
        )
        == "promote"
    )
    # duplicate flag → merge
    assert (
        salience.eviction_action(
            {"meta": {"duplicate_of": 7, "axes": {"stakes": 0.5, "context": 0.5, "growth": 0.5, "staleness": 0.0}}}
        )
        == "merge"
    )


# ---------------------------------------------------------------------------------
# FILE — bookmarks (touches the real bookmarks.jsonl, isolated by unique ids)
# ---------------------------------------------------------------------------------
def test_bookmark_append_read_clear_roundtrip():
    tag = f"_pytest_bm_{uuid.uuid4().hex[:8]}"
    rec = firewall.write_bookmark(
        bubble=tag, kind="surprise", surprise=0.8, tone=0.3, note="a live spike", ref="g1#m1"
    )
    assert rec["id"] and rec["ts"]

    found = bookmarks.read_all(bubble=tag)
    assert len(found) == 1
    assert found[0]["note"] == "a live spike"
    assert found[0]["surprise"] == 0.8

    removed = bookmarks.clear([rec["id"]])
    assert removed == 1
    assert bookmarks.read_all(bubble=tag) == []


# ---------------------------------------------------------------------------------
# LIVE DB — the write → search → evict round-trip (real Postgres + real Gemini)
# ---------------------------------------------------------------------------------
@pytest.fixture
def live_bubble():
    """A throwaway bubble; every row tagged with it is deleted on teardown so the live
    corpus is left as found. (DELETE here is test-teardown housekeeping, NOT the engine's
    eviction path — eviction never deletes.)"""
    tag = f"_pytest_fw_{uuid.uuid4().hex[:8]}"
    yield tag
    with db.session() as conn:
        with conn.cursor() as cur:
            cur.execute(f"DELETE FROM {db.TABLE} WHERE bubble = %s", (tag,))
        conn.commit()


def test_write_then_hybrid_search_finds_it(live_bubble):
    """write() embeds + inserts; search() hybrid-retrieves the right row first."""
    firewall.write(
        "Saori stood up a pgvector Postgres database named saori-hibana for her memory.",
        bubble=live_bubble, mem_type="episode", source="pytest",
    )
    firewall.write(
        "The avatar's idle white fringe was a stale macOS window shadow, killed in the Tauri shell.",
        bubble=live_bubble, mem_type="episode", source="pytest",
    )
    firewall.write(
        "Kamil needs about seven hours of sleep; melatonin runs the sleep-wake cycle.",
        bubble=live_bubble, mem_type="fact", source="pytest",
    )

    results = firewall.search(
        "what database did Saori build for her memory?", bubble=live_bubble, limit=3
    )
    assert results, "hybrid search returned nothing"
    top = results[0]
    assert "saori-hibana" in top["content"] or "pgvector" in top["content"]
    assert "rrf_score" in top  # confirms the RRF blend actually ran


def test_keyword_half_matches_on_exact_term(live_bubble):
    """The lexical (FTS) half finds a row by an exact rare term even when phrased oddly,
    and the hybrid fuses it in — proves the keyword index path, not just the vector one."""
    firewall.write(
        "The HNSW halfvec index is the only path pgvector supports above 2000 dimensions.",
        bubble=live_bubble, mem_type="lesson", source="pytest",
    )
    with db.session() as conn:
        kw = db.search_keyword(conn, query="halfvec HNSW", bubble=live_bubble, limit=3)
    assert kw, "keyword search found nothing for an exact term"
    assert "halfvec" in kw[0]["content"]


def test_creative_search_reaches_past_the_nearest(live_bubble):
    """Creative mode returns the farthest-but-still-coherent row, distinct ordering from
    the nearest-neighbour result — the bridge, not the echo."""
    # three rows on one theme at varying distance from the query
    firewall.write(
        "Chess: a sharp open attack sacrifices a pawn for the initiative.",
        bubble=live_bubble, mem_type="episode", source="pytest",
    )
    firewall.write(
        "Chess: a solid closed setup trades tempo for a safe king and a long game.",
        bubble=live_bubble, mem_type="episode", source="pytest",
    )
    firewall.write(
        "Improvisation in jazz also trades a safe plan for the thrill of the open line.",
        bubble=live_bubble, mem_type="episode", source="pytest",
    )
    q = "the aggressive sacrificial attacking style in chess"
    nearest = firewall.search(q, bubble=live_bubble, limit=3)
    creative = firewall.creative_search(q, bubble=live_bubble, limit=3)
    assert creative, "creative search returned nothing"
    assert all(r.get("creative") for r in creative)
    # the nearest top and the creative top should differ — creative reaches past the echo
    if not creative[0].get("creative_degraded"):
        assert creative[0]["id"] != nearest[0]["id"]


def test_evict_demotes_low_viability_without_deleting(live_bubble):
    """evict() devalues a low-viability row to 'demoted' and the row STILL EXISTS in cold
    storage — the never-silent-delete guarantee, proven live."""
    rid = firewall.write(
        "A throwaway, low-stakes, no-growth note that should be demoted.",
        bubble=live_bubble, mem_type="episode", source="pytest",
        meta={"axes": {"stakes": 0.0, "context": 0.0, "staleness": 0.0, "growth": 0.0}},
    )
    with db.session() as conn:
        rows = db.fetch_rows(conn, bubble=live_bubble, status="active")
    counts = firewall.evict(rows)
    assert counts["demote"] >= 1

    # the row is gone from ACTIVE but still present in cold (status='demoted').
    with db.session() as conn:
        active = db.fetch_rows(conn, bubble=live_bubble, status="active")
        demoted = db.fetch_rows(conn, bubble=live_bubble, status="demoted")
    assert all(r["id"] != rid for r in active), "demoted row still active"
    assert any(r["id"] == rid for r in demoted), "row was lost — eviction must never delete"


def test_evict_keeps_high_stakes_floored(live_bubble):
    """A high-stakes row survives eviction (the catastrophe-averter is floored)."""
    rid = firewall.write(
        "Never push a 3am screen on Kamil — it wrecks both melatonin and his sleep. High stakes.",
        bubble=live_bubble, mem_type="lesson", source="pytest",
        meta={"axes": {"stakes": 0.95, "context": 0.5, "staleness": 0.0, "growth": 0.3}},
    )
    with db.session() as conn:
        rows = db.fetch_rows(conn, bubble=live_bubble, status="active")
    firewall.evict(rows)
    with db.session() as conn:
        active = db.fetch_rows(conn, bubble=live_bubble, status="active")
    assert any(r["id"] == rid for r in active), "a floored high-stakes row must be kept"
