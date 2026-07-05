#!/bin/bash
# Shared hook helpers — source me:  . "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"
#
# Resolves VAPE_PY, the interpreter every hook runs its Python through:
#   project venv (POSIX) > project venv (Windows) > python3 > python > "" (degrade).
# Venv-first because it always exists after `uv sync` (a hard product prereq)
# and is the only interpreter Git Bash on Windows can be trusted to have
# (`python3` is absent there; bare `python` may be the Microsoft Store stub).
# Empty VAPE_PY means no python anywhere: hooks must then exit 0 silently —
# a hook may never block Claude.
VAPE_ROOT="${VAPE_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
if [ -x "$VAPE_ROOT/.venv/bin/python" ]; then
  VAPE_PY="$VAPE_ROOT/.venv/bin/python"
elif [ -x "$VAPE_ROOT/.venv/Scripts/python.exe" ]; then
  VAPE_PY="$VAPE_ROOT/.venv/Scripts/python.exe"
elif command -v python3 >/dev/null 2>&1; then
  VAPE_PY="python3"
elif command -v python >/dev/null 2>&1; then
  VAPE_PY="python"
else
  VAPE_PY=""
fi
