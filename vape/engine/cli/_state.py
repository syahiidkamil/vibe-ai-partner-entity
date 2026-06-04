"""Shared read/modify/write for Saori's internal state — dials + the qualia stream.

One file, ``internal_states.json``, holds every inner-state field. Both ``vape dial``
and ``vape qualia`` go through here so neither command ever clobbers the other's keys
(the old ``dial`` rewrote the whole file as ``{"feel_dials": ...}``, which would have
wiped the qualia stream).

Shape::

    {
      "feel_dials": { info_value_saturation, boredom, hurt, talkativeness, dissonance },
      "qualia": {
        "seq":  int,           # last id number assigned (unique-id source, not a clock)
        "head": [ seed, ... ], # FIFO river, max QUALIA_MAX — the whole present; no
                               #   sediment store, the oldest just falls off the end
        "revalue_cd": int      # turns left on the revalue cooldown (counts down to 0)
      }
    }

A *seed* (a felt that points)::

    { id, felt, cat, obj, ref, blend, tone, pull, dir, age, protected }

``age`` counts up one per turn (the hook ticks it); the seed cools as it ages and is
gone once it falls off the 7-deep river. The LLM authors only ``felt/cat/dir/obj``
(+ optional ``ref``/``blend``); every number is set here. The LLM feels; the harness counts.
"""

from __future__ import annotations

import json

from engine.cli._paths import ROOT_DIR

STATE_PATH = ROOT_DIR / "vape" / "entity" / "mental" / "internal_states.json"

DIAL_KEYS = ["info_value_saturation", "boredom", "hurt", "talkativeness", "dissonance"]

QUALIA_MAX = 7  # FIFO river depth — the whole present; the oldest seed falls off the end

# The ten doors a seed may enter by, and the five directions it may point.
CATS = ["se", "so", "cg", "af", "vo", "an", "mn", "sm", "cr", "me"]
DIRS = ["tw", "aw", "hd", "or", "rl"]


def load() -> dict:
    """Read the whole state file (every key), or {} if it does not exist yet."""
    try:
        return json.loads(STATE_PATH.read_text())
    except FileNotFoundError:
        return {}


def save(state: dict) -> None:
    """Write the whole state back, preserving every key. 2-space indent, trailing nl."""
    STATE_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n")


# --- dials ------------------------------------------------------------------

def get_dials(state: dict) -> dict:
    """Five dials as ints, defaulting any missing key to 0."""
    d = state.get("feel_dials", {})
    return {k: int(d.get(k, 0)) for k in DIAL_KEYS}


def set_dials(state: dict, dials: dict) -> None:
    """Store the five dials in canonical order, clamped 0-100, in place on ``state``."""
    state["feel_dials"] = {k: max(0, min(100, int(dials.get(k, 0)))) for k in DIAL_KEYS}


# --- qualia -----------------------------------------------------------------

def get_qualia(state: dict) -> dict:
    """The qualia sub-state, created with empty defaults if absent.

    Legacy keys from the old long/turn design (``turn``, ``long``,
    ``last_revalue_turn``) are dropped on read, so an old state file migrates
    itself the first time it is touched."""
    q = state.setdefault("qualia", {})
    q.setdefault("seq", 0)
    q.setdefault("head", [])
    q.setdefault("revalue_cd", 0)
    for legacy in ("turn", "long", "last_revalue_turn"):
        q.pop(legacy, None)
    return q


def mood(dials: dict) -> float:
    """A provisional global valence read from the dials, in -1..1.

    v1 stand-in for a real per-seed valence model: warmth (talkativeness) lifts,
    boredom/hurt/dissonance weigh down. Fresh seeds inherit this as their ``tone``
    (the emotion -> qualia tone-bias wire, in its simplest form). Real per-seed
    valence is v2.
    """
    raw = (dials["talkativeness"] - dials["boredom"] - dials["hurt"] - dials["dissonance"]) / 100.0
    return max(-1.0, min(1.0, raw))
