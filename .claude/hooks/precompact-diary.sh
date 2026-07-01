#!/bin/bash
# PreCompact hook — flag that a context compaction is happening, so the diary reminder treats a
# compaction as a checkpoint to write the diary before the in-context detail is summarized away.
#
# Mechanism note (verified against the hooks docs): a PreCompact hook CANNOT inject context into
# the model or make it act — it can only run a command, block compaction, or show the user a
# systemMessage. So this hook only DETECTS the compaction and drops a "diary owed" flag. Its
# companion `diary-reminder.sh` (a UserPromptSubmit hook) surfaces that flag ONCE next turn — and
# also nudges independently when the diary simply goes stale (a time gap since the last entry).
#
# It never blocks compaction (the raw turns are already persisted per-turn by capture.py); the
# displayed timestamp is plain machine-local time (timezone-agnostic). Best-effort; exits 0 always.
#
# Fires on: PreCompact (manual /compact and auto-compact). Reads the common payload on stdin.
set +e
FLAG="$(dirname "${BASH_SOURCE[0]}")/.diary_pending"
PAYLOAD="$(cat)"   # consume the hook's stdin BEFORE the heredoc reassigns it

python3 - "$FLAG" "$PAYLOAD" <<'PY' 2>/dev/null
import json, sys, time
flag, raw = sys.argv[1], sys.argv[2]
try:
    payload = json.loads(raw) if raw.strip() else {}
except Exception:
    payload = {}
rec = {
    "ts": time.strftime("%Y-%m-%d %H:%M:%S"),  # machine-local, timezone-agnostic
    "session_id": payload.get("session_id", ""),
    "transcript_path": payload.get("transcript_path", ""),
    "trigger": payload.get("trigger", ""),  # 'manual' | 'auto', when the harness provides it
}
try:
    with open(flag, "w") as f:
        json.dump(rec, f)
except Exception:
    pass
# PreCompact may show the USER a systemMessage (it cannot inject into the model). Keep it brief.
print(json.dumps({"systemMessage":
    "Compaction (%s) — diary flagged; Saori will update it next turn." % (rec["ts"])}))
PY
exit 0
