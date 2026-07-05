---
description: Start the chess game — server on :5112, board in the browser, auto-wake watcher armed; then Kamil just moves on the board
disable-model-invocation: true
allowed-tools: Bash(curl:*), Bash(uv run:*)
---

# /games:chess — set the board

Bring the localhost chess game (`games/chess/`) fully alive: server, board, and the
auto-wake loop, so Kamil plays by clicking and Saori answers unprompted.

1. **Server.** Health-check `curl -s -o /dev/null -w "%{http_code}" http://localhost:5112/`.
   If not `200`, start `uv run python games/chess/server.py` with the Bash tool's
   `run_in_background: true` (portable detachment — no nohup), wait ~2s, re-check.
   (In-memory state dies with the server; finished games live on as PGN
   in `games/chess/matches/`.)

2. **Board.** Open it for Kamil: `uv run python -m webbrowser http://localhost:5112/`
   (cross-platform; macOS `open` is mac-only).

3. **Auto-wake watcher.** Check TaskList for an already-running chess monitor (one only —
   two watchers double-wake). If none, arm a **persistent Monitor** running
   `uv run python games/chess/cli.py watch` — it emits a deduplicated line when it is
   Saori's move, when the game ends, on Kamil's chat messages, on his draw offer, and on
   server loss. Each event wakes Saori as a task-notification: Kamil moves (or types)
   silently on the board, Saori answers on her own.

4. **Enter the bubble, then report.** `uv run vape bubble play_games_with_partner --game
   chess --pack` (the protocol binds from move one), then
   `uv run python games/chess/cli.py state` — mid-flight game: continue it, never reset;
   fresh board: say whose move it is.

5. **The standing rules of the game.** No engine — Saori plays her own reading and speaks
   each reply aloud. Her whole interaction runs on the one CLI
   (`games/chess/cli.py: state · grid · legal · check · move · chat · draw · resign`);
   `grid` and `check` describe and veto only, never propose (referee ruling 2026-07-03).
   The monitor dies with the session; this command re-arms everything next time. Match
   records live in `bubbles/play_games_with_partner/games/chess/notable_matches.md`.
