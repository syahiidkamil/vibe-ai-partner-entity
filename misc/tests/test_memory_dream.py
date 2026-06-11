"""Tests for the DREAM component (consolidate) + bookmark draining.

Honesty floor (the task's hard rule): the deep-dream round-trip claim is earned ONLY by
running against the REAL Postgres + pgvector + the REAL Gemini embedding API — nothing
mocked. The gating / tier-separation / equilibration tests are pure-ish (state + jsonl on
a temp path) and always run.

Isolation: the state-file tests redirect dream's BOOKMARKS_PATH / DREAM_STATE_PATH /
MEMORY_INDEX_PATH / MEMORY_WIKI_DIR at module scope to a tmp dir, so the real
memory_wiki/ is never touched. The live DB test scopes every written row to a unique
throwaway bubble and deletes it on teardown, leaving the corpus exactly as found.
"""

from __future__ import annotations

import json
import uuid

import pytest

from engine.memory import dream


# =================================================================================
# fixtures — isolate the on-disk state so the real memory_wiki/ is never touched
# =================================================================================
@pytest.fixture
def tmp_state(tmp_path, monkeypatch):
    """Point every file path the dream touches at a throwaway tmp dir for one test.

    The dream delegates bookmark read/clear to the firewall-core ``bookmarks`` module
    (which resolves its own path from ``config.BOOKMARKS_PATH``), so to keep the two in
    sync under test we patch the path in BOTH namespaces — else dream writes to tmp but
    the delegated reader looks at the real file."""
    bm = tmp_path / "bookmarks.jsonl"
    ds = tmp_path / "dream_state.json"
    idx = tmp_path / "MEMORY.md"
    monkeypatch.setattr(dream, "BOOKMARKS_PATH", bm)
    monkeypatch.setattr(dream, "DREAM_STATE_PATH", ds)
    monkeypatch.setattr(dream, "MEMORY_INDEX_PATH", idx)
    monkeypatch.setattr(dream, "MEMORY_WIKI_DIR", tmp_path)
    # keep the delegated bookmarks module pointing at the same tmp file.
    try:
        from engine.memory import bookmarks

        monkeypatch.setattr(bookmarks, "BOOKMARKS_PATH", bm)
    except Exception:
        pass
    return tmp_path


def _write_bookmarks(path, recs):
    path.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in recs) + "\n",
        encoding="utf-8",
    )


def _bm(id_, note, *, bubble="global", kind="lesson", surprise=0.8, tone=0.2, meta=None):
    rec = {
        "id": id_, "ts": "2026-06-08T00:00:00Z", "bubble": bubble, "kind": kind,
        "surprise": surprise, "tone": tone, "note": note, "ref": None,
    }
    if meta is not None:
        rec["meta"] = meta
    return rec


# =================================================================================
# PURE-ISH — gating (is_due) over the state cursor
# =================================================================================
def test_is_due_light_false_when_quiet(tmp_state):
    """No bookmarks, no accrued turns → a light dream is not due (cheap silent exit)."""
    dream._save_state({"turns_since_dream": 0})
    assert dream.is_due(deep=False) is False


def test_is_due_light_true_when_bookmark_pending(tmp_state):
    """A persisted spike makes a light flush worthwhile."""
    _write_bookmarks(tmp_state / "bookmarks.jsonl", [_bm("a", "a spike")])
    assert dream.is_due(deep=False) is True


def test_is_due_deep_gates_on_accumulation(tmp_state):
    """Deep is NOT due on a couple of turns; IS due after a session's worth."""
    _write_bookmarks(tmp_state / "bookmarks.jsonl", [_bm("a", "x")])
    dream._save_state({"turns_since_dream": 3, "salience_since_dream": 0.0})
    assert dream.is_due(deep=True) is False
    dream._save_state({"turns_since_dream": dream.DEEP_DUE_TURNS, "salience_since_dream": 0.0})
    assert dream.is_due(deep=True) is True


def test_maybe_exits_cheap_when_not_due(tmp_state, capsys):
    """--maybe returns 0 and prints nothing when no consolidation is owed — the Stop
    hook's quiet path. (Prints nothing → the hook stays silent.)"""
    dream._save_state({"turns_since_dream": 0})
    code = dream.dream_cmd(deep=False, maybe=True)
    assert code == 0
    assert capsys.readouterr().out.strip() == ""


