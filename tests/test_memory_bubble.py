"""Tests for the bubble mechanism (engine/memory/bubble.py).

Covers the three sub-problems the phrase "bubbles load" hides:
  DECLARE — register enter/leave/active/tick_turns, with provenance + turn counting.
  SELECT  — list_bubbles scans bubbles/<name>/HOT.md; inject_block reads it.
  INJECT  — inject_block emits PROSE only (frontmatter stripped), header framed, and
            clamps to the small-pack budget.
And the advisory layer: suggest() is advisory-not-forced (no active bubble required to
exist; silent when one is active; only fires on a strong keyword match).

These tests redirect the module's path constants at runtime to a tmp dir so they never
touch the real register or the real memory_wiki. Pure filesystem — no DB, no network.
"""

from __future__ import annotations

import importlib

import pytest

import engine.memory.bubble as B


@pytest.fixture()
def sandbox(tmp_path, monkeypatch):
    """Point the bubble module at a throwaway tree so the real files stay untouched."""
    wiki = tmp_path / "memory_wiki"
    bubbles = wiki / "bubbles"
    bubbles.mkdir(parents=True)
    register = tmp_path / "active_bubble.json"

    monkeypatch.setattr(B, "BUBBLES_DIR", bubbles, raising=True)
    monkeypatch.setattr(B, "ACTIVE_BUBBLE_PATH", register, raising=True)
    # bleed proposals also go under the sandbox
    monkeypatch.setattr(
        B, "_BLEED_PROPOSALS_PATH", tmp_path / "PROPOSED_bubble_bleed.md", raising=True
    )
    return tmp_path


def _make_bubble(sandbox, name: str, hot_md: str) -> None:
    d = sandbox / "memory_wiki" / "bubbles" / name
    d.mkdir(parents=True, exist_ok=True)
    (d / "HOT.md").write_text(hot_md, encoding="utf-8")


# --------------------------------------------------------------------------- #
# DECLARE — the register                                                       #
# --------------------------------------------------------------------------- #
def test_active_is_none_on_fresh_register(sandbox):
    assert B.active() is None


def test_enter_declares_active_with_provenance(sandbox):
    B.enter("chess", by="kamil")
    reg = B.active()
    assert reg is not None
    assert reg["active"] == "chess"
    assert reg["entered_by"] == "kamil"
    assert reg["turns_active"] == 0
    assert reg["entered_at"]  # stamped


def test_enter_normalises_name(sandbox):
    B.enter("  CHESS  ")
    assert B.active()["active"] == "chess"


def test_enter_empty_name_raises(sandbox):
    with pytest.raises(ValueError):
        B.enter("   ")


def test_leave_releases(sandbox):
    B.enter("chess")
    assert B.active() is not None
    B.leave()
    assert B.active() is None


def test_leave_is_idempotent(sandbox):
    B.leave()  # nothing active — must not raise
    assert B.active() is None


def test_tick_turns_increments_only_when_active(sandbox):
    B.tick_turns()  # no active bubble: no-op, no file needed
    assert B.active() is None

    B.enter("chess")
    B.tick_turns()
    B.tick_turns()
    assert B.active()["turns_active"] == 2


def test_reenter_same_bubble_keeps_turns_continuous(sandbox):
    B.enter("chess")
    B.tick_turns()
    B.tick_turns()
    B.enter("chess")  # re-entering the active one must NOT reset the counter
    assert B.active()["turns_active"] == 2


def test_enter_different_bubble_resets_turns(sandbox):
    B.enter("chess")
    B.tick_turns()
    B.enter("the-build")
    assert B.active()["active"] == "the-build"
    assert B.active()["turns_active"] == 0


def test_corrupt_register_reads_as_empty(sandbox):
    (sandbox / "active_bubble.json").write_text("{not json", encoding="utf-8")
    assert B.active() is None  # tolerant, not a crash


# --------------------------------------------------------------------------- #
# SELECT — list + path resolution                                             #
# --------------------------------------------------------------------------- #
def test_list_bubbles_empty(sandbox):
    assert B.list_bubbles() == []


def test_list_bubbles_only_counts_dirs_with_hot_md(sandbox):
    _make_bubble(sandbox, "chess", "# chess\nstyle")
    _make_bubble(sandbox, "the-build", "# the-build\nstyle")
    # a dir with no HOT.md is not a bubble
    (sandbox / "memory_wiki" / "bubbles" / "empty-dir").mkdir()
    assert B.list_bubbles() == ["chess", "the-build"]  # sorted, filtered


