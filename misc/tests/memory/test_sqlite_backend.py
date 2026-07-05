"""The sqlite drawer: reconcile semantics, disposability, live schema."""
from __future__ import annotations

from engine.memory.interface import Query


def _ids(backend, cue: str, space="memory"):
    return sorted(h.memory.id for h in backend.search(Query(text=cue, space=space)))


def test_full_rebuild_equivalence(indexer, sqlite_backend):
    indexer.sweep()
    before = _ids(sqlite_backend, "widget gear odd ratios")
    assert before
    res = indexer.sweep(full=True)
    assert res.files_changed == res.files_seen
    assert _ids(sqlite_backend, "widget gear odd ratios") == before   # deterministic IDs


def test_reconcile_removes_vanished_anchors(root, indexer, sqlite_backend):
    indexer.sweep()
    target = root / "vape" / "entity" / "memory" / "cases" / "sample.md"
    text = target.read_text(encoding="utf-8")
    target.write_text(text.split("### id: widget-checked-first")[0], encoding="utf-8")
    indexer.sweep()
    hits = sqlite_backend.search(Query(text="asked before extending approved", space="memory", kind="case"))
    assert all(h.memory.pointer["anchor"] != "widget-checked-first" for h in hits)


def test_filters_scope_the_search(indexer, sqlite_backend):
    indexer.sweep()
    only_cases = sqlite_backend.search(Query(text="widget", space="memory", kind="case"))
    assert only_cases and all(h.memory.kind == "case" for h in only_cases)
    only_topic = sqlite_backend.search(Query(text="gear", space="memory", topic="widgets"))
    assert only_topic and all(h.memory.topic == "widgets" for h in only_topic)


def test_schema_is_live_introspection(sqlite_backend):
    s = sqlite_backend.schema()
    assert "memories" in s and "fts5" in s.lower()


def test_file_space_serves_the_keyring(indexer, sqlite_backend):
    indexer.sweep()
    hits = sqlite_backend.search(Query(text="overreach case extend the brief", space="file"))
    assert any("in_context" in h.memory.source_path for h in hits)
