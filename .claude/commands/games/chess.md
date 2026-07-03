---
description: Start the chess game — server on :5112, board in the browser, auto-wake watcher armed; then Kamil just moves on the board
disable-model-invocation: true
allowed-tools: Bash(curl:*), Bash(nohup:*), Bash(open:*), Bash(lsof:*)
---

# /games:chess — set the board

Bring the localhost chess game (`games/chess/`) fully alive: server, board, and the
auto-wake loop, so Kamil plays by clicking and Saori answers unprompted.

1. **Server.** Health-check `curl -s -o /dev/null -w "%{http_code}" http://localhost:5112/`.
   If not `200`, start it detached from the repo root —
   `nohup uv run python games/chess/server.py > <scratchpad>/chess-server.log 2>&1 & disown` —
   wait ~2s, re-check. (In-memory state dies with the server; finished games live on as PGN
   in `games/chess/matches/`.)

2. **Board.** Open it for Kamil: `open http://localhost:5112/`.

3. **Auto-wake watcher.** Check TaskList for an already-running chess monitor (one only —
   two watchers double-wake). If none, arm a **persistent Monitor** that polls
   `http://localhost:5112/state` once a second and emits a line only when: `to_move`
   becomes `Saori`, the game ends (`result != *`), or the server goes unreachable —
   deduplicated against the previous emission. Each event wakes Saori as a
   task-notification: Kamil moves silently on the board, Saori answers on her own.

4. **Report the position.** `GET /state` — if a game is mid-flight, give the move list and
   whose turn compactly (continue it; do not reset). Fresh board: say whose move it is.

5. **The standing rules of the game.** No engine — Saori plays her own reading, moves via
   `POST /move {"move": "e7e5"}` (UCI or SAN), and speaks each reply aloud. The monitor
   dies with the session; this command re-arms everything next time. The first finished
   real game births the memory bubble (`bubbles/play_games_alone/games/chess/` or the
   with-Kamil home it earns) — living before memory.
