"""
State Manager — Python mirror of the TypeScript state system.

Mirrors three classes from packages/core/src/state/:
  - StateManager (internal-states.ts): 6 epistemic states, 0-100, baseline 50
  - FeelingEngine (feeling-engine.ts): derives 14 feelings from states
  - ExpressionTrigger (expression-trigger.ts): fires expressions on threshold crossings

Returns StateResponse matching protocol.ts:
  { states: {...}, feelings: {...}, expressionsTriggered: [...] }
"""

from __future__ import annotations

import time
from typing import Any


# ─── Constants (mirrors shared/constants.ts) ──────────────────

STATE_NAMES = [
    "confidence", "contextSaturation", "alignment",
    "memoryPressure", "momentum", "trustCalibration",
]

FEELING_NAMES = [
    "happy", "sad", "frustrated", "curious", "proud",
    "anxious", "excited", "calm", "bored", "guilty",
    "angry", "blushing", "surprised", "relieved",
]

STATE_BASELINE = 50

# ─── Expression thresholds (mirrors expression-trigger.ts) ────

EXPRESSION_THRESHOLDS = [
    {"expression": "celebrate",   "feeling": "happy",      "threshold": 80,  "cooldown_ms": 60_000},
    {"expression": "cry",         "feeling": "sad",        "threshold": 75,  "cooldown_ms": 120_000},
    {"expression": "sigh",        "feeling": "frustrated", "threshold": 60,  "cooldown_ms": 30_000},
    {"expression": "head-tilt",   "feeling": "curious",    "threshold": 50,  "cooldown_ms": 15_000},
    {"expression": "fist-pump",   "feeling": "proud",      "threshold": 70,  "cooldown_ms": 60_000},
    {"expression": "tremble",     "feeling": "anxious",    "threshold": 70,  "cooldown_ms": 45_000},
    {"expression": "bounce",      "feeling": "excited",    "threshold": 65,  "cooldown_ms": 30_000},
    {"expression": "nod",         "feeling": "calm",       "threshold": 60,  "cooldown_ms": 20_000},
    {"expression": "yawn",        "feeling": "bored",      "threshold": 70,  "cooldown_ms": 90_000},
    {"expression": "facepalm",    "feeling": "guilty",     "threshold": 60,  "cooldown_ms": 60_000},
    {"expression": "puff-cheeks", "feeling": "angry",      "threshold": 65,  "cooldown_ms": 45_000},
    {"expression": "cover-face",  "feeling": "blushing",   "threshold": 50,  "cooldown_ms": 30_000},
    {"expression": "gasp",        "feeling": "surprised",  "threshold": 60,  "cooldown_ms": 15_000},
]


def _clamp(value: float) -> int:
    """Clamp to 0-100 integer."""
    return max(0, min(100, round(value)))


