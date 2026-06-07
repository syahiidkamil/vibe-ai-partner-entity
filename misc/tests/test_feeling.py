"""Unit tests for the dials -> feeling scoring engine (engine/cli/_feeling.py).

The canonical cases ARE the mapping table, encoded as assertions; the regression
tests pin the four self-review bugs (blush reachable, scores comparable, raw-score
confidence, eligibility-guarded STAY)."""
import itertools

import pytest

from engine.cli._feeling import recommend_feeling, DIALS


def D(**kw):
    """A full dial dict, neutral (50) baseline with overrides."""
    base = {k: 50 for k in DIALS}
    base.update(kw)
    return base


# --- canonical: one clear dial-vector per feeling (current=None, no spike) ---
CASES = [
    ("happy",      dict(warmth=85, hurt=5,  dissonance=10, mastery=65, talkativeness=55, info_value_saturation=55)),
    ("proud",      dict(mastery=90, hurt=5,  dissonance=15, warmth=45, talkativeness=45)),
    ("excited",    dict(talkativeness=85, warmth=70, hurt=10, info_value_saturation=70, dissonance=15, mastery=55)),
    ("content",    dict(warmth=70, talkativeness=50, dissonance=15, hurt=10, mastery=45, info_value_saturation=45)),
    ("calm",       dict(warmth=45, talkativeness=35, dissonance=10, hurt=10, mastery=50, info_value_saturation=50)),
    ("curious",    dict(info_value_saturation=30, dissonance=40, talkativeness=55, warmth=40, hurt=20, mastery=50)),
    ("bored",      dict(info_value_saturation=20, dissonance=15, talkativeness=35, warmth=40, hurt=15, mastery=45)),
    ("sad",        dict(hurt=80, talkativeness=25, warmth=15, mastery=20, dissonance=40, info_value_saturation=40)),
    ("angry",      dict(hurt=80, talkativeness=70, warmth=10, dissonance=50, mastery=30, info_value_saturation=50)),
    ("frustrated", dict(dissonance=75, mastery=15, warmth=50, hurt=30, talkativeness=55, info_value_saturation=65)),
    ("anxious",    dict(dissonance=75, hurt=20, warmth=20, mastery=35, talkativeness=45, info_value_saturation=50)),
    ("blushing",   dict(warmth=80, talkativeness=25, hurt=10, dissonance=10, mastery=50, info_value_saturation=50)),
]


@pytest.mark.parametrize("expected,ov", CASES, ids=[c[0] for c in CASES])
def test_canonical_feeling(expected, ov):
    d = D(**ov)
    rec = recommend_feeling(d, prev_dials=d, current=None)   # prev==cur -> no spike
    assert rec["recommendation"] == expected, (expected, rec["scores"])


# --- surprised: a spike, the one Δ-based feeling ---
def test_surprised_on_iv_spike():
    rec = recommend_feeling(D(info_value_saturation=75),
                            prev_dials=D(info_value_saturation=40), current=None)
    assert rec["recommendation"] == "surprised"


def test_no_surprise_without_spike():
    d = D(info_value_saturation=75)
    rec = recommend_feeling(d, prev_dials=d, current=None)   # ΔIV = 0
    assert rec["recommendation"] != "surprised"


# --- regression A/B: blush is reachable; it is NOT drowned by content ---
def test_blush_beats_content_when_warm_and_quiet():
    d = D(warmth=70, talkativeness=35)            # the exact case that was buggy
    rec = recommend_feeling(d, prev_dials=d, current=None)
    assert rec["recommendation"] == "blushing", rec["scores"]


# --- regression D: STAY must not pin an ineligible current feeling ---
def test_switches_when_current_ineligible():
    sad = D(hurt=80, talkativeness=25, warmth=15, mastery=20, dissonance=40, info_value_saturation=40)
    rec = recommend_feeling(sad, prev_dials=sad, current="happy", turns_since_change=0)
    assert rec["recommendation"] == "sad"         # happy ineligible -> switch, never STAY


# --- STAY / hysteresis behaviour ---
def test_stay_when_already_showing():
    d = D(warmth=85, hurt=5, dissonance=10, mastery=65, talkativeness=55, info_value_saturation=55)
    rec = recommend_feeling(d, prev_dials=d, current="happy")
    assert rec["recommendation"] == "STAY"


def test_stay_holds_within_margin_same_tier():
    # content edges out happy, but both tier-1 and close -> hold happy (anti-flicker)
    d = D(warmth=70, talkativeness=50, dissonance=15, hurt=10, mastery=45, info_value_saturation=45)
    rec = recommend_feeling(d, prev_dials=d, current="happy", turns_since_change=5)
    assert rec["stay"] is True


def test_blush_preempts_even_a_held_feeling():
    d = D(warmth=80, talkativeness=25, hurt=10, dissonance=10)
    rec = recommend_feeling(d, prev_dials=d, current="content", turns_since_change=5)
    assert rec["recommendation"] == "blushing"    # tier-0 override beats STAY


# --- shape of the output ---
def test_output_shape():
    d = D(warmth=85, hurt=5, mastery=65)
    rec = recommend_feeling(d, prev_dials=d, current=None)
    assert set(rec) == {"recommendation", "top3", "stay", "scores"}
    assert 1 <= len(rec["top3"]) <= 3
    assert all(0.0 <= w <= 1.0 for _, w in rec["top3"])


# --- coverage: never crashes over a coarse grid, most feelings reachable ---
def test_grid_no_crash_and_coverage():
    seen = set()
    for combo in itertools.product((15, 50, 85), repeat=len(DIALS)):
        d = dict(zip(DIALS, combo))
        for dlt in (0, 30):
            prev = dict(d, info_value_saturation=max(0, d["info_value_saturation"] - dlt))
            rec = recommend_feeling(d, prev_dials=prev, current=None)
            seen.add(rec["recommendation"])
    seen.discard("STAY")
    assert len(seen) >= 9, sorted(seen)           # coarse grid reaches most of the 13
    assert "blushing" in seen and "surprised" in seen
