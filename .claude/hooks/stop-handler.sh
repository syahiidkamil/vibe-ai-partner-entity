#!/bin/bash
# Handle Stop event — relay response for sentiment analysis.
# Fires on: Stop

SERVER_URL="${TTS_SERVER_URL:-http://localhost:5111}"

# Read hook payload from stdin
PAYLOAD=$(cat)

ENRICHED=$(echo "$PAYLOAD" | python3 -c "
import sys, json
data = json.load(sys.stdin)
data['hook_event_name'] = 'Stop'
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
