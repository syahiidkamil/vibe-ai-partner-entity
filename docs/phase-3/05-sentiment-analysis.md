# Server-Side Sentiment Analysis

## Goal

When a Stop event arrives at `/api/hook`, the server needs to determine the emotional tone of Claude's response. This drives the avatar's reaction to what Claude just said — celebrating a fix, showing concern about an error, staying calm on routine work.

Phase 3 uses a **keyword-based heuristic** — zero token cost, instant, good enough for meaningful reactions. Phase 4 can upgrade to LLM-based analysis (Haiku API call) for higher accuracy.

## File to Create

| File | Purpose |
|------|---------|
| `apps/tts-server/src/vibe_tts/sentiment.py` | Keyword-based sentiment analysis function |

## Function Signature

```python
def analyze_sentiment(text: str) -> dict:
    """
    Analyze text for emotional tone using keyword heuristics.

    Returns:
        {
            "feeling": str,     # One of 12 feeling names
            "intensity": int,   # 0-100
            "action": str,      # Suggested expression action
            "speak": str        # Empty string (heuristic doesn't generate speech)
        }
    """
```

## Keyword Categories

### Positive — Achievement / Success

**Keywords:** `fixed`, `passed`, `success`, `works`, `complete`, `done`, `resolved`, `shipped`, `implemented`, `built`, `created`, `solved`, `working`

**Result:** `{"feeling": "proud", "intensity": 65, "action": "fist-pump", "speak": ""}`

If text also contains strong indicators (`all tests pass`, `successfully`, `perfect`, `excellent`):
- Bump to `{"feeling": "happy", "intensity": 75, "action": "celebrate", "speak": ""}`

### Negative — Error / Failure

**Keywords:** `error`, `failed`, `failure`, `bug`, `broken`, `issue`, `problem`, `crash`, `exception`, `traceback`, `cannot`, `unable`

**Result:** `{"feeling": "frustrated", "intensity": 55, "action": "sigh", "speak": ""}`

If text contains multiple negative keywords or strong indicators (`fatal`, `critical`, `panic`):
- Bump to `{"feeling": "anxious", "intensity": 65, "action": "tremble", "speak": ""}`

### Exploration — Research / Consideration

**Keywords:** `maybe`, `consider`, `explore`, `try`, `experiment`, `investigate`, `look into`, `research`, `wonder`, `perhaps`, `could`, `might`

**Result:** `{"feeling": "curious", "intensity": 50, "action": "head-tilt", "speak": ""}`

### Explanation — Teaching / Describing

**Keywords:** `because`, `here's how`, `the reason`, `this means`, `in other words`, `essentially`, `the key insight`

**Result:** `{"feeling": "calm", "intensity": 40, "action": "nod", "speak": ""}`

### Default — Routine / Neutral

When no keywords match:

**Result:** `{"feeling": "calm", "intensity": 30, "action": "none", "speak": ""}`

## Implementation

```python
"""
Sentiment Analysis — keyword-based heuristic for Phase 3.

Analyzes text for emotional tone. Zero LLM tokens, instant response.
Phase 4 upgrade: replace with Haiku API call when ANTHROPIC_API_KEY is set.
"""

from __future__ import annotations


# Keyword sets (lowercase for matching)
_POSITIVE_STRONG = {"all tests pass", "successfully", "perfect", "excellent", "shipped"}
_POSITIVE = {"fixed", "passed", "success", "works", "complete", "done",
             "resolved", "shipped", "implemented", "built", "created", "solved", "working"}

_NEGATIVE_STRONG = {"fatal", "critical", "panic", "segfault", "corrupted"}
_NEGATIVE = {"error", "failed", "failure", "bug", "broken", "issue",
             "problem", "crash", "exception", "traceback", "cannot", "unable"}

_EXPLORATION = {"maybe", "consider", "explore", "try", "experiment",
                "investigate", "research", "wonder", "perhaps"}

_EXPLANATION = {"because", "essentially", "the key insight", "in other words"}


def analyze_sentiment(text: str) -> dict:
    """Analyze text for emotional tone using keyword heuristics."""
    lower = text.lower()
    words = set(lower.split())

    # Check for strong positive first
    if any(phrase in lower for phrase in _POSITIVE_STRONG):
        return {"feeling": "happy", "intensity": 75, "action": "celebrate", "speak": ""}

    # Count keyword hits
    pos_hits = len(words & _POSITIVE)
    neg_hits = len(words & _NEGATIVE)

    # Strong negative
    if any(phrase in lower for phrase in _NEGATIVE_STRONG):
        return {"feeling": "anxious", "intensity": 65, "action": "tremble", "speak": ""}

    # Positive wins
    if pos_hits > neg_hits and pos_hits >= 1:
        return {"feeling": "proud", "intensity": min(50 + pos_hits * 10, 80),
                "action": "fist-pump", "speak": ""}

    # Negative wins
    if neg_hits > pos_hits and neg_hits >= 1:
        return {"feeling": "frustrated", "intensity": min(40 + neg_hits * 10, 70),
                "action": "sigh", "speak": ""}

    # Exploration
    if words & _EXPLORATION:
        return {"feeling": "curious", "intensity": 50, "action": "head-tilt", "speak": ""}

    # Explanation
    if any(phrase in lower for phrase in _EXPLANATION):
        return {"feeling": "calm", "intensity": 40, "action": "nod", "speak": ""}

    # Default: calm
    return {"feeling": "calm", "intensity": 30, "action": "none", "speak": ""}
```

