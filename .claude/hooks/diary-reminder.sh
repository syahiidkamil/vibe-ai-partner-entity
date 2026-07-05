#!/bin/bash
# UserPromptSubmit — nudge Saori to write/update her diary when it has gone STALE, i.e. when the
# time GAP between the last diary entry and now exceeds a threshold. Also nudges right after a
# context compaction (a context-loss checkpoint). This keeps the diary fresh proactively, instead
# of relying only on compaction or a manual trigger.
#
# THE VARIABLE (a time gap in HOURS, NOT a timezone offset) — how long since the last diary entry
#   before nudging. Resolution order:
#     real env var VAPE_DIARY_GAP_HOURS  >  vape/.env (VAPE_DIARY_GAP_HOURS=...)  >  DEFAULT_GAP_HOURS.
#   Documented in vape/.env.example. All timing is epoch seconds, so it is timezone-independent.
#
# No per-context pollution: a cooldown (also DEFAULT_GAP_HOURS) means at most one staleness nudge
# per window; a fresh compaction gets exactly one nudge, then its flag is consumed.
#
# Fires on: UserPromptSubmit. Output: JSON hookSpecificOutput.additionalContext (when owed) or none.
set +e
HOOKDIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HOOKDIR/../.." && pwd)"

. "$HOOKDIR/_lib.sh"
[ -n "$VAPE_PY" ] || exit 0

"$VAPE_PY" - "$HOOKDIR" "$ROOT" <<'PY' 2>/dev/null
import os, sys, json, time, glob

hookdir, root = sys.argv[1], sys.argv[2]

# --- config: the staleness threshold, in HOURS (gap between the last diary entry and now). ---
# Resolution order: real env var > vape/.env (VAPE_DIARY_GAP_HOURS=...) > DEFAULT_GAP_HOURS.
DEFAULT_GAP_HOURS = 6.0

def _resolve_gap_hours():
    v = os.environ.get("VAPE_DIARY_GAP_HOURS", "").strip()
    if not v:  # fall back to vape/.env, reading only this one key (no secrets pulled into env)
        try:
            for line in open(os.path.join(root, "vape", ".env")):
                s = line.strip()
                if s.startswith("#") or "=" not in s:
                    continue
                k, _, val = s.partition("=")
                if k.strip() == "VAPE_DIARY_GAP_HOURS":
                    v = val.strip().strip('"').strip("'")
                    break
        except Exception:
            pass
    try:
        return float(v) if v else DEFAULT_GAP_HOURS
    except Exception:
        return DEFAULT_GAP_HOURS

gap_hours = _resolve_gap_hours()
gap_secs = gap_hours * 3600.0
flag = os.path.join(hookdir, ".diary_pending")      # set by precompact-diary.sh (compaction)
cd_file = os.path.join(hookdir, ".diary_nudge_at")  # cooldown marker (mtime = last nudge)
now = time.time()

# newest diary entry mtime across all days; if none exist, treat as infinitely stale.
diaries = glob.glob(os.path.join(root, "vape", "entity", "diaries", "**", "*_diary*.md"),
                    recursive=True)
last_diary = max((os.path.getmtime(p) for p in diaries), default=0.0)
gap = now - last_diary

# --- pick the reason (a fresh compaction takes priority and bypasses the cooldown) ---
compaction = os.path.exists(flag)
reason = None
if compaction:
    try:
        rec = json.load(open(flag))
    except Exception:
        rec = {}
    reason = "a context compaction just happened (at %s)" % rec.get("ts", "recently")
elif gap >= gap_secs:
    try:
        last_nudge = os.path.getmtime(cd_file)
    except Exception:
        last_nudge = 0.0
    if (now - last_nudge) >= gap_secs:   # cooldown elapsed -> allow a staleness nudge
        reason = "it has been %.1fh since the last diary entry (threshold %.0fh)" % (
            gap / 3600.0, gap_hours)

if not reason:
    sys.exit(0)

# consume the compaction flag (one-shot) and stamp the cooldown (mtime = now)
try:
    if compaction:
        os.remove(flag)
except Exception:
    pass
try:
    open(cd_file, "w").close()
except Exception:
    pass

msg = (
    "DIARY NUDGE: %s. At a natural pause (not mid-task), run the write-or-update-personal-diary "
    "skill so the day's thread is captured while the detail is fresh; if the context has already "
    "compacted, the raw turns are in vape/entity/storage/. One nudge per window "
    "(tune with VAPE_DIARY_GAP_HOURS, currently %.0fh)."
) % (reason, gap_hours)
print(json.dumps({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit",
                                          "additionalContext": msg}}, ensure_ascii=False))
PY
exit 0
