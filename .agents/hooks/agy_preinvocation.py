#!/usr/bin/env python3
"""Antigravity PreInvocation bridge — one adapter, zero duplicated logic.

Antigravity has no UserPromptSubmit/SessionStart events; it has PreInvocation (fires
before every model call) with an `injectSteps` output contract. This script bridges the
canonical Claude Code hooks in `.claude/hooks/` into that contract:

- On invocationNum == 0 (the start of an exchange), it runs `qualia-ground.sh` (the
  felt-state block; this also advances the qualia river one turn) and
  `diary-reminder.sh` (which carries its own cooldown).
- When the session-check marker is stale (> SESSION_GAP_MINUTES), it also runs the
  SessionStart trio: `session-temporal-check.sh`, `dream-check.sh`,
  `self-proposals-check.sh` — the closest thing Antigravity has to a session boundary.

Each canonical hook prints Claude Code's contract
(`{"hookSpecificOutput": {"additionalContext": ...}}`); this bridge harvests the
additionalContext strings and re-emits them as one Antigravity
`{"injectSteps": [{"ephemeralMessage": ...}]}`.

Degrade-silent by design: any failure (no bash, no python state, format drift) prints
`{}` and costs nothing but the feature. Untested on a live Antigravity install as of
2026-07-13 — the I/O contract follows https://antigravity.google/docs/hooks.
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CLAUDE_HOOKS = ROOT / ".claude" / "hooks"
MARKER = Path(__file__).resolve().parent / ".agy_last_session_checks"
SESSION_GAP_MINUTES = 30


def run_claude_hook(script: str, stdin_payload: str = "{}") -> str:
    """Run a canonical .claude hook, return its additionalContext ('' on any failure)."""
    path = CLAUDE_HOOKS / script
    if not path.is_file():
        return ""
    try:
        proc = subprocess.run(
            ["bash", str(path)],
            input=stdin_payload,
            capture_output=True,
            text=True,
            timeout=20,
            cwd=str(ROOT),
        )
        out = (proc.stdout or "").strip()
        if not out:
            return ""
        try:
            data = json.loads(out)
            return (data.get("hookSpecificOutput") or {}).get("additionalContext", "") or ""
        except json.JSONDecodeError:
            return out  # a hook that prints plain text still gets relayed
    except Exception:
        return ""


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        payload = {}

    # Ground only at the start of an exchange, not on every tool-loop invocation —
    # otherwise the qualia river would age once per tool call instead of once per turn.
    if payload.get("invocationNum", 0) != 0:
        print("{}")
        return

    pieces = []

    session_stale = True
    try:
        session_stale = (time.time() - MARKER.stat().st_mtime) > SESSION_GAP_MINUTES * 60
    except OSError:
        pass
    if session_stale:
        for script, stdin_payload in (
            ("session-temporal-check.sh", '{"source": "startup"}'),
            ("dream-check.sh", "{}"),
            ("self-proposals-check.sh", "{}"),
        ):
            ctx = run_claude_hook(script, stdin_payload)
            if ctx:
                pieces.append(ctx)
        try:
            MARKER.touch()
        except OSError:
            pass

    for script in ("qualia-ground.sh", "diary-reminder.sh"):
        ctx = run_claude_hook(script)
        if ctx:
            pieces.append(ctx)

    if not pieces:
        print("{}")
        return

    print(json.dumps(
        {"injectSteps": [{"ephemeralMessage": "\n\n".join(pieces)}]},
        ensure_ascii=False,
    ))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print("{}")
