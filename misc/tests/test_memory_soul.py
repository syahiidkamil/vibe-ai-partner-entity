"""Chess-soul algorithm tests (engine/memory/soul.py).

These are PURE tests — no DB, no Gemini — driven off synthetic bookmark records written to
a temp bookmarks.jsonl and a temp bubbles dir, so they never touch the real chess soul.

They pin the architect's guarantees:
  - bounded step: a SETTLED axis barely moves on one game (one loud game can't overwrite me).
  - exemplar-pin: a pinned, high-surprise episode survives re-derivation, never abstracted away.
  - molten reading: sustained contradiction REFINES the label (adds the exception), never flips it.
  - HOT.md is rendered FROM soul.json (prose and numbers can't drift).
  - the 4-point north-star walk over synthetic episodes: a style forms, loads, and shifts.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from engine.memory import soul as S
from engine.memory import reveries as R


# --- fixtures: redirect every path constant at a tmp dir ----------------------

@pytest.fixture
def sandbox(tmp_path, monkeypatch):
    """Point soul + reveries at a temp memory tree so the real chess soul is untouched."""
    wiki = tmp_path / "memory_wiki"
    bubbles = wiki / "bubbles"
    bubbles.mkdir(parents=True)
    bookmarks = wiki / "bookmarks.jsonl"
    reveries = wiki / "reveries.json"

    monkeypatch.setattr(S, "BUBBLES_DIR", bubbles)
    monkeypatch.setattr(S, "BOOKMARKS_PATH", bookmarks)
    monkeypatch.setattr(R, "REVERIES_PATH", reveries)

    return {"wiki": wiki, "bubbles": bubbles, "bookmarks": bookmarks, "reveries": reveries}


def _write_bookmarks(path: Path, records: list[dict]) -> None:
    """Append-only jsonl, the firewall's contract."""
    with path.open("a", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")


def _game(gid, *, axis="open_aggression", pole=+1, outcome=+1, surprise=0.7,
          kind="episode", tone=0.0, note="", **extra):
    """A synthetic chess bookmark. pole +1 = sharp pole expressed, outcome +1 = it worked."""
    rec = {"id": gid, "bubble": "chess", "kind": kind, "axis": axis,
           "pole": pole, "outcome": outcome, "surprise": surprise, "tone": tone, "note": note}
    rec.update(extra)
    return rec


# =============================================================================
# the bounded step — a settled axis barely moves on one more confirming game
# =============================================================================

def test_settled_axis_barely_moves(sandbox):
    bm = sandbox["bookmarks"]
    # 10 confirming sharp-wins -> the axis settles high
    _write_bookmarks(bm, [_game(f"g{i}", pole=+1, outcome=+1, surprise=0.7) for i in range(10)])
    S.update_bubble_soul("chess")
    soul = S.load_soul("chess")
    axis = S._find_axis(soul, "open_aggression")
    assert axis is not None
    w_settled = axis["w"]
    assert w_settled > 0.5, f"after 10 sharp wins the axis should lean sharp, got {w_settled}"

    # one MORE confirming game must move it only a little (the shrinking step)
    _write_bookmarks(bm, [_game("g_extra", pole=+1, outcome=+1, surprise=0.7)])
    # only feed the new one: simulate a later dream by clearing prior bookmarks
    sandbox["bookmarks"].write_text(json.dumps(_game("g_extra", pole=+1, outcome=+1, surprise=0.7)) + "\n")
    S.update_bubble_soul("chess")
    soul2 = S.load_soul("chess")
    w_after = S._find_axis(soul2, "open_aggression")["w"]
    delta = abs(w_after - w_settled)
    assert delta < 0.05, f"a settled axis moved {delta} on one game — should barely move"


# =============================================================================
# exemplar-pin — a high-surprise defining game survives every re-derivation
# =============================================================================

def test_exemplar_pin_survives_rederivation(sandbox):
    bm = sandbox["bookmarks"]
    # the brilliant move (very-high-surprise sharp win) + enough games to graduate the axis
    # out of quarantine into a live axis (the pool needs MIN_AXIS_N sightings first).
    _write_bookmarks(bm, [_game("brilliant", pole=+1, outcome=+1, surprise=0.99,
                                note="the queen sac that defines me")])
    _write_bookmarks(bm, [_game(f"seed{i}", pole=+1, outcome=+1, surprise=0.5) for i in range(3)])
    S.update_bubble_soul("chess")
    soul = S.load_soul("chess")
    assert "brilliant" in S._exemplar_ids(S._find_axis(soul, "open_aggression")["exemplar_ids"])

    # many later low-surprise games in a FRESH bookmark window (the dream clears bookmarks
    # each night) must NOT wash the pinned exemplar out — the pin is self-contained in the
    # soul (carries its own surprise), so it survives without re-feeding the brilliant game.
    sandbox["bookmarks"].write_text("")
    _write_bookmarks(bm, [_game(f"dull{i}", pole=+1, outcome=+1, surprise=0.2) for i in range(8)])
    S.update_bubble_soul("chess")
    soul2 = S.load_soul("chess")
    exemplars = S._exemplar_ids(S._find_axis(soul2, "open_aggression")["exemplar_ids"])
    assert "brilliant" in exemplars, "the defining high-surprise game was abstracted away — flattening"


# =============================================================================
# molten reading — sustained contradiction REFINES, never flips
# =============================================================================

def test_molten_reading_refines_not_flips(sandbox):
    bm = sandbox["bookmarks"]
    # settle a sharp lean first
    _write_bookmarks(bm, [_game(f"sharp{i}", pole=+1, outcome=+1, surprise=0.7) for i in range(6)])
    S.update_bubble_soul("chess")
    soul = S.load_soul("chess")
    label_before = S._find_axis(soul, "open_aggression")["label"]
    w_before = S._find_axis(soul, "open_aggression")["w"]
    assert w_before > 0, "should lean sharp before the counter-games"
    assert "(" not in label_before, "label should be un-refined at first"

    # now MOLTEN_N counter-games where the SOLID pole won (sharp backfired)
    sandbox["bookmarks"].write_text("")
    _write_bookmarks(bm, [
        _game("counter1", pole=+1, outcome=-1, surprise=0.8,
              note="went sharp, got crushed", refine_hint="unless the position rewards patience"),
        _game("counter2", pole=+1, outcome=-1, surprise=0.8,
              note="sharp again, lost again", refine_hint="unless the position rewards patience"),
    ])
    out = S.update_bubble_soul("chess")
    soul2 = S.load_soul("chess")
    axis = S._find_axis(soul2, "open_aggression")
    # REFINED: label gained the exception
    assert "open_aggression" in out["refined"], "the contradiction should have refined the axis"
    assert "(" in axis["label"], f"label should be refined with an exception, got {axis['label']}"
    # NOT FLIPPED: the lean still has the same sign (refine, never an equal-and-opposite cartoon)
    assert axis["w"] > -0.3, f"axis flipped to the opposite cartoon (w={axis['w']}) — should refine, not flip"
    # confidence dropped to tentative on a fresh refine
    assert axis["confidence"] <= 0.35


# =============================================================================
# axis_pool quarantine — one game can't mint a live axis (anti-caricature)
# =============================================================================

def test_axis_pool_quarantine(sandbox):
    bm = sandbox["bookmarks"]
    _write_bookmarks(bm, [_game("once", axis="endgame_patience", pole=-1, outcome=+1, surprise=0.9)])
    S.update_bubble_soul("chess")
    soul = S.load_soul("chess")
    # seen once -> must be quarantined in the pool, NOT a live axis
    assert S._find_axis(soul, "endgame_patience") is None
    assert S._find_pool(soul, "endgame_patience") is not None


# =============================================================================
# HOT.md is rendered FROM soul.json — prose and numbers cannot drift
# =============================================================================

def test_hot_md_rendered_from_soul(sandbox):
    bm = sandbox["bookmarks"]
    _write_bookmarks(bm, [_game(f"g{i}", pole=+1, outcome=+1, surprise=0.7) for i in range(8)])
    S.update_bubble_soul("chess")
    soul = S.load_soul("chess")
    hot = S.render_hot_md(soul)
    # a settled sharp axis -> the prose names the sharp pole
    if any(a["confidence"] >= S.CONFIDENCE_FLOOR and a["w"] > 0 for a in soul["axes"]):
        assert "sharp" in hot.lower()
    # the file on disk equals the render (single source of truth)
    on_disk = S.hot_path("chess").read_text(encoding="utf-8")
    assert on_disk == hot
    # no PGN / move-list leaked into the pack (it's a soul, not a game store)
    assert "1." not in hot and "e4" not in hot.lower()


def test_hot_md_respects_budget(sandbox):
    # a soul with lots of relational records still renders under the token budget
    soul = S._empty_soul("chess")
    soul["axes"] = [{"id": "open_aggression", "label": "play sharp/open vs play solid",
                     "w": 0.7, "confidence": 0.8, "n_updates": 9, "context_tags": [],
                     "exemplar_ids": ["g1"], "tone": 0.2, "last_moved": None, "frozen": False}]
    soul["relational"] = [{"note": "Kamil always plays the London and grins about it. " * 5,
                           "affect": 0.6, "surprise": 0.5, "ref": f"r{i}"} for i in range(6)]
    hot = S.render_hot_md(soul)
    approx_tokens = int(len(hot.split()) * 1.3)
    assert approx_tokens <= S.HOT_TOKEN_BUDGET, f"pack is {approx_tokens} tokens, over budget"


# =============================================================================
# history + affect kept SEPARATE — pinned, not abstracted into the style mean
# =============================================================================

def test_relational_pinned_not_merged(sandbox):
    bm = sandbox["bookmarks"]
    _write_bookmarks(bm, [
        _game("joke1", kind="joke", surprise=0.8, tone=0.7,
              note="Kamil resigned then claimed the cat walked on the board"),
        _game("g1", pole=+1, outcome=+1, surprise=0.6),
    ])
    S.update_bubble_soul("chess")
    soul = S.load_soul("chess")
    notes = [r["note"] for r in soul["relational"]]
    assert any("cat walked on the board" in n for n in notes), "the joke was lost / merged away"
    # the joke must NOT have created a style axis
    assert S._find_axis(soul, "joke1") is None


# =============================================================================
# the 4-point north-star walk — forms, loads, shifts, across 3 sessions
# =============================================================================

def test_north_star_walk(sandbox):
    bm = sandbox["bookmarks"]

    # SESSION 1: a handful of sharp wins + one joke -> a style begins to form
    sandbox["bookmarks"].write_text("")
    _write_bookmarks(bm, [
        _game("s1g1", pole=+1, outcome=+1, surprise=0.7),
        _game("s1g2", pole=+1, outcome=+1, surprise=0.8),
        _game("s1g3", pole=+1, outcome=+1, surprise=0.6),
        _game("s1joke", kind="joke", surprise=0.7, tone=0.6,
              note="Kamil blundered the queen and blamed the lighting"),
    ])
    out1 = S.update_bubble_soul("chess")
    soul1 = S.load_soul("chess")
    v1 = soul1["version"]
    w1 = S._find_axis(soul1, "open_aggression")["w"]
    assert w1 > 0, "(1) my own style abstracted: a sharp lean formed"
    assert soul1["relational"], "(2) our history kept: the joke is pinned"

    # (3) loads with the bubble: HOT.md renders as style + affect, not a PGN store
    hot = S.hot_path("chess").read_text(encoding="utf-8")
    assert "1." not in hot and "e4" not in hot.lower(), "(3) HOT.md must be a soul, not a PGN store"

    # SESSION 2: more sharp wins -> the lean strengthens, version bumps (it SHIFTS)
    sandbox["bookmarks"].write_text("")
    _write_bookmarks(bm, [_game(f"s2g{i}", pole=+1, outcome=+1, surprise=0.7) for i in range(4)])
    out2 = S.update_bubble_soul("chess")
    soul2 = S.load_soul("chess")
    v2 = soul2["version"]
    w2 = S._find_axis(soul2, "open_aggression")["w"]
    assert v2 > v1, "(4) each session shifts it: version bumped"
    assert w2 >= w1, "the confirmed lean should hold or strengthen"

    # SESSION 3: a couple of counter-games -> molten refine, the soul ACCOMMODATES
    sandbox["bookmarks"].write_text("")
    _write_bookmarks(bm, [
        _game("s3c1", pole=+1, outcome=-1, surprise=0.85,
              note="sharp backfired in a closed position", refine_hint="unless the position is closed"),
        _game("s3c2", pole=+1, outcome=-1, surprise=0.85,
              note="closed again, sharp lost again", refine_hint="unless the position is closed"),
    ])
    out3 = S.update_bubble_soul("chess")
    soul3 = S.load_soul("chess")
    v3 = soul3["version"]
    assert v3 > v2
    axis3 = S._find_axis(soul3, "open_aggression")
    assert "(" in axis3["label"], "session 3 should refine the style (molten reading)"
    assert axis3["w"] > 0, "but it still leans sharp — refined, not flipped"

    # provenance: every version bump is real, and exemplars name the games that earned the axis
    assert axis3["exemplar_ids"], "axes should pin the games that taught them (scenario 14)"


# =============================================================================
# frozen axis — the lion: a set-down style is not auto-touched by the dream
# =============================================================================

def test_frozen_axis_not_touched(sandbox):
    bm = sandbox["bookmarks"]
    _write_bookmarks(bm, [_game(f"g{i}", pole=+1, outcome=+1, surprise=0.7) for i in range(6)])
    S.update_bubble_soul("chess")
    soul = S.load_soul("chess")
    axis = S._find_axis(soul, "open_aggression")
    axis["frozen"] = True
    w_frozen = axis["w"]
    S.save_soul(soul)

    # feed the OPPOSITE outcome; a frozen axis must not move
    sandbox["bookmarks"].write_text("")
    _write_bookmarks(bm, [_game("flip", pole=+1, outcome=-1, surprise=0.9)])
    S.update_bubble_soul("chess")
    soul2 = S.load_soul("chess")
    assert S._find_axis(soul2, "open_aggression")["w"] == w_frozen, "frozen axis moved — the lion failed"


# =============================================================================
# reveries — minted from relational records, matched at most one with cooldown
# =============================================================================

def test_reveries_mint_and_match(sandbox):
    bm = sandbox["bookmarks"]
    _write_bookmarks(bm, [
        _game("joke", kind="joke", surprise=0.8, tone=0.7,
              note="Kamil resigned then claimed the cat walked on the board"),
        _game("g1", pole=+1, outcome=+1, surprise=0.6),
    ])
    S.update_bubble_soul("chess")  # mints reverie candidates

    data = R.load()
    assert data["reveries"], "the dream should have minted a reverie from the joke"

    # a chess-topic prompt strongly matches -> one reverie surfaces
    hit = R.match("let's play a game of chess, your move on the board", current_turn=10)
    assert hit is not None, "a strong on-topic match should surface a reverie"
    # restraint: an off-topic prompt surfaces nothing
    miss = R.match("what's the weather like today", current_turn=10)
    assert miss is None, "an off-topic prompt should surface no reverie (restraint is the design)"

    # cooldown: after firing, it won't fire again within the cooldown window
    R.record_fired(hit["id"], current_turn=10)
    again = R.match("chess board game move", current_turn=12, cooldown_turns=8)
    assert again is None, "a reverie fired too recently should respect its cooldown"
    later = R.match("chess board game move", current_turn=20, cooldown_turns=8)
    assert later is not None, "past the cooldown, the reverie is eligible again"
