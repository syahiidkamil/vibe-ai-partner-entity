"""Reveries — the callback at the right moment.

A reverie is the *re-surfacing* half of memory (Ford's word, from Westworld): a past
moment returning at the right moment. The deep dream mints 1-3 candidates — a moment +
a trigger-condition + a cooldown — into ``reveries.json``; live, the hook checks the
current prompt against the triggers and surfaces **at most one** on a strong match.

**Restraint IS the design.** A reverie every turn is flicker and reads as a machine dumping
memory; one well-timed callback reads as a self that genuinely remembers. The dynamism
lesson: not the recall itself, but the timing of it. So ``match`` returns at most one, only
on a real match, and only if past its cooldown.

Ownership: the SOUL owns minting (it calls ``mint``); the hook reaches ``match`` via
bubble.py's re-export, so the hook's imports stay on bubble-system. This module touches only
``reveries.json`` (files + git, identity-adjacent, diffable) — no DB.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from engine.memory.config import REVERIES_PATH

DEFAULT_COOLDOWN_TURNS = 8
MATCH_THRESHOLD = 0.34  # fraction of trigger tokens that must hit before a reverie is "strong"


# =============================================================================
# load / save
# =============================================================================

def _empty() -> dict[str, Any]:
    return {"reveries": []}


def load() -> dict[str, Any]:
    """Load reveries.json, or an empty store if absent."""
    if not REVERIES_PATH.exists():
        return _empty()
    try:
        with REVERIES_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return _empty()
    data.setdefault("reveries", [])
    return data


def save(data: dict[str, Any]) -> None:
    """Persist reveries.json (atomic-ish via temp + replace)."""
    REVERIES_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = REVERIES_PATH.with_suffix(".json.tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    tmp.replace(REVERIES_PATH)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _slug(moment: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", moment.lower()).strip("-")[:48] or "reverie"


# =============================================================================
# mint — soul hands in candidates, we persist (capped, de-duplicated)
# =============================================================================

def mint(candidates: list[dict[str, Any]], *, maxn: int = 3) -> None:
    """Write up to ``maxn`` reverie candidates into reveries.json.

    Each candidate: {bubble, moment, trigger, cooldown_turns?, tone?, ref?}. We assign a
    stable id (from the moment slug), keep the existing ``last_fired_turn`` / ``turn_seen``
    bookkeeping if the reverie already exists, and cap the store so it never balloons.
    """
    if not candidates:
        return
    data = load()
    existing = {r.get("id"): r for r in data["reveries"]}

    minted = 0
    for cand in candidates:
        if minted >= maxn:
            break
        moment = (cand.get("moment") or "").strip()
        if not moment:
            continue
        rid = cand.get("id") or f"{cand.get('bubble', 'global')}:{_slug(moment)}"
        rec = {
            "id": rid,
            "bubble": cand.get("bubble", "global"),
            "moment": moment,
            "trigger": cand.get("trigger", ""),
            "cooldown_turns": int(cand.get("cooldown_turns", DEFAULT_COOLDOWN_TURNS)),
            "tone": float(cand.get("tone", 0.0)),
            "ref": cand.get("ref"),
            "minted_at": _now_iso(),
            # preserve firing history across re-mints so cooldown survives a dream
            "last_fired_turn": existing.get(rid, {}).get("last_fired_turn"),
        }
        existing[rid] = rec
        minted += 1

    # keep the store bounded: the most recently minted win
    merged = list(existing.values())
    merged.sort(key=lambda r: r.get("minted_at") or "", reverse=True)
    data["reveries"] = merged[:12]
    save(data)


# =============================================================================
# match — at most one, strong match, past cooldown
# =============================================================================

def _trigger_tokens(trigger: str) -> set[str]:
    raw = re.split(r"[\s,]+|(?:\bOR\b)|(?:\bAND\b)", trigger)
    return {t.strip().lower() for t in raw if t.strip() and t.strip().upper() not in ("OR", "AND")}


def _match_strength(prompt: str, trigger: str) -> float:
    """Fraction of trigger tokens present in the prompt (cheap keyword overlap)."""
    toks = _trigger_tokens(trigger)
    if not toks:
        return 0.0
    p = prompt.lower()
    hits = sum(1 for t in toks if t in p)
    return hits / len(toks)


def match(prompt: str, *, cooldown_turns: int = DEFAULT_COOLDOWN_TURNS,
          current_turn: Optional[int] = None,
          bubble: Optional[str] = None) -> Optional[dict[str, Any]]:
    """Return AT MOST ONE reverie whose trigger strongly matches the prompt and that is past
    its cooldown — or None. Restraint is the design.

    ``current_turn`` (if given) is compared against each reverie's ``last_fired_turn`` +
    ``cooldown_turns`` so a callback doesn't fire twice in a row. When it fires, the caller
    (the hook) should call ``record_fired`` so the cooldown takes effect.
    """
    data = load()
    best: Optional[dict[str, Any]] = None
    best_strength = MATCH_THRESHOLD  # must clear the bar to count as "strong"

    for r in data["reveries"]:
        if bubble is not None and r.get("bubble") not in (bubble, "global"):
            continue
        # cooldown gate
        last = r.get("last_fired_turn")
        cd = int(r.get("cooldown_turns", cooldown_turns))
        if last is not None and current_turn is not None and (current_turn - last) < cd:
            continue
        strength = _match_strength(prompt, r.get("trigger", ""))
        if strength > best_strength:
            best_strength = strength
            best = r

    return best


def record_fired(reverie_id: str, *, current_turn: Optional[int] = None) -> None:
    """Stamp a reverie as fired so its cooldown begins. Called by the hook after surfacing."""
    data = load()
    for r in data["reveries"]:
        if r.get("id") == reverie_id:
            r["last_fired_turn"] = current_turn if current_turn is not None else 0
            r["fired_at"] = _now_iso()
            break
    save(data)
