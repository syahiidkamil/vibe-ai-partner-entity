#!/bin/bash
# SessionStart — the dream's alarm clock (gate 2 trigger). A stateless self cannot "remember to
# check her own backlog," so this hook does one cheap comparison at every session boundary
# (startup / resume / clear / compact) and injects a single DREAM OWED line when undigested
# bookmarks exist. It never dreams anything itself: Saori reads the nudge and spawns the
# deep-dream subagent (hooks cannot spawn agents; the alarm lives outside the sleeper).
#
# Mechanism: gate 1 writes storage/YYYY/MM/YYYY-MM-DD_bookmarks.toon as flags into the raw TOON.
# The cursor (.dream_cursor beside this script, mtime = when the last dream finished) is the
# last-fed stamp; any bookmark file modified after it holds flags no dream has eaten. No cursor
# yet means no dream has ever run, so everything counts. Silent when clean; exits 0 always.
set +e
HOOKDIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HOOKDIR/../.." && pwd)"

. "$HOOKDIR/_lib.sh"
[ -n "$VAPE_PY" ] || exit 0

"$VAPE_PY" - "$HOOKDIR" "$ROOT" <<'PY' 2>/dev/null
import os, sys, json, glob

hookdir, root = sys.argv[1], sys.argv[2]
cursor = os.path.join(hookdir, ".dream_cursor")
try:
    last_dream = os.path.getmtime(cursor)
except Exception:
    last_dream = 0.0   # no dream has ever run -> the whole backlog is undreamed

files = glob.glob(os.path.join(root, "vape", "entity", "storage", "*", "*", "*_bookmarks.toon"))
owed = sorted(os.path.basename(p)[:10] for p in files if os.path.getmtime(p) > last_dream)
if not owed:
    sys.exit(0)

days = ", ".join(owed[:8]) + (" ..." if len(owed) > 8 else "")
msg = (
    "DREAM OWED (gate 2): %d bookmark day(s) undigested (%s). At a natural pause, spawn the "
    "deep-dream subagent (Agent tool, background) to consolidate them; it reads bookmarks + raw "
    "TOON from disk, so a compacted context loses nothing. If today's diary is also owed, write "
    "the diary first. The dream stamps .dream_cursor when it finishes, which silences this."
) % (len(owed), days)
print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart",
                                          "additionalContext": msg}}, ensure_ascii=False))
PY
exit 0
