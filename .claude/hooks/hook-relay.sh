#!/bin/bash
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

# POST to server (silent, 3s timeout, non-blocking on failure)
curl -s -m 3 -X POST "$SERVER_URL/api/hook" \
    -H "Content-Type: application/json" \
    -d "$ENRICHED" > /dev/null 2>&1

# Always continue (don't block Claude)
echo '{"continue": true}'
