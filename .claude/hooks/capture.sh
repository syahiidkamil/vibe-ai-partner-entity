#!/bin/bash
# Stop-hook wrapper: capture.py needs the PROJECT venv (imports toons +
# engine.cli), so only a venv interpreter qualifies — never system python.
# Registered instead of a raw `.venv/bin/python` path because Windows venvs
# put the interpreter at .venv/Scripts/python.exe. Silent no-op pre-setup;
# never blocks Claude.
. "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"
case "$VAPE_PY" in
  *"/.venv/"*) exec "$VAPE_PY" "$VAPE_ROOT/.claude/hooks/capture.py" ;;
esac
exit 0
