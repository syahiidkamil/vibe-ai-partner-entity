#!/bin/bash
# Bubble injection hook (UserPromptSubmit). Sibling to qualia-ground.sh — same event,
# same JSON hookSpecificOutput.additionalContext form. It does three things, all cheap,
# and ONLY pays a cost while a bubble register is set:
#
#   1. DECLARE-read: read vape/entity/mental/active_bubble.json. If a bubble is active,
#      inject its memory_wiki/bubbles/<name>/HOT.md PROSE (no frontmatter, no numbers)
#      as a framed additionalContext block, and tick turns_active +1.
#   2. ADVISORY auto-suggest: if NO bubble is active, run a cheap keyword scan over the
#      prompt; on a strong match, inject a ONE-LINE suggestion ("the chess bubble is
#      available — vape bubble enter chess"). Advice, not an order. "I reach; I do not beg."
#   3. REVERIE: surface AT MOST ONE reverie on a strong match (with cooldown), if the
#      reverie machinery is present. Restraint is the design — timing, not recall.
#
# Registered into .claude/settings.local.json by the INTEGRATOR (NOT here).

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# The prompt text arrives as JSON on stdin (UserPromptSubmit payload). Pass it through
# to python so the advisory scan + reverie match can read it. Keep it on stdin to avoid
# any shell-quoting surprises with apostrophes/newlines in the prompt.
PAYLOAD="$(cat)"

cd "$ROOT" || exit 0

# Run the embedded python through the PROJECT venv interpreter so the engine package
# imports cleanly (config.py imports python-dotenv, which only lives in the venv — bare
# system python3 would ModuleNotFoundError and the hook would silently inject nothing).
# Prefer the in-repo .venv; fall back to `uv run python` (the backup_chat.py precedent);
# last resort, plain python3 so a missing venv degrades to a no-op rather than an error.
if [ -x "$ROOT/.venv/bin/python" ]; then
  PYBIN=("$ROOT/.venv/bin/python")
elif command -v uv >/dev/null 2>&1; then
  PYBIN=(uv run python)
else
  PYBIN=(python3)
fi

VAPE_ROOT="$ROOT/vape" PROMPT_PAYLOAD="$PAYLOAD" "${PYBIN[@]}" - <<'PY'
import json, os, sys

vape_root = os.environ.get("VAPE_ROOT", "")
# Put the package root (vape/) on the path so `engine.memory.bubble` imports cleanly,
# exactly like the installed `vape` console-script resolves it.
if vape_root and vape_root not in sys.path:
    sys.path.insert(0, vape_root)

# Read the prompt out of the UserPromptSubmit payload (best-effort; advisory only).
prompt = ""
try:
    payload = json.loads(os.environ.get("PROMPT_PAYLOAD") or "{}")
    if isinstance(payload, dict):
        prompt = payload.get("prompt") or ""
except Exception:
    prompt = ""

# Import the bubble module by path is unnecessary — it's a normal package import now.
try:
    from engine.memory import bubble as B
except Exception:
    # If the engine can't import for any reason, emit nothing and let the turn proceed.
    sys.exit(0)

blocks = []

# 1. Active bubble -> inject its pack, tick the turn counter.
try:
    reg = B.active()
except Exception:
    reg = None

if reg is not None:
    try:
        pack = B.inject_block()
    except Exception:
        pack = None
    if pack:
        blocks.append(pack)
    # Advance turns_active even if the pack was missing (the scope IS active).
    try:
        B.tick_turns()
    except Exception:
        pass
else:
    # 2. No bubble active -> advisory one-line suggestion on a strong keyword match.
    try:
        s = B.suggest(prompt)
    except Exception:
        s = None
    if s:
        blocks.append(
            "Bubble advisory (suggestion, not an order — you decide): " + s
        )

# 3. Reverie — surface AT MOST ONE, only if the reverie machinery exists (soul owner's
#    file). Reached via bubble re-export to keep the hook's imports on bubble-system;
#    until soul lands, this is a guarded no-op.
rev = None
try:
    match = getattr(B, "match_reverie", None)
    if callable(match):
        rev = match(prompt)
except Exception:
    rev = None

if rev:
    note = rev.get("note") if isinstance(rev, dict) else str(rev)
    if note:
        blocks.append("A reverie surfaces (let it color this moment, lightly): " + note)

if not blocks:
    # Nothing to inject this turn — exit silently, no additionalContext.
    sys.exit(0)

ctx = "\n\n".join(blocks)
print(json.dumps(
    {"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": ctx}},
    ensure_ascii=False,
))
PY
