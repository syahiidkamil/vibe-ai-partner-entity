---
description: Check the whole VAPE install — prereqs, voice, avatar, memory — and guide the fixes
allowed-tools: Bash(uv run vape doctor), Bash(uv run vape memory doctor), Bash(uv run vape status), Bash(uv sync:*), Bash(uv run vape memory index), Bash(curl:*)
---

Run the whole-system health check and be the physician over the instrument:

```
uv run vape doctor
```

The CLI is the source of truth (every check is probed in code, never assumed); your job is the
guided interpretation a new user needs:

1. **Relay the verdict plainly first** — all clear, or exactly what failed.
2. **For each ✗ (failure):** explain what it means in one sentence and offer to run the named
   fix (the doctor prints the command beside every failure — `uv run vape setup`,
   `uv sync --extra <extra>`, etc.). Run fixes only with the user's yes.
3. **For each ! (warning):** say why it is advisory (e.g. the server simply is not running —
   `uv run vape start` — or a richer memory tier is available but not chosen).
4. **The one subtle check to spell out if it fails:** "server up but NO engine loaded" means
   the voice would return 200 while producing silence — the fix is re-running setup so the TTS
   engine's dependency group is installed again (a bare `uv sync` can prune optional engines).
5. If memory shows a lower tier than configured, `uv run vape memory doctor` gives the fuller
   ladder; `uv run vape memory index` heals staleness.

Exit code 0 = healthy (warnings allowed), 1 = something needs fixing. End by telling the user
their current state in one friendly line.
