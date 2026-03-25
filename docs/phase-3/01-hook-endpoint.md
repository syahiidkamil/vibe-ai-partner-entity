# Hook Endpoint — `POST /api/hook`

## Goal

Add a single endpoint to the TTS server that receives all Claude Code hook events and translates them into state adjustments. This is the nervous system's brain — every hook event flows through here.

## Files to Modify

| File | Changes |
|------|---------|
| `apps/tts-server/src/vibe_tts/server.py` | Add `HookEvent` Pydantic model + `POST /api/hook` endpoint + vocal mode |
| `apps/tts-server/src/vibe_tts/state_manager.py` | Add `HOOK_ADJUSTMENTS`, `SENTIMENT_ADJUSTMENTS`, `scale_adjustments()`, `get_hook_adjustments()`, `apply_sentiment()` |

## HookEvent Pydantic Model

Add to `server.py` alongside existing request models:

```python
class HookEvent(BaseModel):
    """POST /api/hook — receives Claude Code hook events."""
    hook_event_name: str          # SessionStart, UserPromptSubmit, PreToolUse, PostToolUse, PostToolUseFailure, Stop
    session_id: str | None = None
    tool_name: str | None = None  # Bash, Edit, Write, Read, Grep, Glob, etc.
    tool_input: dict | None = None
    tool_output: str | None = None
    tool_error: str | None = None
    user_prompt: str | None = None
    stop_response: str | None = None
    session_trigger: str | None = None  # startup, resume, clear, compact
    # Pre-analyzed sentiment (from prompt hook or external analysis)
    sentiment: dict | None = None  # { feeling, intensity, action, speak }
```

These fields mirror Claude Code's hook input format documented in [hooks-integration.md](../claude_code/hooks-integration.md).

## Hook Event → State Adjustment Table

Add to `state_manager.py` as a module-level constant. These values are from [10-hooks-system.md](../architecture_after_review/10-hooks-system.md).

```python
HOOK_ADJUSTMENTS: dict[str, list[tuple[str, float]]] = {
    # Event name (or event:tool_category) → list of (state_name, delta)
    "SessionStart":             [("confidence", +10), ("contextSaturation", -20)],
    "UserPromptSubmit":         [("alignment", +3), ("contextSaturation", +5)],
    "PreToolUse:Bash":          [("momentum", +2)],
    "PreToolUse:Edit|Write":    [("confidence", +2), ("momentum", +2)],
    "PreToolUse:Read|Grep|Glob":[("contextSaturation", +2)],
    "PostToolUse":              [("confidence", +3), ("momentum", +5), ("contextSaturation", +3)],
    "PostToolUseFailure":       [("confidence", -5), ("momentum", -8), ("alignment", -2)],
}
```

### Tool Categorization

PreToolUse events need the tool name categorized:

| Tool Name | Category |
|-----------|----------|
| `Bash` | `Bash` |
| `Edit`, `Write` | `Edit\|Write` |
| `Read`, `Grep`, `Glob` | `Read\|Grep\|Glob` |
| Any other | Falls through to generic `PreToolUse` (no adjustments) |

Add a method to `StateManager`:

```python
TOOL_CATEGORIES = {
    "Bash": "Bash",
    "Edit": "Edit|Write", "Write": "Edit|Write",
    "Read": "Read|Grep|Glob", "Grep": "Read|Grep|Glob", "Glob": "Read|Grep|Glob",
}

def get_hook_adjustments(self, event_name: str, tool_name: str | None = None) -> list[tuple[str, float]]:
    """Look up state adjustments for a hook event."""
    if event_name == "PreToolUse" and tool_name:
        category = TOOL_CATEGORIES.get(tool_name)
        if category:
            key = f"PreToolUse:{category}"
            return HOOK_ADJUSTMENTS.get(key, [])
        return []  # Unknown tool, no adjustments
    return HOOK_ADJUSTMENTS.get(event_name, [])
```

## Sentiment → State Adjustment Table

When a Stop event carries sentiment (either pre-analyzed or from the heuristic), map the feeling to state adjustments. Values from [10-hooks-system.md](../architecture_after_review/10-hooks-system.md).

```python
SENTIMENT_ADJUSTMENTS: dict[str, list[tuple[str, float]]] = {
    "happy":      [("confidence", +5), ("momentum", +3), ("alignment", +3)],
    "proud":      [("confidence", +8), ("alignment", +5), ("momentum", +5)],
    "frustrated": [("momentum", -5)],
    "curious":    [("contextSaturation", -5), ("confidence", -2)],
    "anxious":    [("confidence", -5), ("alignment", -3)],
    "sad":        [("momentum", -5), ("alignment", -3), ("trustCalibration", -2)],
    "excited":    [("momentum", +8), ("contextSaturation", -3)],
    "calm":       [],  # No changes — equilibrium
    "bored":      [("contextSaturation", +5), ("momentum", -3)],
    "surprised":  [("contextSaturation", -10)],
    "guilty":     [("alignment", -8), ("confidence", -3)],
    "angry":      [("alignment", -5), ("momentum", -3)],
}
```

## Intensity Scaling

The `intensity` value (0-100) from sentiment scales the adjustments:

| Intensity Range | Scale Factor | Meaning |
|----------------|-------------|---------|
| 0-29 (low) | ×0.5 | Mild sentiment, halve deltas |
| 30-70 (moderate) | ×1.0 | Standard deltas |
| 71-100 (strong) | ×1.5 | Strong sentiment, amplify deltas |

