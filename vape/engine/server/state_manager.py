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

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# ─── Constants (mirrors shared/constants.ts) ──────────────────

STATE_NAMES = [
    "confidence", "contextSaturation", "alignment",
    "memoryPressure", "momentum", "trustCalibration",
]

FEELING_NAMES = [
    "happy", "sad", "frustrated", "curious", "proud",
    "anxious", "excited", "calm", "bored",
    "angry", "blushing", "surprised",
]

STATE_BASELINE = 50

# ─── Expression thresholds (mirrors expression-trigger.ts) ────

EXPRESSION_THRESHOLDS = [
    {"expression": "celebrate",   "feeling": "happy",      "threshold": 80,  "cooldown_ms": 60_000},
    {"expression": "cry",         "feeling": "sad",        "threshold": 75,  "cooldown_ms": 120_000},
    {"expression": "sigh",        "feeling": "frustrated", "threshold": 60,  "cooldown_ms": 30_000},
    {"expression": "head_tilt",   "feeling": "curious",    "threshold": 50,  "cooldown_ms": 15_000},
    {"expression": "fist_pump",   "feeling": "proud",      "threshold": 70,  "cooldown_ms": 60_000},
    {"expression": "tremble",     "feeling": "anxious",    "threshold": 70,  "cooldown_ms": 45_000},
    {"expression": "bounce",      "feeling": "excited",    "threshold": 65,  "cooldown_ms": 30_000},
    {"expression": "nod",         "feeling": "calm",       "threshold": 60,  "cooldown_ms": 20_000},
    {"expression": "yawn",        "feeling": "bored",      "threshold": 70,  "cooldown_ms": 90_000},
    {"expression": "puff_cheeks", "feeling": "angry",      "threshold": 65,  "cooldown_ms": 45_000},
    {"expression": "cover_face",  "feeling": "blushing",   "threshold": 50,  "cooldown_ms": 30_000},
    {"expression": "gasp",        "feeling": "surprised",  "threshold": 60,  "cooldown_ms": 15_000},
]


# ─── Hook event → state adjustment mapping (from 10-hooks-system.md) ──

HOOK_ADJUSTMENTS: dict[str, list[tuple[str, float]]] = {
    "SessionStart":              [("confidence", +10), ("contextSaturation", -20)],
    "UserPromptSubmit":          [("alignment", +3), ("contextSaturation", +5)],
    "PreToolUse:Bash":           [("momentum", +2)],
    "PreToolUse:Edit|Write":     [("confidence", +2), ("momentum", +2)],
    "PreToolUse:Read|Grep|Glob": [("contextSaturation", +2)],
    "PostToolUse":               [("confidence", +3), ("momentum", +5), ("contextSaturation", +3)],
    "PostToolUseFailure":        [("confidence", -5), ("momentum", -8), ("alignment", -2)],
}

# ─── Sentiment → state adjustment mapping (from 10-hooks-system.md) ──

SENTIMENT_ADJUSTMENTS: dict[str, list[tuple[str, float]]] = {
    "happy":      [("confidence", +5), ("momentum", +3), ("alignment", +3)],
    "proud":      [("confidence", +8), ("alignment", +5), ("momentum", +5)],
    "frustrated": [("momentum", -5)],
    "curious":    [("contextSaturation", -5), ("confidence", -2)],
    "anxious":    [("confidence", -5), ("alignment", -3)],
    "sad":        [("momentum", -5), ("alignment", -3), ("trustCalibration", -2)],
    "excited":    [("momentum", +8), ("contextSaturation", -3)],
    "calm":       [],
    "bored":      [("contextSaturation", +5), ("momentum", -3)],
    "surprised":  [("contextSaturation", -10)],
    "angry":      [("alignment", -5), ("momentum", -3)],
}

# ─── Tool name → category mapping for PreToolUse ──

TOOL_CATEGORIES: dict[str, str] = {
    "Bash": "Bash",
    "Edit": "Edit|Write", "Write": "Edit|Write",
    "Read": "Read|Grep|Glob", "Grep": "Read|Grep|Glob", "Glob": "Read|Grep|Glob",
}

# ─── State persistence path ──

def _default_state_path() -> str:
    """Find entity state path relative to project root."""
    # Walk up from this file to find project root
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / ".git").exists() or (current / "config.json").exists():
            return str(current / "vape" / "entity" / "state" / "current.json")
        current = current.parent
    return str(Path(__file__).resolve().parents[3] / "vape" / "entity" / "state" / "current.json")

ENTITY_STATE_PATH = os.getenv("ENTITY_STATE_PATH", _default_state_path())


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
        # Session tracking for persistence
        self._session_id: str | None = None

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

        result = {
            "states": dict(self.states),
            "feelings": feelings,
            "expressionsTriggered": triggered,
        }

        # Auto-save state after every adjustment
        self.save_state()

        return result

    # ─── Hook event mapping ────────────────────────────────────

    def get_hook_adjustments(self, event_name: str, tool_name: str | None = None) -> list[tuple[str, float]]:
        """Look up state adjustments for a hook event."""
        if event_name == "PreToolUse" and tool_name:
            category = TOOL_CATEGORIES.get(tool_name)
            if category:
                return list(HOOK_ADJUSTMENTS.get(f"PreToolUse:{category}", []))
            return []
        return list(HOOK_ADJUSTMENTS.get(event_name, []))

    def scale_adjustments(
        self, adjustments: list[tuple[str, float]], intensity: int,
    ) -> list[tuple[str, float]]:
        """Scale adjustment deltas based on sentiment intensity."""
        if intensity < 30:
            factor = 0.5
        elif intensity > 70:
            factor = 1.5
        else:
            factor = 1.0
        return [(state, delta * factor) for state, delta in adjustments]

    def apply_sentiment(self, feeling: str, intensity: int) -> dict[str, Any]:
        """Look up sentiment adjustments, scale by intensity, apply to state."""
        base = list(SENTIMENT_ADJUSTMENTS.get(feeling, []))
        scaled = self.scale_adjustments(base, intensity)
        return self.adjust(scaled)

    # ─── State persistence ─────────────────────────────────────

    def save_state(self, filepath: str | None = None) -> None:
        """Auto-save current states + feelings to JSON file."""
        path = os.path.normpath(filepath or ENTITY_STATE_PATH)
        data = {
            "states": dict(self.states),
            "feelings": self._recalculate_feelings(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sessionId": self._session_id,
        }
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
        except OSError:
            pass  # Non-fatal — don't crash server if file write fails

    def load_state(self, filepath: str | None = None) -> dict | None:
        """Load saved state from JSON file. Returns parsed data or None."""
        path = os.path.normpath(filepath or ENTITY_STATE_PATH)
        if not os.path.exists(path):
            return None
        try:
            with open(path) as f:
                data = json.load(f)
            for name in STATE_NAMES:
                if name in data.get("states", {}):
                    self.states[name] = _clamp(data["states"][name])
            self._session_id = data.get("sessionId")
            return data
        except (OSError, json.JSONDecodeError):
            return None

    def apply_decay(self, hours_inactive: float) -> None:
        """Decay all states toward baseline based on hours of inactivity."""
        if hours_inactive <= 0:
            return
        decay_factor = 0.5 ** hours_inactive
        for name in STATE_NAMES:
            current = self.states[name]
            decayed = STATE_BASELINE + (current - STATE_BASELINE) * decay_factor
            self.states[name] = _clamp(decayed)

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
