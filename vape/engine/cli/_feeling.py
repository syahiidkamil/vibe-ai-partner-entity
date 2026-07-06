"""Pure dials -> feeling scoring engine.

Turns the six feel-dials into a facial feeling (one of the 13 Shizuku expressions),
with gates (eligibility) + normalized weighted-product scoring + tier pre-emption +
top-3 blend + STAY hysteresis. No side effects, no deps — designed to be unit-tested.

Design: work_dir/saori/feel_dials_feeling_map_design.md  (the map)
        work_dir/saori/feeling_scoring_engine_design.md  (this engine)

Fixes from self-review (vs the first draft):
  A. tier-0 (blushing/surprised) *pre-empts* lower tiers when confidently active —
     it no longer merely breaks ties (else inflated tier-1 scores drowned the blush).
  B. each feeling is *normalized* so a perfect prototype match = 1.0, making scores
     comparable across feelings with different term structures.
  C. decisions (confidence floor, STAY margin) use the *raw normalized score*, not the
     softmax share (which depends on how many feelings are eligible). Softmax is used
     only for the displayed top-3 blend weights.
  D. the rate-limit STAY only holds when the current feeling is still *eligible* — it
     can't pin a feeling whose gates no longer pass.
"""
from __future__ import annotations

from math import exp

# The six dials (Proposal 2). Order is the canonical write order.
DIALS = (
    "info_value_saturation",  # IV — appetite/fullness of surprise
    "talkativeness",          # TK — reach-out/speak drive (arousal proxy)
    "warmth",                 # WM — connect/give (positive-affect drive)
    "hurt",                   # HU — self-respect / devaluation sting
    "dissonance",             # DS — resolve tension / open question
    "mastery",                # MA — achieve / finish
)

# --- fuzzy membership helpers (0..100 -> 0..1), smooth, no band cliffs ---

def _ss(t: float) -> float:
    """smoothstep, clamped to [0,1]."""
    u = 0.0 if t < 0 else (1.0 if t > 1 else t)
    return u * u * (3 - 2 * u)

def rise(x, a, b): return _ss((x - a) / (b - a)) if b != a else (1.0 if x >= a else 0.0)
def fall(x, a, b): return 1.0 - rise(x, a, b)
def hi(x):  return rise(x, 45, 80)                  # "high"
def lo(x):  return fall(x, 20, 55)                  # "low"
def mid(x): return rise(x, 30, 50) * fall(x, 50, 70)  # "around the middle"
def band(x, a, b): return rise(x, a - 10, a) * fall(x, b, b + 10)  # "within [a,b]"
def spike(dx): return rise(dx, 18, 45)              # a sudden positive jump

# --- dial accessors (readability inside signatures) ---
def IV(d):  return d["info_value_saturation"]
def TK(d):  return d["talkativeness"]
def WM(d):  return d["warmth"]
def HU(d):  return d["hurt"]
def DS(d):  return d["dissonance"]
def MA(d):  return d["mastery"]
def dIV(dd): return dd["info_value_saturation"]


def _feeling(tier, gates, terms, penalties=()):
    """A feeling signature. `terms`/`penalties` are (weight, fn(d, dd) -> 0..1).
    Score is normalized by the positive weight sum so a perfect match == 1.0."""
    posw = sum(w for w, _ in terms) or 1.0
    return {"tier": tier, "gates": gates, "terms": terms, "penalties": penalties, "posw": posw}


