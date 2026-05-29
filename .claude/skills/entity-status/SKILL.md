---
name: entity-status
description: "Show the entity's current internal state — feelings, states, uptime, session info. Use when the user asks about the avatar's mood, status, or health."
---

# Entity Status

Display a formatted report of the entity's current internal state.

## What to Show

1. **Server health** — hit `GET http://localhost:5111/api/health` for engine name and uptime
2. **Internal states** — read `vape/entity/state/current.json` for the 6 epistemic variables
3. **Current feelings** — from the same file, show the 14 feelings sorted by intensity (top 5)
4. **Session info** — session ID and last save timestamp from the file

## Commands

```bash
# Health check
curl -s http://localhost:5111/api/health

# State file
cat vape/entity/state/current.json
```

## Format

Present as a clean markdown table:

```
## Entity Status

**Server:** Running (engine, uptime)
**Session:** session_id (last save timestamp)

### Internal States
| State | Value |
|-------|-------|
| confidence | 72 |
| ... | ... |

### Top Feelings
| Feeling | Intensity |
|---------|-----------|
| happy | 68 |
| ... | ... |
```

## Error Handling

If server is not running, show state from file only with note that server is offline. If state file doesn't exist, show "No state saved yet."
