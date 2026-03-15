#!/bin/bash
# Speak assistant response via Kokoro TTS daemon (Vibe Learning)
# Toggle: touch ~/.claude/voice-enabled (on) / rm ~/.claude/voice-enabled (off)

SOCKET="/tmp/vibe-kokoro.sock"

# Check toggle
[ -f "$HOME/.claude/voice-enabled" ] || exit 0

# Check daemon is running
[ -S "$SOCKET" ] || exit 0

# Read JSON payload from stdin
INPUT=$(cat)

# Prevent loops
if [ "$(echo "$INPUT" | jq -r '.stop_hook_active')" = "true" ]; then
  exit 0
fi

# Extract last assistant message
TEXT=$(echo "$INPUT" | jq -r '.last_assistant_message // empty' 2>/dev/null)
[ -z "$TEXT" ] && exit 0

# Strip markdown using perl (macOS compatible)
CLEAN=$(printf '%s' "$TEXT" | perl -0777 -pe '
  s/```.*?```//gs;
  s/^#{1,6}\s+//gm;
  s/\*\*([^*]*)\*\*/$1/g;
  s/\*([^*]*)\*/$1/g;
  s/`[^`]*`//g;
  s/\[([^\]]*)\]\([^\)]*\)/$1/g;
  s/^\s*[-*+]\s+//gm;
  s/^\s*\d+\.\s+//gm;
  s/\n/ /g;
  s/\s+/ /g;
  s/^\s+|\s+$//g;
')

[ -z "$CLEAN" ] && exit 0

# Send JSON to daemon (voice configurable via KOKORO_VOICE env var)
VOICE="${KOKORO_VOICE:-af_heart}"
PAYLOAD=$(jq -n --arg text "$CLEAN" --arg voice "$VOICE" '{text: $text, voice: $voice}')

(python3 -c "
import socket, sys
s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
s.connect('$SOCKET')
s.sendall(sys.stdin.buffer.read())
s.close()
" <<< "$PAYLOAD" 2>/dev/null) &

exit 0
