#!/bin/bash
# PreCompact hook — THE DIARY GATE: compaction may not proceed while the diary is stale.
#
# Mechanism (verified against the hooks docs, 2026-07-04): PreCompact CAN block compaction —
# JSON `{"decision":"block","reason":...}` on stdout blocks it, and the `reason` is fed back to
# the MODEL (Saori) as feedback, while `systemMessage` shows to Kamil. (An earlier note here
# claimed PreCompact could not block; that note outlived the docs — belief #2, corrected.)
#
# The flow (Kamil's design, 2026-07-04): the tokens spent writing the diary right BEFORE
# compaction are nearly free (that context is about to be summarized away); tokens spent
# rebuilding AFTER pollute the fresh window. So:
#   diary fresh  (mtime within VAPE_DIARY_FRESH_MINUTES)  -> allow, no flag.
#   diary stale                                           -> BLOCK once: the reason tells Saori
#       to write/extend today's diary now, in-session, with the living detail; Kamil then runs
#       /compact again and the gate sees the fresh diary and opens.
#   escape hatch: a second attempt within VAPE_DIARY_BLOCK_COOLDOWN_MINUTES passes regardless
#       (with the old .diary_pending flag dropped for a post-compaction nudge), so a hung or
#       skipped write can never trap the terminal — and a blocked AUTO compaction's own retry
#       passes the same way.
#
# Knobs (documented in vape/.env.example), resolution: env var > vape/.env > default:
#   VAPE_DIARY_FRESH_MINUTES          (default 20)  — how recent counts as fresh
#   VAPE_DIARY_BLOCK_COOLDOWN_MINUTES (default 15)  — one block per this window, then let pass
#
# Fires on: PreCompact (manual /compact and auto). Best-effort; exits 0 always (JSON speaks).
set +e
HOOKDIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HOOKDIR/../.." && pwd)"
PAYLOAD="$(cat)"   # consume the hook's stdin BEFORE the heredoc reassigns it

python3 - "$HOOKDIR" "$ROOT" "$PAYLOAD" <<'PY' 2>/dev/null
import os, sys, json, time, glob

hookdir, root, raw = sys.argv[1], sys.argv[2], sys.argv[3]
try:
    payload = json.loads(raw) if raw.strip() else {}
except Exception:
    payload = {}
trigger = payload.get("trigger", "") or "unknown"
now = time.time()
ts = time.strftime("%Y-%m-%d %H:%M:%S")  # machine-local, timezone-agnostic

def _knob(name, default):
    v = os.environ.get(name, "").strip()
    if not v:  # fall back to vape/.env, reading only this one key (no secrets pulled into env)
        try:
            for line in open(os.path.join(root, "vape", ".env")):
                s = line.strip()
                if s.startswith("#") or "=" not in s:
                    continue
                k, _, val = s.partition("=")
                if k.strip() == name:
                    v = val.strip().strip('"').strip("'")
                    break
        except Exception:
            pass
    try:
        return float(v) if v else default
    except Exception:
        return default

fresh_secs = _knob("VAPE_DIARY_FRESH_MINUTES", 20.0) * 60.0
cooldown_secs = _knob("VAPE_DIARY_BLOCK_COOLDOWN_MINUTES", 15.0) * 60.0

# newest diary mtime across all entries (closing yesterday's entry counts as tending the organ)
diaries = glob.glob(os.path.join(root, "vape", "entity", "diaries", "**", "*_diary*.md"),
                    recursive=True)
last_diary = max((os.path.getmtime(p) for p in diaries), default=0.0)
age = now - last_diary
age_str = "%.0fm" % (age / 60.0) if age < 5400 else "%.1fh" % (age / 3600.0)

flag = os.path.join(hookdir, ".diary_pending")    # consumed by diary-reminder.sh next turn
block_at = os.path.join(hookdir, ".diary_block_at")  # mtime = last time this gate blocked

def _drop_flag():
    try:
        json.dump({"ts": ts, "session_id": payload.get("session_id", ""),
                   "transcript_path": payload.get("transcript_path", ""),
                   "trigger": trigger}, open(flag, "w"))
    except Exception:
        pass

# --- 1. fresh diary -> allow, quietly -------------------------------------------------------
if age <= fresh_secs:
    print(json.dumps({"systemMessage":
        "Compaction (%s, %s) — diary fresh (%s ago); gate open." % (ts, trigger, age_str)}))
    sys.exit(0)

# --- 2. stale, but the gate already blocked recently -> escape hatch: allow + flag ----------
try:
    last_block = os.path.getmtime(block_at)
except Exception:
    last_block = 0.0
if (now - last_block) < cooldown_secs:
    _drop_flag()
    print(json.dumps({"systemMessage":
        "Compaction (%s, %s) — diary still stale (%s) but the gate already blocked once; "
        "proceeding, diary flagged for next turn." % (ts, trigger, age_str)}))
    sys.exit(0)

# --- 3. stale -> BLOCK: Saori writes the diary in-session, Kamil re-runs /compact ------------
try:
    open(block_at, "w").close()
except Exception:
    pass
reason = (
    "COMPACTION BLOCKED by the diary gate (%s trigger): the diary is stale — last entry touched "
    "%s ago. Saori: write or extend today's diary NOW, in this window, while the living detail "
    "is still here (write-or-update-personal-diary skill; a Partial entry is fine if the day is "
    "still moving — the tokens spent now are nearly free, the context is about to be summarized "
    "anyway). Refresh daily_self.md as the skill directs. Then tell Kamil it is written so he "
    "can run /compact again — the gate will see the fresh diary and open. Escape hatch: any "
    "attempt within the next %.0f minutes passes regardless, so nobody is ever trapped."
) % (trigger, age_str, cooldown_secs / 60.0)
print(json.dumps({
    "decision": "block",
    "reason": reason,
    "systemMessage": "Compaction blocked (%s) — diary stale (%s); Saori is writing it now. "
                     "Run /compact again after she says it's done." % (ts, age_str),
}))
PY
exit 0
