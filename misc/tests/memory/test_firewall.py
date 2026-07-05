"""The firewall: read-time verification, counters, deref, floor smoke."""
from __future__ import annotations


def test_recall_end_to_end(indexer, firewall):
    indexer.sweep()
    res = firewall.recall("flux capacitor warm rotation", k=4)
    assert res.hits and res.backend == "sqlite"
    assert any("flux capacitor" in h.content for h in res.hits)


def test_stale_hit_is_flagged_and_enqueued(root, indexer, firewall, core):
    indexer.sweep()
    res = firewall.recall("gear law odd ratios", k=4)
    target_hit = next(h for h in res.hits if "schemata/widgets" in h.source_path)
    assert not target_hit.stale

    # the world moves; the index doesn't know yet
    f = root / target_hit.source_path
    f.write_text(f.read_text(encoding="utf-8") + "\nAn appended truth.\n", encoding="utf-8")

    res2 = firewall.recall("gear law odd ratios", k=4)
    hit2 = next(h for h in res2.hits if h.source_path == target_hit.source_path)
    assert hit2.stale
    assert core.queue_depth() >= 1

    # the next sweep heals it
    indexer.sweep()
    res3 = firewall.recall("gear law odd ratios", k=4)
    hit3 = next(h for h in res3.hits if h.source_path == target_hit.source_path)
    assert not hit3.stale


def test_counters_recalled_and_dereferenced(indexer, firewall, core):
    indexer.sweep()
    res = firewall.recall("widget overreach shipped", k=4)
    ids = {h.id for h in res.hits}
    usage = core.usage_rows(ids)
    assert all(usage[i].recalled >= 1 for i in ids)

    body_ptr = firewall.deref(res.hits[0].id)
    assert body_ptr is not None
    body, pointer = body_ptr
    assert body.strip()
    assert core.usage_rows({res.hits[0].id})[res.hits[0].id].dereferenced == 1


def test_usage_survives_full_rebuild(indexer, firewall, core):
    indexer.sweep()
    res = firewall.recall("widget overreach shipped", k=2)
    the_id = res.hits[0].id
    before = core.usage_rows({the_id})[the_id].recalled
    indexer.sweep(full=True)
    res2 = firewall.recall("widget overreach shipped", k=2)
    assert res2.hits[0].id == the_id                        # deterministic ID rejoined
    assert core.usage_rows({the_id})[the_id].recalled == before + 1


def test_case_deref_prints_the_block(indexer, firewall):
    indexer.sweep()
    res = firewall.recall("scope creep asked first", kind="case", k=4)
    hit = next(h for h in res.hits if h.pointer.get("anchor") == "widget-checked-first")
    body, _ = firewall.deref(hit.id)
    assert "asked before extending" in body and "one-line ask" in body


def test_floor_answers_when_backend_lacks_space(root, core):
    """qmd-shaped scenario: a backend without memory-space falls to the floor."""
    from engine.memory.files_backend import FilesBackend
    from engine.memory.firewall import Firewall

    class FileOnly(FilesBackend):
        def capabilities(self):
            caps = super().capabilities()
            caps.spaces = {"file"}
            caps.name = "fileonly"
            return caps

    fw = Firewall(FileOnly(root), root, floor=FilesBackend(root), core_store=core)
    res = fw.recall("widget overreach shipped", space="memory", k=4)
    assert res.hits   # the floor answered