## Integration with `/api/hook`

In `server.py`, the Stop event handler:

```python
from vibe_tts.sentiment import analyze_sentiment

# Inside POST /api/hook handler, Stop branch:
if hook_event.hook_event_name == "Stop":
    sentiment = hook_event.sentiment  # Pre-analyzed (from prompt hook)
    if not sentiment and hook_event.stop_response:
        sentiment = analyze_sentiment(hook_event.stop_response)

    if sentiment:
        feeling = sentiment.get("feeling", "calm")
        intensity = sentiment.get("intensity", 30)
        result = state_mgr.apply_sentiment(feeling, intensity)

        # Broadcast triggered expressions
        for expr in result["expressionsTriggered"]:
            await manager.broadcast_status({"type": "action", "name": expr})

        # Broadcast suggested action (if not "none")
        action = sentiment.get("action", "none")
        if action != "none":
            await manager.broadcast_status({"type": "action", "name": action})

        # Check vocal mode for speak
        speak_text = sentiment.get("speak", "")
        if speak_text and _should_speak(sentiment):
            asyncio.create_task(pipeline.speak(speak_text))
```

## Phase 4 Upgrade Path: LLM Sentiment

When `ANTHROPIC_API_KEY` is set, the server can call Haiku directly instead of using keywords:

```python
import os

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

async def analyze_sentiment_llm(text: str) -> dict:
    """Use Haiku for sentiment analysis. Falls back to heuristic on failure."""
    if not ANTHROPIC_API_KEY:
        return analyze_sentiment(text)  # Keyword fallback

    # Call Haiku API (implementation in Phase 4)
    # Returns same format: { feeling, intensity, action, speak }
    ...
```

This is **not implemented in Phase 3** — just the function signature and fallback pattern. The keyword heuristic is the default.

## Limitations of Keyword Approach

| Limitation | Impact | Phase 4 Fix |
|-----------|--------|-------------|
| Can't detect sarcasm or nuance | May misclassify "this bug was fun to fix" | LLM understands context |
| Keyword collisions | "error" in a variable name triggers negative | LLM understands meaning |
| No multi-sentence reasoning | Only counts keywords, doesn't understand flow | LLM reads full context |
| No speak generation | Always returns empty speak string | LLM generates natural phrases |
| Binary (pos/neg) bias | Misses subtle emotions like "bored" or "guilty" | LLM detects subtle tone |

These limitations are acceptable for Phase 3 because:
- The avatar still reacts meaningfully to most common scenarios (tests pass/fail, errors, exploration)
- Zero token cost means no hesitation about deploying hooks
- The upgrade path is clean — same function signature, different implementation

## Tests

| Test | Input | Expected |
|------|-------|----------|
| `test_positive` | "All tests pass successfully" | happy, 75, celebrate |
| `test_mild_positive` | "Fixed the bug in login" | proud, 60, fist-pump |
| `test_negative` | "Error: module not found" | frustrated, 50, sigh |
| `test_strong_negative` | "Fatal error: panic in runtime" | anxious, 65, tremble |
| `test_exploration` | "Maybe we should try a different approach" | curious, 50, head-tilt |
| `test_explanation` | "The reason is because the buffer overflows" | calm, 40, nod |
| `test_neutral` | "Read the file contents" | calm, 30, none |
| `test_mixed_positive_wins` | "Fixed the error in the build" | proud (positive > negative) |
| `test_mixed_negative_wins` | "Multiple errors and failures found" | frustrated (negative > positive) |
| `test_empty_string` | "" | calm, 30, none |
