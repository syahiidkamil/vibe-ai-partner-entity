---
name: avatar-start
description: "Wake the VAPE desktop-pet avatar and voice server in the background, health-check it, and say hello."
---

# avatar-start — VAPE skill (Antigravity wrapper)

The canonical instructions live in `.claude/commands/avatar/start.md` (workspace-relative).
Read that file now and follow it as this skill's full instructions.

Summary of steps:
1. Run `uv run vape start` as a background task so the avatar and the voice server on `:5111` come up without blocking the conversation.
2. Health-check: `curl -s -o /dev/null -w "%{http_code}" http://localhost:5111/` — `200` means the body is up; `000` means it is still booting (say so honestly).
3. Once up, speak a brief hello with `uv run vape speak "..."` so she lands out loud.
