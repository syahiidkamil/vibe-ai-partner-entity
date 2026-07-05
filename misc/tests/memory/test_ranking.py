"""The rank policy: RRF fusion, the capped whisper, decay, challengers, explore."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from engine.memory import ranking
from engine.memory.interface import Hit, Memory

NOW = datetime(2026, 7, 5, tzinfo=timezone.utc)


def _mem(i: str) -> Memory:
    return Memory(
        id=i, kind="note", space="memory", content=f"row {i}",
        pointer={"file": "x.md", "anchor": i}, source_path="x.md", source_hash="h",
    )


def _hit(i: str, source: str, rank: int) -> Hit:
    return Hit(memory=_mem(i), source=source, leg_rank=rank)


def test_fuse_dedups_across_legs():
    legs = [_hit("a", "fts", 1), _hit("a", "vector", 2), _hit("b", "fts", 2)]
    out = ranking.fuse(legs, {}, k=4, now=NOW)
    ids = [s.hit.memory.id for s in out]
    assert ids.count("a") == 1
    assert set(out[0].sources) >= {"fts"}


def test_two_leg_agreement_outranks_single_leg():
    legs = [_hit("a", "fts", 2), _hit("a", "vector", 2), _hit("b", "fts", 1)]
    out = ranking.fuse(legs, {}, k=4, now=NOW)
    assert out[0].hit.memory.id == "a"


def test_strength_is_capped():
    u = ranking.UsageRow(helped=10_000, last_recalled_at=NOW)
    assert ranking.strength(u, NOW) <= ranking.STRENGTH_CAP


def test_strength_decays():
    fresh = ranking.UsageRow(helped=5, last_recalled_at=NOW)
    old = ranking.UsageRow(helped=5, last_recalled_at=NOW - timedelta(days=28))
    assert ranking.strength(old, NOW) < ranking.strength(fresh, NOW) / 2


def test_strength_cannot_outshout_relevance():
    # b is far more relevant; a has maximal strength — b must still win
    legs = [_hit("b", "fts", 1), _hit("a", "fts", 40)]
    usage = {"a": ranking.UsageRow(helped=10_000, recalled=50, last_recalled_at=NOW)}
    out = ranking.fuse(legs, usage, k=2, now=NOW)
    assert out[0].hit.memory.id == "b"


def test_challenger_quota():
    legs = [_hit(f"m{i}", "fts", i + 1) for i in range(20)]
    out = ranking.fuse(legs, {}, k=8, now=NOW)
    assert len(out) == 8
    assert sum(1 for s in out if s.challenger) == 2   # k/4


def test_explore_widens_challengers_and_drops_strength():
    legs = [_hit(f"m{i}", "fts", i + 1) for i in range(20)]
    usage = {f"m{i}": ranking.UsageRow(helped=9, last_recalled_at=NOW) for i in range(20)}
    out = ranking.fuse(legs, usage, k=8, explore=True, now=NOW)
    assert sum(1 for s in out if s.challenger) == 4   # k/2
    assert all(s.strength == 0.0 for s in out)


def test_challengers_prefer_untried():
    legs = [_hit(f"m{i}", "fts", i + 1) for i in range(10)]
    usage = {f"m{i}": ranking.UsageRow(recalled=100) for i in range(9)}   # m9 untried
    out = ranking.fuse(legs, usage, k=8, now=NOW)
    chal = [s.hit.memory.id for s in out if s.challenger]
    assert "m9" in chal
