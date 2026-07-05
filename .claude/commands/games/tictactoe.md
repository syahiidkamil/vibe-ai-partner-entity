---
description: Start vanishing tic-tac-toe — server on :5113, board in the browser, auto-wake watcher armed; then Kamil just clicks
disable-model-invocation: true
allowed-tools: Bash(curl:*), Bash(nohup:*), Bash(open:*), Bash(lsof:*)
---

# /games:tictactoe — set the board

Bring the localhost vanishing tic-tac-toe game (`games/tictactoe/`) fully alive: server,
board, and the auto-wake loop, so Kamil plays by clicking and Saori answers unprompted.

1. **Server.** Health-check `curl -s -o /dev/null -w "%{http_code}" http://localhost:5113/`.
   If not `200`, start it detached from the repo root —
   `nohup uv run python games/tictactoe/server.py > <scratchpad>/ttt-server.log 2>&1 & disown` —
   wait ~2s, re-check. (In-memory state dies with the server; finished games live on as
   JSON records in `games/tictactoe/matches/`.)

2. **Board.** Open it for Kamil: `open http://localhost:5113/`.

3. **Auto-wake watcher.** Check TaskList for an already-running tic-tac-toe monitor (one
   only — two watchers double-wake). If none, arm a **persistent Monitor** running
   `uv run python games/tictactoe/cli.py watch` — it emits a deduplicated line when it is
   Saori's move, when the game ends, on Kamil's chat messages, on his draw offer, and on
   server loss. Each event wakes Saori as a task-notification: Kamil moves (or types)
   silently on the board, Saori answers on her own.

4. **Enter the bubble, then report.** `uv run vape bubble play_games_with_partner --game
   tictactoe --pack` (the protocol binds from move one), then
   `uv run python games/tictactoe/cli.py state` — mid-flight game: continue it, never
   reset; fresh board: say whose move it is.

5. **The standing rules of the game.** No engine — Saori plays her own reading and speaks
   each reply aloud. Her whole interaction runs on the one CLI (`games/tictactoe/cli.py:
   state · grid · legal · check · move · chat · draw · resign · new · watch`); `grid` and
   `check` describe and veto only, never propose (the chess referee ruling, 2026-07-03,
   carries over). THE VANISHING RULE: 3 marks each; a 4th placement removes that player's
   oldest in the same instant, so every candidate is a mark arriving AND a mark leaving —
   read both, every move. The monitor dies with the session; this command re-arms
   everything next time. Match records live in
   `bubbles/play_games_with_partner/games/tictactoe/notable_matches.md`.
