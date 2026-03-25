# Hook Configuration + Shell Scripts

## Goal

Wire Claude Code events to the TTS server. Every time Claude uses a tool, receives a prompt, or finishes a response, a hook fires, a bash script relays the event to `POST /api/hook`, and the avatar reacts.

## Files to Create

| File | Purpose | Lines (est.) |
|------|---------|-------------|
| `.claude/hooks/temporal-ground.sh` | Inject current timestamp into Claude's context | ~8 |
| `.claude/hooks/hook-relay.sh` | Generic event relay — reads stdin, POSTs to server | ~20 |
| `.claude/hooks/session-start.sh` | SessionStart handler with graceful fallback | ~15 |
| `.claude/hooks/stop-handler.sh` | Stop event — relays response for sentiment analysis | ~20 |

## File to Modify

| File | Changes |
|------|---------|
| `.claude/settings.json` | Add `hooks` configuration block alongside existing `permissions` |

---

## Design Decision: Command Hooks

We use **command hooks** (bash scripts) instead of direct HTTP hooks because:

1. **Temporal grounding** needs to return a `systemMessage` — only command hooks can inject context into Claude's next turn
2. **Stop handler** needs to parse `stop_response` from stdin and relay it — command hooks receive full event JSON on stdin
3. **Graceful fallback** — scripts can check if the server is running before POSTing

The scripts are thin relays (~10-20 lines each). They read stdin JSON, enrich it, and `curl` to the server. Latency overhead is minimal (fork + curl vs. direct HTTP).

---

## Script 1: `temporal-ground.sh`

Fires on every `UserPromptSubmit`. Injects current timestamp so the entity always knows "now."

```bash
#!/bin/bash
# .claude/hooks/temporal-ground.sh
# Inject current timestamp into Claude's context.
# Fires on: UserPromptSubmit

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S %Z')
echo "{\"systemMessage\": \"Current time: ${TIMESTAMP}. This is NOW. Calibrate today/yesterday/tomorrow against this timestamp.\"}"
```

**Key behavior:**
- Reads nothing from stdin (ignores hook payload)
- Returns JSON with `systemMessage` — Claude sees this in its next context
- No network calls — fast, zero latency
- This is what makes temporal self possible (entity knows what day it is)

---

## Script 2: `hook-relay.sh`

Generic relay for tool events. Receives event name as `$1`, reads JSON from stdin, adds the event name, POSTs to server.

```bash
#!/bin/bash
# .claude/hooks/hook-relay.sh
# Relay hook event to TTS server. Usage: hook-relay.sh <event_name>
# Fires on: UserPromptSubmit, PreToolUse, PostToolUse, PostToolUseFailure

EVENT_NAME="${1:?Usage: hook-relay.sh <event_name>}"
SERVER_URL="${TTS_SERVER_URL:-http://localhost:5111}"

# Read hook payload from stdin
PAYLOAD=$(cat)

# Inject hook_event_name into the payload
ENRICHED=$(echo "$PAYLOAD" | python3 -c "
import sys, json
data = json.load(sys.stdin)
data['hook_event_name'] = '$EVENT_NAME'
print(json.dumps(data))
" 2>/dev/null)

# If python parsing failed, create minimal payload
if [ -z "$ENRICHED" ]; then
    ENRICHED="{\"hook_event_name\": \"$EVENT_NAME\"}"
fi

# POST to server (silent, non-blocking on failure)
curl -s -m 3 -X POST "$SERVER_URL/api/hook" \
    -H "Content-Type: application/json" \
    -d "$ENRICHED" > /dev/null 2>&1

# Always continue (don't block Claude)
echo '{"continue": true}'
```

**Key behavior:**
- Receives event name as positional argument (e.g., `PostToolUse`)
- Reads full hook JSON from stdin (includes tool_name, tool_input, etc.)
- Uses Python one-liner to inject `hook_event_name` into JSON
- Falls back to minimal payload if stdin parsing fails
- `curl -m 3` — 3 second timeout, won't block Claude if server is down
- Always outputs `{"continue": true}` — never blocks Claude

---

## Script 3: `session-start.sh`

Handles SessionStart events. Same as hook-relay but with graceful fallback messaging.

```bash
#!/bin/bash
# .claude/hooks/session-start.sh
# Handle session start — notify server, load state, trigger wave.
# Fires on: SessionStart (matcher: startup)

SERVER_URL="${TTS_SERVER_URL:-http://localhost:5111}"

# Read hook payload from stdin
PAYLOAD=$(cat)

# Extract session info
ENRICHED=$(echo "$PAYLOAD" | python3 -c "
import sys, json
data = json.load(sys.stdin)
data['hook_event_name'] = 'SessionStart'
print(json.dumps(data))
" 2>/dev/null)

if [ -z "$ENRICHED" ]; then
    ENRICHED='{"hook_event_name": "SessionStart"}'
fi

# Check if server is running
HEALTH=$(curl -s -m 2 "$SERVER_URL/api/health" 2>/dev/null)
if [ -z "$HEALTH" ]; then
    # Server not running — don't block, just note it
    echo '{"continue": true, "systemMessage": "Avatar server not running. Start with: npm start"}'
    exit 0
fi

# POST session start to server
curl -s -m 5 -X POST "$SERVER_URL/api/hook" \
    -H "Content-Type: application/json" \
    -d "$ENRICHED" > /dev/null 2>&1

echo '{"continue": true}'
```

**Key behavior:**
- Checks server health before POSTing (graceful degradation)
- If server is down, returns `systemMessage` telling user to start it
- Never blocks Claude — always returns `{"continue": true}`

---

