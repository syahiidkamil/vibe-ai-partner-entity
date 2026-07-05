"""The sweeper's freshness discipline: mtime prunes, hash decides, version forces."""
from __future__ import annotations

import os

from engine.memory.interface import Query


def test_initial_sweep_indexes_everything(indexer, sqlite_backend):
    res = indexer.sweep()
    assert not res.skipped_lock
    assert res.files_changed == res.files_seen > 0
    assert res.report.upserted > 0
    hits = sqlite_backend.search(Query(text="flux capacitor warm", space="memory"))
    assert hits and any("flux capacitor" in h.memory.content for h in hits)


def test_resweep_is_noop(indexer):
    indexer.sweep()
    res = indexer.sweep()
    assert res.files_changed == 0 and res.report.upserted == 0


def test_mtime_touch_does_not_rederive(root, indexer):
    indexer.sweep()
    target = root / "vape" / "entity" / "memory" / "notes" / "2026-01-01.md"
    os.utime(target)   # envelope changes, letter doesn't
    res = indexer.sweep()
    assert res.report.upserted == 0


def test_content_change_rederives_only_that_file(root, indexer):
    indexer.sweep()
    target = root / "vape" / "entity" / "memory" / "notes" / "2026-01-01.md"
    target.write_text(
        target.read_text(encoding="utf-8") + "- open · a third insight · fresh\n",
        encoding="utf-8",
    )
    res = indexer.sweep()
    assert res.files_changed == 1
    assert res.report.upserted >= 3   # the file's bullets reconciled


def test_deleted_file_evicts_rows(root, indexer, sqlite_backend):
    indexer.sweep()
    target = root / "vape" / "entity" / "memory" / "people" / "particular" / "alice" / "profile.md"
    target.unlink()
    res = indexer.sweep()
    assert res.files_deleted == 1
    assert not sqlite_backend.search(Query(text="alice widget testbeds", space="memory", kind="person"))


def test_version_bump_forces_rederive(indexer, monkeypatch):
    indexer.sweep()
    import engine.memory.indexer as idx_mod
    monkeypatch.setattr(idx_mod, "INDEXER_VERSION", 999)
    res = indexer.sweep()
    assert res.files_changed == res.files_seen > 0


def test_reindex_queue_forces_file(root, indexer, core):
    indexer.sweep()
    core.enqueue_reindex("vape/entity/memory/cases/sample.md", reason="test")
    res = indexer.sweep()
    assert res.files_changed == 1
    assert core.queue_depth() == 0
