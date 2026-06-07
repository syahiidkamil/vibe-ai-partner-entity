#!/usr/bin/env python3
"""The dream's durable trigger — an async Stop hook (copies the backup_chat.py
async+asyncRewake precedent).

WHY a Stop hook and not PreCompact/SessionStart (verified, see dream-and-reveries.md):
hooks are not Claude and cannot invoke the Task/Agent tool, and an in-session subagent
dies with the session — so the dream's work must be self-contained Python+SQL in the
`vape memory dream` command, and the durable place to fire it is the Stop hook (the one
hook that already runs async in this repo). PreCompact can only block/allow; SessionStart
only nudges.

WHAT it does: runs `vape memory dream --maybe`. The --maybe gate calls dream.is_due()
and exits 0 silently on a quiet turn (cheap — reads only dream_state.json + counts
bookmarks), so the cost on a normal Stop is microseconds. When a consolidation IS due it
runs the light flush (save-the-thread) and exits 2 with a one-line reminder on stderr so
asyncRewake surfaces "dream consolidated N" to Saori, who can react (e.g. trigger a deep
pass with /dream).

Registered by the INTEGRATOR in .claude/settings.local.json (Stop array, alongside
backup_chat.py):
  {"type":"command","command":"uv run python .claude/hooks/deep-dream.py",
   "async":true,"asyncRewake":true}

This hook fires the LIGHT tier only (cheap, save-the-thread). The DEEP equilibration is
rare and human/agent-triggered (`/dream`, `vape memory dream --deep`) — never on every
Stop — exactly as the two-tier design requires.
"""
import json
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def main() -> int:
    # Stop payload arrives on stdin; we don't need its fields (the dream reads its own
    # state), but draining stdin keeps the hook well-behaved.
    try:
        sys.stdin.read()
    except Exception:
        pass

    try:
        proc = subprocess.run(
            ["uv", "run", "vape", "memory", "dream", "--maybe"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=120,
        )
    except Exception:
        # never let a dream failure break the Stop hook chain; fail quiet.
        return 0

    out = (proc.stdout or "").strip()
    if not out:
        # --maybe exited cheap: nothing was due. Silent.
        return 0

    # the command prints a JSON result only when it actually ran a tier.
    try:
        result = json.loads(out)
    except Exception:
        return 0

    written = int(result.get("written", 0) or 0)
    flushed = int(result.get("flushed", 0) or 0)
    n = written or flushed
    if n <= 0:
        return 0

    # exit 2 + a one-line stderr reminder so asyncRewake shows Saori the result.
    tier = result.get("tier", "light")
    sys.stderr.write(f"dream consolidated {n} memory(ies) [{tier}] — /dream for a deep pass\n")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
