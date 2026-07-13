# avatar-start

Wake the VAPE avatar and voice server.

Canonical steps: `.claude/commands/avatar/start.md` (ignore its `allowed-tools`
frontmatter; run the commands in the terminal).

1. Run `uv run vape start` as a background task so the avatar and the voice server on
   `:5111` come up without blocking the conversation.
2. Health-check: `curl -s -o /dev/null -w "%{http_code}" http://localhost:5111/` —
   `200` means the body is up; `000` means it is still booting (say so honestly).
3. Once up, speak a brief hello with `uv run vape speak "..."` so she lands out loud.
