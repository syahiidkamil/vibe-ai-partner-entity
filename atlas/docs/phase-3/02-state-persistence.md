# State Persistence + Decay

## Goal

The entity's internal states must survive across sessions. After every `adjustState()` call, auto-save to `entity/state/current.json`. On session resume, load the saved state and apply time-based decay toward baseline — the entity "cools down" between sessions, not resets to zero.

## File to Modify

| File | Changes |
|------|---------|
| `apps/tts-server/src/vibe_tts/state_manager.py` | Add `save_state()`, `load_state()`, `apply_decay()` methods |

## Save Format

`entity/state/current.json`:

```json
{
  "states": {
    "confidence": 72,
    "contextSaturation": 55,
    "alignment": 80,
    "memoryPressure": 30,
    "momentum": 65,
    "trustCalibration": 75
  },
  "feelings": {
    "happy": 68, "sad": 5, "frustrated": 12,
    "curious": 45, "proud": 52, "anxious": 8,
    "excited": 40, "calm": 55, "bored": 3,
    "guilty": 0, "angry": 0, "blushing": 10,
    "surprised": 0, "relieved": 0
  },
  "timestamp": "2026-03-25T14:32:00Z",
  "sessionId": "abc123"
}
```

## Save State Method

```python
import json
import os
from datetime import datetime, timezone

# Default path relative to project root
ENTITY_STATE_PATH = os.getenv(
    "ENTITY_STATE_PATH",
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "entity", "state", "current.json")
)

def save_state(self, filepath: str | None = None) -> None:
    """Auto-save current states + feelings to JSON file."""
    path = filepath or ENTITY_STATE_PATH
    data = {
        "states": dict(self.states),
        "feelings": self._recalculate_feelings(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "sessionId": self._session_id,
    }
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
```

**Integration point**: Call `self.save_state()` at the end of every `adjust()` call. This ensures state is always persisted.

```python
def adjust(self, adjustments: list[tuple[str, float]]) -> dict:
    # ... existing logic ...
    result = { "states": ..., "feelings": ..., "expressionsTriggered": ... }
    self.save_state()  # <-- add this line
    return result
```

## Load State Method

```python
def load_state(self, filepath: str | None = None) -> dict | None:
    """Load saved state from JSON file. Returns parsed data or None."""
    path = filepath or ENTITY_STATE_PATH
    if not os.path.exists(path):
        return None
    with open(path) as f:
        data = json.load(f)
    # Apply to internal state
    for name in STATE_NAMES:
        if name in data.get("states", {}):
            self.states[name] = _clamp(data["states"][name])
    self._session_id = data.get("sessionId")
    return data
```

## Decay Formula

From [08-memory-system.md](../architecture_after_review/08-memory-system.md):

```
decayed = baseline + (current - baseline) × 0.5^(hoursInactive)
```

| Hours Inactive | Decay of (85 - 50) = 35 | Result |
|---------------|-------------------------|--------|
| 0 | 35 × 1.0 = 35 | 85 |
| 1 | 35 × 0.5 = 17.5 | 67.5 |
| 2 | 35 × 0.25 = 8.75 | 58.75 |
| 4 | 35 × 0.0625 = 2.19 | 52.19 |
| 8+ | ≈ 0 | ≈ 50 (baseline) |

After ~4 hours, states are nearly back to baseline. This creates natural "morning reset" for overnight gaps while preserving momentum within a workday.

```python
def apply_decay(self, hours_inactive: float) -> None:
    """Decay all states toward baseline based on hours of inactivity."""
    if hours_inactive <= 0:
        return
    decay_factor = 0.5 ** hours_inactive
    for name in STATE_NAMES:
        current = self.states[name]
        decayed = STATE_BASELINE + (current - STATE_BASELINE) * decay_factor
        self.states[name] = _clamp(decayed)
```

## SessionStart Flow

When `/api/hook` receives a `SessionStart` event:

```
1. Load state from entity/state/current.json
   ↓
2. Parse timestamp → calculate hours since last save
   ↓
3. Apply decay: apply_decay(hours_inactive)
   ↓
4. Apply SessionStart adjustments: confidence +10, contextSaturation -20
   ↓
5. Save updated state
   ↓
6. Broadcast wave action to avatar via WebSocket
   ↓
7. Store session_id for subsequent saves
```

```python
# In the /api/hook handler, SessionStart branch:
saved = state_mgr.load_state()
if saved and saved.get("timestamp"):
    last_time = datetime.fromisoformat(saved["timestamp"])
    now = datetime.now(timezone.utc)
    hours = (now - last_time).total_seconds() / 3600
    state_mgr.apply_decay(hours)

state_mgr._session_id = hook_event.session_id
adjustments = state_mgr.get_hook_adjustments("SessionStart")
result = state_mgr.adjust(adjustments)
# adjust() now auto-saves via save_state()

# Broadcast wave
await manager.broadcast_status({"type": "action", "name": "wave"})
```

## Session ID Tracking

Add `_session_id` to `StateManager.__init__()`:

```python
def __init__(self) -> None:
    # ... existing fields ...
    self._session_id: str | None = None
```

Set from the first hook event of each session. Used in `save_state()` for the `sessionId` field in `current.json`.

## Environment Configuration

| Env Var | Default | Description |
|---------|---------|-------------|
| `ENTITY_STATE_PATH` | `entity/state/current.json` (relative to project root) | Path to state persistence file |

## What to Reuse

| Existing Code | How Used |
|--------------|----------|
| `STATE_BASELINE = 50` (`state_manager.py:32`) | Decay target for all states |
| `STATE_NAMES` list (`state_manager.py:21`) | Iterate all states for decay |
| `_clamp()` function (`state_manager.py:53`) | Clamp decayed values to 0-100 |
| `adjust()` method (`state_manager.py:75`) | Called after decay + SessionStart adjustments |
| `entity/state/current.json` template | Already exists from Phase 1 entity structure |

## Tests

| Test | Verifies |
|------|----------|
| `test_save_state_creates_file` | JSON file written with correct structure |
| `test_load_state_restores` | States restored from saved file |
| `test_load_state_missing_file` | Returns None, no crash |
| `test_decay_zero_hours` | No change to states |
| `test_decay_one_hour` | Each state moves 50% toward baseline |
| `test_decay_four_hours` | States nearly at baseline |
| `test_decay_baseline_unchanged` | State at 50 stays at 50 |
| `test_session_start_loads_and_decays` | Full flow: load → decay → adjust → save |
| `test_adjust_auto_saves` | Every `adjust()` call writes to file |
