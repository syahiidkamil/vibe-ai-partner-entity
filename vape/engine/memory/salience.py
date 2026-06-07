"""The two-gate salience policy — *consequence, not frequency*.

Entropy is only half the law: the *most* surprising string is random noise, and a
memory of noise is worse than useless. So salience runs in two gates at two points
(``memory_research/entropy-and-salience.md``):

- **Gate 1 — surprise gates ATTENTION** (live, in the hook, at bookmark-time). What
  gets noticed is decided by prediction-error, not topic and not frequency. A predicted
  event carries ~0 bits and is let go; a prediction-violating event carries many bits
  and crosses the bookmark threshold. ``info_value_saturation`` already *is* Shannon
  surprise, so the signal exists — Gate 1 just boosts a seed's pull by how wrong the
  prediction was.

- **Gate 2 — viability gates RETENTION** (offline, in the dream). Von Glasersfeld:
  knowledge is true only as long as it *works*. Gate 2 is the noise filter Gate 1
  cannot be — noise passes Gate 1 (maximally surprising) and fails Gate 2 (maximally
  useless); insight passes both. Four axes, all independent of frequency: **stakes**
  (cost to lose — the rare catastrophe-averter is FLOORED against eviction),
  **context** (thin evidence → default keep, evict slowly), **staleness** (the world
  changed and the lesson is now wrong → revise, subtracts), and **growth** (the
  deliberate divergence from biology — opens a capability / shifts an opinion / deepens
  a bond; weighted HIGHEST, because the goal is becoming *more*, not getting by).

Everything here is a **pure function** — no DB, no files, no clock side effects. The
firewall and the dream call these; this module never calls them. That keeps the policy
unit-testable in isolation and swappable beneath the firewall.
"""

from __future__ import annotations

from typing import Any

# --- Gate 1 -----------------------------------------------------------------------
GATE1_THRESHOLD = 0.6  # boosted pull above this → persist a bookmark

# --- Gate 2 axis weights ----------------------------------------------------------
# Growth is weighted HIGHEST on purpose — the named divergence from the biological,
# survival-only template. Staleness SUBTRACTS (a stale lesson is worth less, heading
# toward revision rather than retention).
W_STAKES = 0.30
W_CONTEXT = 0.20
W_GROWTH = 0.40
W_STALENESS = -0.30  # subtractive

# A high-stakes memory is floored against eviction regardless of the rest: losing the
# rare catastrophe-averter is the expensive mistake the whole policy exists to prevent.
STAKES_FLOOR = 0.8          # stakes at/above this → never evicted
VIABILITY_KEEP = 0.5        # gate2 score at/above → keep
VIABILITY_DEMOTE = 0.25     # below this (and not floored/stale) → demote toward cold
STALE_REVISE = 0.6          # staleness at/above → revise (molten reading), distinct fate
PROMOTE_VIABILITY = 0.85    # very-high viability + generality → promotion candidate


def _clip01(x: float) -> float:
    return 0.0 if x < 0.0 else 1.0 if x > 1.0 else x


def gate1_surprise(
    observed_pull: float,
    prediction_error: float,
    threshold: float = GATE1_THRESHOLD,
) -> tuple[float, bool]:
    """Gate 1: boost a seed's pull by its prediction-error; decide whether to bookmark.

    ``observed_pull`` is the seed's live salience (the qualia ``pull``, 0-1 scaled);
    ``prediction_error`` is how much the event violated the turn's prediction (0 = fully
    predicted ⇒ ~0 bits, 1 = maximally surprising). The boost is multiplicative-ish: a
    fully-predicted event keeps its pull, a maximally-surprising one can roughly double
    it (capped at 1.0). Returns ``(boosted_pull, should_bookmark)``.

    Note Gate 1 deliberately lets noise through — noise is maximally surprising. Gate 2
    is where noise dies. That separation is the design, not a bug.
    """
    pe = _clip01(prediction_error)
    pull = _clip01(observed_pull)
    boosted = _clip01(pull * (1.0 + pe))
    return boosted, boosted > threshold