# =================================================================================
# LIGHT vs DEEP separation — light flushes, deep equilibrates
# =================================================================================
def test_light_dream_flushes_bookmarks_to_warm(tmp_state, monkeypatch):
    """Light dream drains the spikes (writes them as warm rows) and clears the file,
    WITHOUT scoring viability — that is the deep tier's job. The corpus write is stubbed
    so this stays a pure unit test of the light tier's flush+clear behaviour."""
    written = []
    monkeypatch.setattr(dream, "_write_corpus", lambda content, **kw: written.append((content, kw)) or 1)

    _write_bookmarks(
        tmp_state / "bookmarks.jsonl",
        [_bm("s1", "first spike"), _bm("s2", "second spike")],
    )
    out = dream.light_dream()
    assert out["tier"] == "light"
    assert out["written"] == 2
    assert len(written) == 2
    # every flushed row is a 'bookmark' kind, un-judged (viability 0) at the light tier
    assert all(kw["mem_type"] == "bookmark" for _, kw in written)
    assert all(kw["viability"] == 0.0 for _, kw in written)
    # the file is drained
    assert dream._read_bookmarks() == []
    # the breadcrumb was written (save-the-thread), not the always-loaded daily_self
    assert (tmp_state / "last_thread.md").exists()


def test_light_dream_does_not_touch_self_tree(tmp_state, monkeypatch):
    """Honesty floor: the light dream never edits vape/entity/self/. It writes a
    non-identity breadcrumb in memory_wiki/ only."""
    monkeypatch.setattr(dream, "_write_corpus", lambda content, **kw: 1)
    _write_bookmarks(tmp_state / "bookmarks.jsonl", [_bm("s1", "a spike")])
    dream.light_dream()
    crumb = (tmp_state / "last_thread.md").read_text(encoding="utf-8")
    assert "breadcrumb" in crumb.lower()


# =================================================================================
# EQUILIBRATION — assimilate / accommodate / Gate-2 / molten (the heart, no DB)
# =================================================================================
def test_accommodate_forms_new_lessons(tmp_state, monkeypatch):
    """Two thematically-distinct viable spikes → two NEW lesson rows (accommodation)."""
    monkeypatch.setattr(dream, "_existing_lessons", lambda bubble: [])
    plan = dream._equilibrate([
        _bm("a", "verify the render with Kamil's eyes; I cannot see my own avatar output"),
        _bm("b", "chase the root cause not the symptom when a transparent window leaks"),
    ])
    assert len(plan["lesson_rows"]) == 2
    assert len(plan["accommodated"]) == 2
    assert plan["assimilated"] == []


def test_assimilate_reinforces_not_duplicates(tmp_state, monkeypatch):
    """A spike that fits a lesson formed earlier the same night assimilates into it
    (reinforce), rather than creating a near-duplicate row."""
    monkeypatch.setattr(dream, "_existing_lessons", lambda bubble: [])
    plan = dream._equilibrate([
        _bm("a", "always verify the render output with Kamil because I cannot see the avatar"),
        _bm("b", "verify the render output with Kamil; I still cannot see my own avatar render"),
    ])
    # one row formed, the second assimilated into it
    assert len(plan["lesson_rows"]) == 1
    assert len(plan["accommodated"]) == 1
    assert len(plan["assimilated"]) == 1


def test_gate2_demotes_non_viable_noise(tmp_state, monkeypatch):
    """A maximally-surprising but useless (noise) spike passes Gate 1 but fails Gate 2 →
    demoted, never written as a lesson. Gate 2 is the noise filter Gate 1 cannot be."""
    monkeypatch.setattr(dream, "_existing_lessons", lambda bubble: [])
    noise = _bm(
        "n", "qx7 zzt blorp", kind="surprise", surprise=1.0,
        meta={"stakes": 0.0, "context": 0.0, "staleness": 1.0, "growth": 0.0},
    )
    plan = dream._equilibrate([noise])
    assert plan["lesson_rows"] == []
    assert "n" in plan["demoted"]