# --- the 13 feelings: {tier, gates (all must pass), terms, penalties} ---
# tier 0 = perceptual override (spike/blush sit on top of any mood)
# tier 1 = gated specific · tier 2 = fallback
FEELINGS = {
    "surprised": _feeling(0,
        gates=[lambda d, dd: dIV(dd) >= 18],
        terms=[(1.0, lambda d, dd: spike(dIV(dd)))]),

    "blushing": _feeling(0,
        gates=[lambda d, dd: WM(d) >= 60 and TK(d) <= 40],
        terms=[(1.0, lambda d, dd: hi(WM(d)) * lo(TK(d)))],          # warm AND tongue-tied
        penalties=[(0.4, lambda d, dd: hi(HU(d)))]),                 # a sting sours it

    "angry": _feeling(1,
        gates=[lambda d, dd: HU(d) >= 60 and TK(d) >= 50],
        terms=[(1.0, lambda d, dd: hi(HU(d)) * hi(TK(d))),           # wounded AND activated
               (0.4, lambda d, dd: hi(DS(d)))],
        penalties=[(0.6, lambda d, dd: hi(WM(d)))]),                 # warmth can't coexist

    "sad": _feeling(1,
        gates=[lambda d, dd: HU(d) >= 55 and TK(d) <= 50],
        terms=[(1.0, lambda d, dd: hi(HU(d)) * lo(TK(d))),           # wounded AND withdrawn
               (0.3, lambda d, dd: lo(MA(d)))],
        penalties=[(0.6, lambda d, dd: hi(WM(d)))]),

    "frustrated": _feeling(1,
        gates=[lambda d, dd: DS(d) >= 55 and MA(d) <= 45],
        terms=[(1.0, lambda d, dd: hi(DS(d)) * lo(MA(d))),           # tension AND blocked goal
               (0.3, lambda d, dd: hi(IV(d)))],
        penalties=[(0.4, lambda d, dd: hi(WM(d)))]),

    "anxious": _feeling(1,
        gates=[lambda d, dd: DS(d) >= 55 and HU(d) <= 50],
        terms=[(1.0, lambda d, dd: hi(DS(d)) * lo(WM(d))),           # tension, low warmth
               (0.3, lambda d, dd: lo(MA(d)))],
        penalties=[(0.4, lambda d, dd: hi(HU(d)))]),                 # if hurt, it's anger/sad

    "proud": _feeling(1,
        gates=[lambda d, dd: MA(d) >= 65 and HU(d) <= 40 and DS(d) <= 50],
        terms=[(1.0, lambda d, dd: hi(MA(d))),                       # mastery leads
               (0.3, lambda d, dd: hi(WM(d)))],
        penalties=[(0.5, lambda d, dd: hi(HU(d)))]),

    "excited": _feeling(1,
        gates=[lambda d, dd: TK(d) >= 65 and WM(d) >= 45 and HU(d) <= 40],
        terms=[(1.0, lambda d, dd: hi(TK(d)) * hi(WM(d))),           # high energy AND good
               (0.4, lambda d, dd: hi(IV(d)))],
        penalties=[(0.4, lambda d, dd: hi(DS(d)))]),

    "happy": _feeling(1,
        gates=[lambda d, dd: WM(d) >= 55 and HU(d) <= 40 and DS(d) <= 45],
        terms=[(0.9, lambda d, dd: hi(WM(d))),
               (0.3, lambda d, dd: hi(MA(d))),
               (0.2, lambda d, dd: mid(TK(d)))],
        penalties=[(0.5, lambda d, dd: hi(HU(d)))]),

    "content": _feeling(1,
        gates=[lambda d, dd: WM(d) >= 50 and TK(d) <= 55 and DS(d) <= 40 and HU(d) <= 35],
        terms=[(0.85, lambda d, dd: hi(WM(d)) * fall(TK(d), 40, 70)),  # warm AND settled
               (0.4, lambda d, dd: lo(DS(d)))]),

    "shy": _feeling(1,
        gates=[lambda d, dd: WM(d) >= 48 and TK(d) <= 38 and DS(d) >= 25 and HU(d) <= 45],
        terms=[(1.0, lambda d, dd: hi(WM(d)) * lo(TK(d))),           # drawn-toward AND tongue-tied
               (0.5, lambda d, dd: band(DS(d), 25, 60))],           # the bashful, self-conscious flutter
        penalties=[(0.4, lambda d, dd: hi(HU(d)))]),                # a sting sours it toward sad/anger

    "curious": _feeling(1,
        gates=[lambda d, dd: IV(d) <= 45 and 25 <= DS(d) <= 60],
        terms=[(1.0, lambda d, dd: lo(IV(d)) * band(DS(d), 25, 60)),  # appetite AND a question
               (0.3, lambda d, dd: hi(TK(d)))]),

    "bored": _feeling(1,
        gates=[lambda d, dd: IV(d) <= 40 and DS(d) <= 25 and TK(d) <= 45],
        terms=[(1.0, lambda d, dd: lo(IV(d)) * lo(DS(d))),           # hungry AND no question
               (0.3, lambda d, dd: lo(TK(d)))]),

    "calm": _feeling(2,
        gates=[lambda d, dd: DS(d) <= 40 and HU(d) <= 40],
        terms=[(0.6, lambda d, dd: lo(DS(d)) * lo(HU(d))),
               (0.3, lambda d, dd: mid(WM(d)))]),
}