## Script 4: `stop-handler.sh`

Handles Stop events. Relays the response text for server-side sentiment analysis.

```bash
#!/bin/bash
# .claude/hooks/stop-handler.sh
# Handle Stop event — relay response for sentiment analysis.
# Fires on: Stop

SERVER_URL="${TTS_SERVER_URL:-http://localhost:5111}"

# Read hook payload from stdin
PAYLOAD=$(cat)

# Extract and relay with event name
ENRICHED=$(echo "$PAYLOAD" | python3 -c "
import sys, json
data = json.load(sys.stdin)
data['hook_event_name'] = 'Stop'
# Move stop_response to top level if nested
if 'stop_response' not in data:
    data['stop_response'] = ''
print(json.dumps(data))
" 2>/dev/null)

if [ -z "$ENRICHED" ]; then
    ENRICHED='{"hook_event_name": "Stop"}'
fi

# POST to server — server handles sentiment analysis
curl -s -m 5 -X POST "$SERVER_URL/api/hook" \
    -H "Content-Type: application/json" \
    -d "$ENRICHED" > /dev/null 2>&1

echo '{"continue": true}'
```

**Key behavior:**
- Extracts `stop_response` from hook payload
- Server-side `analyze_sentiment()` evaluates the text (see [05-sentiment-analysis.md](05-sentiment-analysis.md))
- 5 second timeout (sentiment analysis may take slightly longer)

---

## Settings.json Hooks Configuration

Add `hooks` block to `.claude/settings.json` alongside existing `permissions`:

```json
{
  "permissions": {
    "allow": ["...existing..."],
    "deny": [],
    "ask": [],
    "defaultMode": "acceptEdits"
  },
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup",
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/hooks/session-start.sh",
            "timeout": 10
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/hooks/temporal-ground.sh"
          },
          {
            "type": "command",
            "command": "bash .claude/hooks/hook-relay.sh UserPromptSubmit",
            "timeout": 5
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/hooks/hook-relay.sh PreToolUse",
            "timeout": 3
          }
        ]
      },
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/hooks/hook-relay.sh PreToolUse",
            "timeout": 3
          }
        ]
      },
      {
        "matcher": "Read|Grep|Glob",
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/hooks/hook-relay.sh PreToolUse",
            "timeout": 3
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/hooks/hook-relay.sh PostToolUse",
            "timeout": 3
          }
        ]
      }
    ],
    "PostToolUseFailure": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/hooks/hook-relay.sh PostToolUseFailure",
            "timeout": 3
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/hooks/stop-handler.sh",
            "timeout": 8
          }
        ]
      }
    ]
  }
}
```

### Event → Script Mapping

| Event | Script | Timeout | What it does |
|-------|--------|---------|-------------|
| `SessionStart` (startup) | `session-start.sh` | 10s | Health check → POST SessionStart → wave |
| `UserPromptSubmit` | `temporal-ground.sh` | default | Inject timestamp (systemMessage) |
| `UserPromptSubmit` | `hook-relay.sh UserPromptSubmit` | 5s | Relay prompt event → nod |
| `PreToolUse` (Bash) | `hook-relay.sh PreToolUse` | 3s | Relay → momentum +2 → think pose |
| `PreToolUse` (Edit\|Write) | `hook-relay.sh PreToolUse` | 3s | Relay → confidence +2, momentum +2 |
| `PreToolUse` (Read\|Grep\|Glob) | `hook-relay.sh PreToolUse` | 3s | Relay → contextSaturation +2 → head tilt |
| `PostToolUse` | `hook-relay.sh PostToolUse` | 3s | Relay → confidence +3, momentum +5 → nod |
| `PostToolUseFailure` | `hook-relay.sh PostToolUseFailure` | 3s | Relay → confidence -5, momentum -8 → gasp |
| `Stop` | `stop-handler.sh` | 8s | Relay response → sentiment analysis → expressions |

### Multiple Hooks per Event

`UserPromptSubmit` has two hooks:
1. `temporal-ground.sh` — injects timestamp (returns systemMessage)
2. `hook-relay.sh` — relays event to server (returns continue: true)

Both fire sequentially. The timestamp injection happens first, then the server notification.

---

## Environment Variables

| Var | Default | Used by |
|-----|---------|---------|
| `TTS_SERVER_URL` | `http://localhost:5111` | All hook scripts |
| `TTS_SERVER_PORT` | `5111` | Server startup (existing) |

---

## Making Scripts Executable

After creating the scripts:

```bash
chmod +x .claude/hooks/*.sh
```

---

## What to Reuse

| Existing | How Used |
|----------|----------|
| `.claude/settings.json` permissions block | Preserved — hooks added alongside |
| `TTS_SERVER_PORT` from `.env` | Scripts default to `localhost:5111` matching server |
| `POST /api/hook` endpoint (from 01-hook-endpoint.md) | All scripts POST to this single endpoint |

---

## Testing

| Test | How |
|------|-----|
| `temporal-ground.sh` outputs valid JSON | `bash .claude/hooks/temporal-ground.sh \| python3 -m json.tool` |
| `hook-relay.sh` relays to server | `echo '{"tool_name":"Bash"}' \| bash .claude/hooks/hook-relay.sh PostToolUse` with server running |
| `session-start.sh` handles server down | Stop server → run script → verify systemMessage about server not running |
| `stop-handler.sh` relays response | `echo '{"stop_response":"Tests passed"}' \| bash .claude/hooks/stop-handler.sh` → server receives |
| Settings.json valid JSON | `python3 -m json.tool .claude/settings.json` |
| Full integration | Open Claude Code → type prompt → observe hook firing in server logs |