```python
def scale_adjustments(
    self, adjustments: list[tuple[str, float]], intensity: int
) -> list[tuple[str, float]]:
    """Scale adjustment deltas based on sentiment intensity."""
    if intensity < 30:
        factor = 0.5
    elif intensity > 70:
        factor = 1.5
    else:
        factor = 1.0
    return [(state, delta * factor) for state, delta in adjustments]
```

## Apply Sentiment Method

Combines lookup + scaling + application:

```python
def apply_sentiment(self, feeling: str, intensity: int) -> dict:
    """Look up sentiment adjustments, scale by intensity, apply to state."""
    base = SENTIMENT_ADJUSTMENTS.get(feeling, [])
    scaled = self.scale_adjustments(base, intensity)
    return self.adjust(scaled)
```

## Endpoint Flow

The `POST /api/hook` handler in `server.py`:

```
1. Parse HookEvent from request body
2. Get hook adjustments: state_mgr.get_hook_adjustments(event_name, tool_name)
3. Apply adjustments: result = state_mgr.adjust(adjustments)
4. Broadcast triggered expressions via WebSocket
5. If event is "Stop":
   a. If sentiment dict present → state_mgr.apply_sentiment(feeling, intensity)
   b. Else if stop_response text → call analyze_sentiment() → apply_sentiment()
   c. If sentiment.action and action != "none" → broadcast action
   d. If sentiment.speak and vocal mode allows → trigger speak internally
6. Auto-save state: state_mgr.save_state()
7. Return {"continue": true, "states": ..., "feelings": ...}
```

### Vocal Mode

Read `ENTITY_VOCAL_MODE` from environment (default: `silent`):

| Mode | When sentiment.speak triggers TTS |
|------|----------------------------------|
| `silent` | Never — ignore speak field entirely |
| `reactive` | Only when `intensity > 80` |
| `conversational` | Any non-empty speak field |

Boss can always speak the entity manually via `/api/speak` regardless of vocal mode.

```python
import os

VOCAL_MODE = os.getenv("ENTITY_VOCAL_MODE", "silent")

def _should_speak(sentiment: dict) -> bool:
    speak_text = sentiment.get("speak", "")
    if not speak_text:
        return False
    if VOCAL_MODE == "silent":
        return False
    if VOCAL_MODE == "reactive":
        return sentiment.get("intensity", 0) > 80
    if VOCAL_MODE == "conversational":
        return True
    return False
```

## What to Reuse

| Existing Code | How Phase 3 Uses It |
|--------------|---------------------|
| `StateManager.adjust()` (`state_manager.py:75`) | Called by hook handler after mapping event → adjustments |
| `ConnectionManager.broadcast_status()` (`server.py:83`) | Broadcast triggered expressions + actions to avatar |
| `POST /api/state` handler (`server.py:218`) | Pattern to follow — same adjust → broadcast → return flow |
| `POST /api/speak` handler (`server.py:187`) | Called internally when vocal mode allows sentiment.speak |
| `StateManager._check_expressions()` (`state_manager.py:192`) | Already runs inside `adjust()` — expressions auto-trigger |

## Endpoint Example

```bash
# Tool use event
curl -s -X POST http://localhost:5111/api/hook \
  -H "Content-Type: application/json" \
  -d '{
    "hook_event_name": "PostToolUse",
    "tool_name": "Bash",
    "tool_input": {"command": "npm test"},
    "session_id": "abc123"
  }'

# Response
{
  "continue": true,
  "states": {"confidence": 53, "contextSaturation": 53, "momentum": 55, ...},
  "feelings": {"happy": 52, "curious": 44, ...},
  "expressionsTriggered": []
}
```

```bash
# Stop event with sentiment
curl -s -X POST http://localhost:5111/api/hook \
  -H "Content-Type: application/json" \
  -d '{
    "hook_event_name": "Stop",
    "session_id": "abc123",
    "sentiment": {"feeling": "proud", "intensity": 85, "action": "celebrate", "speak": ""}
  }'
```

## Tests

Add to `apps/tts-server/tests/`:

| Test | Verifies |
|------|----------|
| `test_get_hook_adjustments("PostToolUse", "Bash")` | Returns `[("confidence", +3), ("momentum", +5), ("contextSaturation", +3)]` |
| `test_get_hook_adjustments("PreToolUse", "Edit")` | Returns `[("confidence", +2), ("momentum", +2)]` |
| `test_get_hook_adjustments("PreToolUse", "Agent")` | Returns `[]` (unknown tool) |
| `test_scale_adjustments(intensity=20)` | All deltas × 0.5 |
| `test_scale_adjustments(intensity=50)` | All deltas × 1.0 |
| `test_scale_adjustments(intensity=85)` | All deltas × 1.5 |
| `test_apply_sentiment("proud", 85)` | confidence +12, alignment +7.5, momentum +7.5 |
| `test_apply_sentiment("calm", 50)` | No state changes |
| `test_hook_endpoint_post_tool_use` | HTTP POST returns states/feelings with correct deltas applied |
| `test_hook_endpoint_stop_with_sentiment` | Sentiment mapped to state changes + action broadcast |
| `test_vocal_mode_silent` | speak field ignored |
| `test_vocal_mode_reactive` | speak only when intensity > 80 |

## Architecture Reference

See [10-hooks-system.md](../architecture_after_review/10-hooks-system.md) for:
- Complete hook event → adjustState() tables
- Sentiment → adjustState() mapping
- Intensity scaling tiers
- Consciousness modulation (Phase 4+ — not implemented in Phase 3)
- Inner voice vs speech design rationale