class StateManager:
    """
    Combined state + feeling + expression trigger system.
    Single class because the Python server is stateless between restarts —
    no need for the same granular separation as the TypeScript core.
    """

    def __init__(self) -> None:
        # Internal states — all start at baseline 50
        self.states: dict[str, int] = {name: STATE_BASELINE for name in STATE_NAMES}
        # Previous feelings for expression threshold crossing detection
        self._prev_feelings: dict[str, int] | None = None
        # Previous contextSaturation for surprised calculation
        self._prev_ctx_sat: int | None = None
        # Cooldown tracking: expression name -> last fired timestamp (ms)
        self._last_fired: dict[str, float] = {}

    def adjust(self, adjustments: list[tuple[str, float]]) -> dict[str, Any]:
        """
        Apply state adjustments, recalculate feelings, check expression thresholds.

        Args:
            adjustments: List of (state_name, delta) tuples

        Returns:
            StateResponse dict: { states, feelings, expressionsTriggered }
        """
        # 1. Apply deltas
        for state_name, delta in adjustments:
            if state_name in self.states:
                current = self.states[state_name]
                self.states[state_name] = max(0, min(100, round(current + delta)))

        # 2. Recalculate feelings
        feelings = self._recalculate_feelings()

        # 3. Check expression thresholds
        triggered = self._check_expressions(feelings)

        # 4. Update previous feelings for next call
        self._prev_ctx_sat = self.states["contextSaturation"]
        self._prev_feelings = dict(feelings)

        return {
            "states": dict(self.states),
            "feelings": feelings,
            "expressionsTriggered": triggered,
        }

    # ─── FeelingEngine mirror ─────────────────────────────────

    def _recalculate_feelings(self) -> dict[str, int]:
        """Mirror of FeelingEngine.recalculate() from feeling-engine.ts."""
        s = self.states
        conf = s["confidence"]
        ctx = s["contextSaturation"]
        align = s["alignment"]
        mem = s["memoryPressure"]
        mom = s["momentum"]
        trust = s["trustCalibration"]

        feelings: dict[str, int] = {}

        # happy: confidence * 0.4 + momentum * 0.3 + alignment * 0.3
        feelings["happy"] = _clamp(conf * 0.4 + mom * 0.3 + align * 0.3)

        # sad: 100 - (momentum * 0.5 + alignment * 0.5)
        feelings["sad"] = _clamp(100 - (mom * 0.5 + align * 0.5))

        # frustrated: only when momentum < 30
        if mom >= 30:
            feelings["frustrated"] = 0
        else:
            feelings["frustrated"] = _clamp(conf * 0.3 + (100 - mom) * 0.7)

        # curious: (100 - contextSaturation) * 0.6 + (100 - confidence) * 0.4
        feelings["curious"] = _clamp((100 - ctx) * 0.6 + (100 - conf) * 0.4)

        # proud: only when confidence > 70
        if conf <= 70:
            feelings["proud"] = 0
        else:
            feelings["proud"] = _clamp(conf * 0.4 + align * 0.4 + mom * 0.2)

        # anxious: (100 - confidence) * 0.5 + (100 - trustCalibration) * 0.5
        feelings["anxious"] = _clamp((100 - conf) * 0.5 + (100 - trust) * 0.5)

        # excited: only when momentum > 60
        if mom <= 60:
            feelings["excited"] = 0
        else:
            feelings["excited"] = _clamp(mom * 0.5 + (100 - ctx) * 0.5)

        # calm: low variance across all states (equilibrium)
        values = list(s.values())
        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        feelings["calm"] = _clamp(100 - (variance / 25))

        # bored: only when contextSaturation > 70
        if ctx <= 70:
            feelings["bored"] = 0
        else:
            feelings["bored"] = _clamp(ctx * 0.6 + (100 - mom) * 0.4)

        # guilty: only when alignment < 30
        if align >= 30:
            feelings["guilty"] = 0
        else:
            feelings["guilty"] = _clamp((100 - align) * 0.6 + trust * 0.4)

        # angry: only when alignment < 20
        if align >= 20:
            feelings["angry"] = 0
        else:
            feelings["angry"] = _clamp((100 - align) * 0.5 + mom * 0.5)

        # blushing: baseline from trustCalibration
        feelings["blushing"] = _clamp(trust * 0.3)

        # surprised: sudden contextSaturation drop (> 15 points)
        if self._prev_ctx_sat is None:
            feelings["surprised"] = 0
        else:
            delta = self._prev_ctx_sat - ctx
            feelings["surprised"] = _clamp(delta * 2) if delta > 15 else 0

        # relieved: placeholder (formula not yet defined in TypeScript)
        feelings["relieved"] = 0

        return feelings

    # ─── ExpressionTrigger mirror ─────────────────────────────

    def _check_expressions(self, feelings: dict[str, int]) -> list[str]:
        """Mirror of ExpressionTrigger.check() from expression-trigger.ts."""
        now = time.time() * 1000  # ms
        triggered: list[str] = []

        for rule in EXPRESSION_THRESHOLDS:
            current = feelings.get(rule["feeling"], 0)
            previous = (self._prev_feelings or {}).get(rule["feeling"], 0)

            # Must cross threshold upward
            if current <= rule["threshold"]:
                continue
            if previous > rule["threshold"]:
                continue

            # Check cooldown
            last = self._last_fired.get(rule["expression"], 0)
            if now - last < rule["cooldown_ms"]:
                continue

            # Fire
            self._last_fired[rule["expression"]] = now
            triggered.append(rule["expression"])

        return triggered