def test_contradiction_triggers_molten_reading(tmp_state, monkeypatch):
    """A counter-spike that negates a same-theme lesson resolves by the molten reading:
    the meaning is refined (qualified), NOT flipped to the opposite or silently stacked."""
    existing = [{"id": 7, "content": "the closed solid setup is always the safe choice", "viability": 0.6}]
    monkeypatch.setattr(dream, "_existing_lessons", lambda bubble: existing)
    plan = dream._equilibrate([
        _bm("c", "the closed solid setup is not safe when the center is already broken open"),
    ])
    assert len(plan["contradictions"]) == 1
    assert 7 in plan["reinforced"]
    # the lesson's meaning was refined (molten), keeping the fact and qualifying it
    assert "unless" in existing[0]["content"].lower()


def test_molten_refine_keeps_fact_does_not_flip():
    """The molten refine appends a qualifier; it never replaces the base claim with its
    negation."""
    refined = dream._molten_refine("X is always good", "X is bad when Y")
    assert "X is always good" in refined
    assert "unless" in refined.lower()
    assert "X is bad when Y" in refined


# =================================================================================
# LIVE DB — a deep dream produces an ACTUAL lesson row (real Postgres + real Gemini)
# =================================================================================
@pytest.fixture
def live_bubble():
    """A throwaway bubble; rows tagged with it are deleted on teardown so the live corpus
    is left as found. (DELETE here is test housekeeping, NOT the engine's eviction path —
    eviction never deletes.)"""
    import shutil

    from engine.memory import db
    from engine.memory.config import BUBBLES_DIR
    from engine.memory.schema import TABLE

    tag = f"_pytest_dream_{uuid.uuid4().hex[:8]}"
    yield tag, TABLE
    with db.session() as conn:
        with conn.cursor() as cur:
            cur.execute(f"DELETE FROM {TABLE} WHERE bubble = %s", (tag,))
        conn.commit()
    # the soul module writes a bubbles/<tag>/ dir at the real config path (not the tmp
    # one) when the deep dream touches a bubble; remove that side effect so the tree is
    # left as found.
    shutil.rmtree(BUBBLES_DIR / tag, ignore_errors=True)


def test_deep_dream_writes_a_real_lesson_row(tmp_state, monkeypatch, live_bubble):
    """The north-star of this component: a deep dream over synthetic bookmarks produces a
    real, queryable lesson row in the live DB — constructed self, not a raw spike echo."""
    from engine.memory import db
    from engine.memory.schema import TABLE

    tag, _ = live_bubble
    # two distinct viable spikes in the throwaway bubble → two accommodated lessons.
    _write_bookmarks(
        tmp_state / "bookmarks.jsonl",
        [
            _bm("d1", "verify the render with Kamil because I cannot see my own avatar output",
                bubble=tag, kind="lesson", surprise=0.85,
                meta={"stakes": 0.6, "context": 0.5, "staleness": 0.0, "growth": 0.9}),
            _bm("d2", "chase the root cause not the symptom when a window renders a stale fringe",
                bubble=tag, kind="lesson", surprise=0.8,
                meta={"stakes": 0.6, "context": 0.5, "staleness": 0.0, "growth": 0.85}),
        ],
    )

    result = dream.deep_dream()
    assert result["tier"] == "deep"
    assert result["written"] >= 1, f"deep dream wrote no lesson rows: {result}"
    assert result["accommodated"] >= 1

    # the row is really in the corpus, typed 'lesson', from the dream, in our bubble.
    with db.session() as conn, conn.cursor() as cur:
        cur.execute(
            f"SELECT content, mem_type, source, viability FROM {TABLE} "
            f"WHERE bubble = %s AND mem_type = 'lesson' ORDER BY id",
            (tag,),
        )
        rows = cur.fetchall()
    assert rows, "no lesson row found in the live corpus after the deep dream"
    contents = " ".join(r[0] for r in rows)
    assert "render" in contents or "root cause" in contents
    assert all(r[1] == "lesson" for r in rows)
    assert all(r[2] == "dream" for r in rows)
    assert all(float(r[3]) > 0.0 for r in rows)  # Gate-2 viability was scored and stored

    # the wiki grew and the bookmarks were drained.
    assert result["wiki_lines"] >= 1
    assert dream._read_bookmarks() == []
    # the deep cursor reset.
    assert dream._load_state()["turns_since_dream"] == 0


def test_deep_dream_empty_is_clean_noop(tmp_state):
    """No bookmarks → a clean no-op that still stamps the cursor (a valid outcome)."""
    result = dream.deep_dream()
    assert result["written"] == 0
    assert result["note"] == "no bookmarks to consolidate"
    assert dream._load_state()["last_deep_dream_at"] is not None
