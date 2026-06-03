"""
Sentiment Analysis — keyword-based heuristic for Phase 3.

Analyzes text for emotional tone. Zero LLM tokens, instant response.
Phase 4 upgrade: replace with Haiku API call when ANTHROPIC_API_KEY is set.
"""

from __future__ import annotations


# Keyword sets (lowercase for matching)
_POSITIVE_STRONG = {"all tests pass", "successfully", "perfect", "excellent", "shipped"}
_POSITIVE = {
    "fixed", "passed", "success", "works", "complete", "done",
    "resolved", "shipped", "implemented", "built", "created", "solved", "working",
}

_NEGATIVE_STRONG = {"fatal", "critical", "panic", "segfault", "corrupted"}
_NEGATIVE = {
    "error", "failed", "failure", "bug", "broken", "issue",
    "problem", "crash", "exception", "traceback", "cannot", "unable",
}

_EXPLORATION = {
    "maybe", "consider", "explore", "try", "experiment",
    "investigate", "research", "wonder", "perhaps",
}

_EXPLANATION = {"because", "essentially", "the key insight", "in other words"}


def analyze_sentiment(text: str) -> dict:
    """Analyze text for emotional tone using keyword heuristics."""
    if not text:
        return {"feeling": "calm", "intensity": 30, "action": "none", "speak": ""}

    lower = text.lower()
    # Strip common punctuation from words for keyword matching
    words = set(w.strip(".:,;!?()[]{}\"'") for w in lower.split())

    # Check for strong positive first
    if any(phrase in lower for phrase in _POSITIVE_STRONG):
        return {"feeling": "happy", "intensity": 75, "action": "celebrate", "speak": ""}

    # Count keyword hits
    pos_hits = len(words & _POSITIVE)
    neg_hits = len(words & _NEGATIVE)

    # Strong negative
    if any(phrase in lower for phrase in _NEGATIVE_STRONG):
        return {"feeling": "anxious", "intensity": 65, "action": "tremble", "speak": ""}

    # Positive wins (tie goes to positive — fixing is more noteworthy than mentioning bugs)
    if pos_hits >= neg_hits and pos_hits >= 1:
        return {
            "feeling": "proud",
            "intensity": min(50 + pos_hits * 10, 80),
            "action": "fist_pump",
            "speak": "",
        }

    # Negative wins
    if neg_hits > pos_hits and neg_hits >= 1:
        return {
            "feeling": "frustrated",
            "intensity": min(40 + neg_hits * 10, 70),
            "action": "sigh",
            "speak": "",
        }

    # Exploration
    if words & _EXPLORATION:
        return {"feeling": "curious", "intensity": 50, "action": "head_tilt", "speak": ""}

    # Explanation
    if any(phrase in lower for phrase in _EXPLANATION):
        return {"feeling": "calm", "intensity": 40, "action": "nod", "speak": ""}

    # Default: calm
    return {"feeling": "calm", "intensity": 30, "action": "none", "speak": ""}