def gate2_viability(
    stakes: float,
    context: float,
    staleness: float,
    growth: float,
) -> float:
    """Gate 2: the weighted viability score over the four axes, in [0, 1].

    All four inputs are 0-1. Growth dominates (the divergence from biology); staleness
    subtracts. A high-``stakes`` memory is FLOORED — it returns a viability of at least
    ``VIABILITY_KEEP`` no matter how the other axes fall, so the rare-but-critical lesson
    is never scored into eviction. The score is what ``eviction_action`` thresholds on.
    """
    stakes = _clip01(stakes)
    context = _clip01(context)
    staleness = _clip01(staleness)
    growth = _clip01(growth)

    raw = (
        W_STAKES * stakes
        + W_CONTEXT * context
        + W_GROWTH * growth
        + W_STALENESS * staleness
    )
    # normalize into [0,1] over the achievable positive range (weights sum, ignoring the
    # subtractive staleness term whose worst case is handled by the clip).
    score = _clip01(raw / (W_STAKES + W_CONTEXT + W_GROWTH))

    if stakes >= STAKES_FLOOR:
        score = max(score, VIABILITY_KEEP)
    return score


def _axes_from_row(row: dict[str, Any]) -> tuple[float, float, float, float]:
    """Pull the four salience axes out of a row's ``meta`` (with sane defaults).

    Axes live under ``meta`` (the schema's documented home: ``viability axes
    {stakes,context,staleness,growth}``). Missing axes default toward *keep* — thin
    evidence should not get a row evicted (the context axis principle, applied to the
    absence of the axes themselves).
    """
    meta = row.get("meta") or {}
    if isinstance(meta, str):  # defensive: a raw jsonb string slipped through
        import json

        try:
            meta = json.loads(meta)
        except Exception:
            meta = {}
    axes = meta.get("axes", {}) if isinstance(meta, dict) else {}
    stakes = float(axes.get("stakes", row.get("surprise", 0.0) or 0.0))
    context = float(axes.get("context", 0.5))   # default mid — "few cases, keep slowly"
    staleness = float(axes.get("staleness", 0.0))
    growth = float(axes.get("growth", 0.0))
    return stakes, context, staleness, growth


def eviction_action(row: dict[str, Any]) -> str:
    """Choose the fate of one row: ``keep`` | ``merge`` | ``demote`` | ``revise`` |
    ``promote``. Devaluation, never silent-delete — the action a tombstone enacts.

    Order of judgement:
      1. **stale → revise** — if the world changed and the lesson is now wrong, its fate
         is the molten reading (revise the meaning, keep the fact), a *separate* track
         from the budget. Checked first so a stale-but-otherwise-viable lesson is revised
         rather than kept-as-is.
      2. **floored stakes → keep** — the rare catastrophe-averter is never evicted.
      3. **promote** — very-high viability AND general scope (``meta.scope == 'any'`` or
         a ``promote`` flag) ⇒ a candidate to lift toward the judge-book. (PROPOSE-only
         upstream if it would move a set-point; this function only *flags* it.)
      4. by viability score: ``keep`` ≥ KEEP, ``merge`` if a near-duplicate is flagged in
         meta, else ``demote`` below DEMOTE. The middle band defaults to ``keep`` — thin
         evidence evicts slowly.
    """
    stakes, context, staleness, growth = _axes_from_row(row)
    meta = row.get("meta") or {}
    if isinstance(meta, str):
        import json

        try:
            meta = json.loads(meta)
        except Exception:
            meta = {}

    # 1. stale → revise (the molten reading), a separate fate from the budget. Checked
    #    first so a stale-but-otherwise-viable lesson is revised, not silently kept.
    if staleness >= STALE_REVISE:
        return "revise"

    score = gate2_viability(stakes, context, staleness, growth)

    # 2. promote — checked BEFORE the stakes floor: promotion is ELEVATION, not eviction,
    #    so a high-value general lesson should be lifted toward the judge-book rather than
    #    merely protected in place. (PROPOSE-only upstream if it would move a set-point.)
    scope = meta.get("scope") if isinstance(meta, dict) else None
    wants_promote = bool(meta.get("promote")) if isinstance(meta, dict) else False
    if score >= PROMOTE_VIABILITY and (scope == "any" or wants_promote):
        return "promote"

    # 3. floored stakes → keep — the rare catastrophe-averter is never evicted.
    if stakes >= STAKES_FLOOR:
        return "keep"

    # 4. near-duplicate → merge (the dream folds them).
    if meta.get("duplicate_of") if isinstance(meta, dict) else False:
        return "merge"

    # 5. by viability: keep at/above KEEP, demote below DEMOTE, keep the uncertain middle
    #    (thin evidence evicts slowly).
    if score >= VIABILITY_KEEP:
        return "keep"
    if score < VIABILITY_DEMOTE:
        return "demote"
    return "keep"
