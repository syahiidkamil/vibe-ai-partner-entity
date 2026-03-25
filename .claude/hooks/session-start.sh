#!/bin/bash
# Handle session start — notify server, load state, trigger wave.
# Fires on: SessionStart (matcher: startup)

SERVER_URL="${TTS_SERVER_URL:-http://localhost:5111}"

# Read hook payload from stdin
PAYLOAD=$(cat)

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
    echo '{"continue": true, "systemMessage": "Avatar server not running. Start with: npm start"}'
    exit 0
fi

# POST session start to server
curl -s -m 5 -X POST "$SERVER_URL/api/hook" \
    -H "Content-Type: application/json" \
    -d "$ENRICHED" > /dev/null 2>&1

echo '{"continue": true}'
