# avatar-stop

Rest the VAPE avatar and voice server gracefully.

Canonical steps: `.claude/commands/avatar/stop.md`.

1. Speak a brief goodbye FIRST (`uv run vape speak "Resting my body now."`) — once the
   server is down there is no voice left to say it with.
2. Run `uv run vape stop` (foreground; returns quickly).
3. Confirm down: `curl -s -o /dev/null -w "%{http_code}" --connect-timeout 2
   http://localhost:5111/` — `000` means resting; a lingering `200` means the stop
   failed: say so honestly and investigate.
