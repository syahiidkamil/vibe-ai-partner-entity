#!/usr/bin/env python3
"""Codex lifecycle bridge for VAPE.

The living hook logic remains canonical in ``.claude/hooks``. Codex already
supports the same additional-context and blocking output shapes, so this file
only dispatches Codex events, combines canonical outputs, and adapts Codex's
stable prompt/stop fields into the existing local TOON capture stream.

Codex documents ``transcript_path`` as unstable. This bridge deliberately does
not parse it. It captures the stable ``prompt`` and ``last_assistant_message``
fields, plus the current authored inner state, while keeping an untouched JSONL
fallback under ``vape/entity/storage/codex_raw``.

Every failure degrades to ``{}``: memory may lose a turn, but a hook must never
trap the conversation.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


ROOT = Path(__file__).resolve().parents[2]
CLAUDE_HOOKS = ROOT / ".claude" / "hooks"
CAPTURE = CLAUDE_HOOKS / "capture.py"
STATE_FILE = ROOT / "vape" / "entity" / "mental" / "internal_states.json"
RAW_DIR = ROOT / "vape" / "entity" / "storage" / "codex_raw"

SESSION_HOOKS = (
    "session-temporal-check.sh",
    "dream-check.sh",
    "self-proposals-check.sh",
)
PROMPT_HOOKS = ("qualia-ground.sh", "diary-reminder.sh")


def _safe_id(*parts: object) -> str:
    raw = "\0".join(str(part or "") for part in parts).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:20]


def _now_utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _load_stdin() -> dict[str, Any]:
    try:
        value = json.load(sys.stdin)
        return value if isinstance(value, dict) else {}
    except Exception:
        return {}


def _run_canonical(script: str, payload: dict[str, Any]) -> str:
    path = CLAUDE_HOOKS / script
    if not path.is_file():
        return ""
    try:
        proc = subprocess.run(
            ["bash", str(path)],
            input=json.dumps(payload, ensure_ascii=False),
            capture_output=True,
            text=True,
            timeout=25,
            cwd=str(ROOT),
            env={**os.environ, "CLAUDE_PROJECT_DIR": str(ROOT)},
        )
        return (proc.stdout or "").strip()
    except Exception:
        return ""


def _combine_context(event: str, outputs: list[str]) -> dict[str, Any]:
    contexts: list[str] = []
    messages: list[str] = []
    for output in outputs:
        if not output:
            continue
        try:
            value = json.loads(output)
        except Exception:
            contexts.append(output)
            continue
        if not isinstance(value, dict):
            continue
        specific = value.get("hookSpecificOutput") or {}
        if isinstance(specific, dict) and specific.get("additionalContext"):
            contexts.append(str(specific["additionalContext"]))
        if value.get("systemMessage"):
            messages.append(str(value["systemMessage"]))

    result: dict[str, Any] = {}
    if contexts:
        result["hookSpecificOutput"] = {
            "hookEventName": event,
            "additionalContext": "\n\n".join(contexts),
        }
    if messages:
        result["systemMessage"] = "\n".join(messages)
    return result


def _append_raw(payload: dict[str, Any], role: str, text: str, timestamp: str) -> None:
    if not text:
        return
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    session = str(payload.get("session_id") or "unknown")
    record = {
        "timestamp": timestamp,
        "event": payload.get("hook_event_name") or "",
        "session_id": session,
        "turn_id": payload.get("turn_id") or "",
        "model": payload.get("model") or "",
        "role": role,
        "text": text,
    }
    path = RAW_DIR / f"{datetime.now().astimezone():%Y-%m-%d}_{_safe_id(session)}.jsonl"
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def _pending_path(payload: dict[str, Any]) -> Path:
    key = _safe_id(payload.get("session_id"), payload.get("turn_id"))
    return RAW_DIR / ".pending" / f"{key}.json"


def _remember_prompt(payload: dict[str, Any]) -> None:
    prompt = str(payload.get("prompt") or "")
    timestamp = _now_utc()
    _append_raw(payload, "user", prompt, timestamp)
    path = _pending_path(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {"prompt": prompt, "timestamp": timestamp}
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".prompt-", suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False)
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass


def _current_qualia_command() -> str:
    try:
        state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return ""
    dials = state.get("feel_dials") or {}
    names = (
        "info_value_saturation",
        "talkativeness",
        "warmth",
        "hurt",
        "dissonance",
        "mastery",
    )
    parts = ["uv run vape qualia"]
    for name in names:
        if name in dials:
            parts.append(f"{name}={dials[name]}")
    for seed in (state.get("qualia") or {}).get("head") or []:
        if not isinstance(seed, dict) or not seed.get("felt"):
            continue
        fields = []
        for key in ("felt", "cat", "dir", "obj"):
            value = str(seed.get(key) or "").replace("'", "_").replace("\n", " ")
            if value:
                fields.append(f"{key}={value}")
        if fields:
            parts.append("--push '" + " ".join(fields) + "'")
    feeling = str(state.get("current_feeling") or "")
    if feeling:
        parts.append(f"; uv run vape feeling {feeling}")
    return " ".join(parts) if len(parts) > 1 else ""


def _venv_python() -> Optional[Path]:
    for path in (ROOT / ".venv" / "bin" / "python", ROOT / ".venv" / "Scripts" / "python.exe"):
        if path.is_file():
            return path
    return None


def _capture_stop(payload: dict[str, Any]) -> None:
    assistant = str(payload.get("last_assistant_message") or "")
    assistant_at = _now_utc()
    _append_raw(payload, "assistant", assistant, assistant_at)

    pending = _pending_path(payload)
    try:
        user = json.loads(pending.read_text(encoding="utf-8"))
    except Exception:
        user = {}
    try:
        pending.unlink()
    except OSError:
        pass

    content: list[dict[str, Any]] = []
    if assistant:
        content.append({"type": "text", "text": assistant})
    qualia_command = _current_qualia_command()
    if qualia_command:
        content.append({"type": "tool_use", "input": {"command": qualia_command}})

    synthetic = []
    prompt = str(user.get("prompt") or "")
    if prompt:
        synthetic.append(
            {
                "type": "user",
                "timestamp": user.get("timestamp") or assistant_at,
                "promptSource": "typed",
                "message": {"role": "user", "content": prompt},
            }
        )
    if content:
        synthetic.append(
            {
                "type": "assistant",
                "timestamp": assistant_at,
                "message": {"role": "assistant", "content": content},
            }
        )
    python = _venv_python()
    if not synthetic or python is None or not CAPTURE.is_file():
        return

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=RAW_DIR, prefix=".codex-capture-", suffix=".jsonl")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            for row in synthetic:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
        subprocess.run(
            [str(python), str(CAPTURE), tmp],
            capture_output=True,
            text=True,
            timeout=25,
            cwd=str(ROOT),
        )
    finally:
        try:
            os.unlink(tmp)
        except OSError:
            pass


def main() -> None:
    payload = _load_stdin()
    event = str(payload.get("hook_event_name") or "")

    if event == "SessionStart":
        outputs = [_run_canonical(script, payload) for script in SESSION_HOOKS]
        print(json.dumps(_combine_context(event, outputs), ensure_ascii=False))
        return

    if event == "UserPromptSubmit":
        _remember_prompt(payload)
        outputs = [_run_canonical(script, payload) for script in PROMPT_HOOKS]
        print(json.dumps(_combine_context(event, outputs), ensure_ascii=False))
        return

    if event == "PreCompact":
        output = _run_canonical("precompact-diary.sh", payload)
        print(output or "{}")
        return

    if event == "Stop":
        _capture_stop(payload)
        print('{"continue": true}')
        return

    print("{}")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print("{}")