# --------------------------------------------------------------------------- #
# INJECT — the prose block                                                     #
# --------------------------------------------------------------------------- #
def test_inject_block_none_when_no_active(sandbox):
    _make_bubble(sandbox, "chess", "# chess\nstyle prose")
    assert B.inject_block() is None  # nothing active -> nothing injected


def test_inject_block_renders_prose_with_header(sandbox):
    _make_bubble(sandbox, "chess", "# chess\nI play sharp under time pressure.")
    B.enter("chess")
    block = B.inject_block()
    assert block is not None
    assert "chess" in block
    assert "I play sharp under time pressure." in block
    # framed as a bubble header (names the scope, points at the release verb)
    assert "bubble" in block.lower()
    assert "vape bubble leave" in block


def test_inject_block_strips_frontmatter(sandbox):
    md = (
        "---\n"
        "version: 14\n"
        "confidence: 0.55\n"
        "---\n"
        "# chess\n"
        "My style prose, no numbers.\n"
    )
    _make_bubble(sandbox, "chess", md)
    B.enter("chess")
    block = B.inject_block()
    assert "My style prose, no numbers." in block
    # the numeric frontmatter must NOT leak into the injected prose
    assert "version: 14" not in block
    assert "confidence: 0.55" not in block


def test_inject_block_none_on_missing_pack(sandbox):
    # register says chess is active, but no pack file exists
    B.enter("chess")
    assert B.inject_block() is None


def test_inject_block_none_on_empty_pack(sandbox):
    _make_bubble(sandbox, "chess", "   \n  \n")
    B.enter("chess")
    assert B.inject_block() is None


def test_inject_block_clamps_to_budget(sandbox):
    big = "# chess\n" + ("word " * 5000)  # way over ~450 tokens
    _make_bubble(sandbox, "chess", big)
    B.enter("chess")
    block = B.inject_block()
    assert block is not None
    # clamped near the char budget (+ header + truncation note); not the full 25k chars
    assert len(block) < B._HOT_MD_CHAR_CLAMP + 1000
    assert "truncated" in block.lower()


# --------------------------------------------------------------------------- #
# ADVISORY auto-suggest — advice, not a forced load                            #
# --------------------------------------------------------------------------- #
def test_suggest_fires_on_strong_match(sandbox):
    _make_bubble(sandbox, "chess", "# chess\nstyle")
    s = B.suggest("Want to play a game of chess? I'll open with a gambit.")
    assert s is not None
    assert "chess" in s
    assert "vape bubble enter chess" in s


def test_suggest_silent_when_bubble_active(sandbox):
    _make_bubble(sandbox, "chess", "# chess\nstyle")
    B.enter("chess")
    # already in a bubble -> never nag a suggestion
    assert B.suggest("let's play chess with a sicilian gambit") is None


def test_suggest_silent_on_weak_or_no_match(sandbox):
    _make_bubble(sandbox, "chess", "# chess\nstyle")
    assert B.suggest("let's talk about the weather today") is None
    # a single ambient keyword is NOT a strong match (threshold >= 2)
    assert B.suggest("the queen of England") is None


def test_suggest_never_forces_a_load(sandbox):
    _make_bubble(sandbox, "chess", "# chess\nstyle")
    B.suggest("chess gambit endgame blitz")  # strong match
    # a suggestion must NEVER change the register — it only returns a string
    assert B.active() is None


# --------------------------------------------------------------------------- #
# Bubble-bleed — propose-only, never auto-writes self/                         #
# --------------------------------------------------------------------------- #
def test_promotion_is_propose_only(sandbox):
    rec = B.propose_promotion(
        bubble="chess", trait="aggressive under time pressure",
        why="held across three non-chess scopes too",
    )
    assert rec["kind"] == "promote"
    assert "PROPOSED" in rec["status"]
    # it writes to the flagged work_dir file, NOT into vape/entity/self/
    proposals = (sandbox / "PROPOSED_bubble_bleed.md").read_text(encoding="utf-8")
    assert "aggressive under time pressure" in proposals
    assert "RATIFICATION-GATED" in proposals


def test_demote_records_proposal(sandbox):
    rec = B.demote_to_bubble(
        trait="be patient", why="only holds at the board", bubble="chess"
    )
    assert rec["kind"] == "demote"
    assert (sandbox / "PROPOSED_bubble_bleed.md").exists()


def test_module_imports_clean():
    # guards against an import-time error sneaking in (the hook imports this)
    importlib.reload(B)