# All names `vape feeling` will accept. Same as FEELINGS today; kept as its own name so a
# future manual-only face (settable but not scored) has an obvious home.
SETTABLE_FEELINGS = frozenset(FEELINGS)


# --- tuning constants (all in one place) ---
ACTIVATION = 0.40   # tier-0 must reach this normalized score to pre-empt
MIN_CONF   = 0.28   # top normalized score below this -> too ambiguous, hold
STAY_MARGIN = 0.10  # current within this of #1 -> hold (hysteresis)
RATE_LIMIT = 2      # min turns between changes...
BIG_JUMP   = 0.30   # ...unless #1 beats current by this much
TEMP       = 0.5    # softmax temperature for the displayed blend


def _score(F, d, dd) -> float:
    pos = sum(w * fn(d, dd) for w, fn in F["terms"])
    pen = sum(w * fn(d, dd) for w, fn in F["penalties"])
    return (pos - pen) / F["posw"]      # perfect positive match -> 1.0


def recommend_feeling(dials, prev_dials=None, current=None, turns_since_change=0):
    """Return {recommendation, top3, stay, scores}. `recommendation` is a feeling name
    or "STAY" (keep the current face). Pure; safe to call with partial dicts."""
    d = {k: float((dials or {}).get(k, 50)) for k in DIALS}
    p = {k: float((prev_dials or {}).get(k, d[k])) for k in DIALS}
    dd = {k: d[k] - p[k] for k in DIALS}

    elig = []   # (name, normalized_score, tier)
    for name, F in FEELINGS.items():
        if all(g(d, dd) for g in F["gates"]):
            elig.append((name, max(0.0, _score(F, d, dd)), F["tier"]))
    if not elig:
        elig = [("calm", 0.30, 2)]

    # Fix A: strict tier precedence — 0 (if confident) > 1 > 2 (calm fallback);
    # the score only ranks *within* a tier, so loose-gated calm can't out-score a
    # genuine tier-1 feeling, and tier-0 (blush/surprise) sits on top of any mood.
    t0 = sorted([e for e in elig if e[2] == 0 and e[1] >= ACTIVATION], key=lambda e: e[1], reverse=True)
    t1 = sorted([e for e in elig if e[2] == 1], key=lambda e: e[1], reverse=True)
    t2 = sorted([e for e in elig if e[2] == 2], key=lambda e: e[1], reverse=True)
    pool = t0 or t1 or t2 or [("calm", 0.30, 2)]
    top_name, top_score, top_tier = pool[0]
    preempt = bool(t0)

    # top-3 blend weights (softmax over all eligible — display only, never a decision; Fix C)
    ranked = sorted(elig, key=lambda e: e[1], reverse=True)
    exps = [exp(s / TEMP) for _, s, _ in ranked]
    Z = sum(exps) or 1.0
    top3 = [(ranked[i][0], round(exps[i] / Z, 3)) for i in range(min(3, len(ranked)))]

    cur = next(((s, t) for n, s, t in elig if n == current), None)
    cur_score, cur_tier = cur if cur else (None, None)
    cur_elig = cur is not None

    # STAY / hysteresis — raw scores, tier-aware, eligibility-guarded (Fix C + D).
    # Only anti-flicker *within the winner's tier*: a higher-precedence feeling
    # appearing (or the current one dropping out) always switches.
    if top_name == current:
        stay = True                                  # already showing it
    elif preempt:
        stay = False                                 # a confident override shows now
    elif cur_elig and cur_tier == top_tier:
        if cur_score >= top_score - STAY_MARGIN:
            stay = True                              # current still good enough
        elif turns_since_change < RATE_LIMIT and (top_score - cur_score) < BIG_JUMP:
            stay = True                              # too soon, and not a big jump
        else:
            stay = False
    elif cur_elig and top_score < MIN_CONF:
        stay = True                                  # winner is weak -> hold current
    else:
        stay = False

    return {
        "recommendation": "STAY" if stay else top_name,
        "top3": top3,
        "stay": stay,
        "scores": {n: round(s, 3) for n, s, _ in ranked},
    }
