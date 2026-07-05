"""Derivation rules: deterministic, exclusion-honoring, shape-aware."""
from __future__ import annotations

from engine.memory import derive
from engine.memory.interface import SPACE_FILE, SPACE_MEMORY


def _all_rows(root):
    rows = []
    for p in derive.all_sources(root):
        rows.extend(derive.derive_file(root, p))
    return rows


def test_deterministic_ids_two_runs(root):
    a = sorted(r.id for r in _all_rows(root))
    b = sorted(r.id for r in _all_rows(root))
    assert a == b and len(a) > 0


def test_archive_yields_zero_rows(root):
    rows = _all_rows(root)
    assert not [r for r in rows if "archive" in r.source_path]


def test_in_context_is_file_space_only(root):
    rows = [r for r in _all_rows(root) if "in_context" in r.source_path]
    assert rows, "the keyring must be findable via file-space"
    assert all(r.space == SPACE_FILE for r in rows)


def test_self_and_diaries_are_file_space_only(root):
    rows = [r for r in _all_rows(root)
            if r.source_path.startswith(("vape/entity/self/", "vape/entity/diaries/"))]
    assert rows and all(r.space == SPACE_FILE for r in rows)


def test_case_blocks_become_rows(root):
    cases = [r for r in _all_rows(root) if r.kind == "case"]
    assert len(cases) == 2
    slugs = {r.pointer["anchor"] for r in cases}
    assert slugs == {"widget-overreach", "widget-checked-first"}


def test_note_bullets_fold_continuations(root):
    notes = [r for r in _all_rows(root) if r.kind == "note"]
    assert len(notes) == 2
    assert any("flux capacitor" in r.content and "keeper-candidate" in r.content for r in notes)


def test_event_bullets_are_individual_rows(root):
    events = [r for r in _all_rows(root) if r.kind == "event" and r.space == SPACE_MEMORY]
    assert len(events) == 2


def test_schema_doc_row_carries_topic(root):
    schema = next(r for r in _all_rows(root) if r.kind == "schema")
    assert schema.topic == "widgets"
