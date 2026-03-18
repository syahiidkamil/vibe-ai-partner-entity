# Phase 2 Implementation: End-to-End Integration

## How Components Connect

```
                CLI (npm run speak/feeling/action)
                        |
                        | HTTP POST
                        v
              TTS Server (localhost:5111)
              +------------+-----------+
              | REST API   | WebSocket |
              | /api/speak | /ws/status|
              | /api/feeling| /ws/audio|
              | /api/action|           |
              | /api/state |           |
              | /api/health|           |
              +------------+-----------+
                        | WebSocket
                        v
              Avatar App (Tauri 2)
              +--------------------+
              | ws-client.ts       |
              | renderer-host.ts   |
              | Live2D renderer    |
              +--------------------+
```

### Data flow summary

1. **CLI or Hook** sends HTTP POST to TTS server
2. **TTS server** processes the command, broadcasts via WebSocket
3. **Avatar app** receives WebSocket messages, drives the renderer
4. For speech: TTS server generates audio chunks, streams amplitude + PCM via WebSocket

### Protocol types

All message types are already defined in `packages/shared/src/protocol.ts`:
- REST: `SpeakRequest`, `FeelingRequest`, `ActionRequest`, `StateAdjustRequest`, `HealthResponse`, `StateResponse`
- WebSocket: `WSStateUpdate`, `WSAmplitude`, `WSFeelingUpdate`, `WSActionUpdate`, `WSAudioChunk`, `WSExpressionFired`

---

## Startup Scripts

### `scripts/start.js`

Node.js script that orchestrates startup of both processes.

```
scripts/start.js
```

**What it does:**

1. Checks if TTS server is already running (`curl http://localhost:5111/api/health`)
2. If not running, starts TTS server: `python -m uvicorn vibe_tts.server:app --port 5111`
3. Polls `/api/health` until it responds OK (timeout: 30s, interval: 500ms)
4. Starts avatar app:
   - **Dev mode** (`--dev` flag): `npm run dev -w apps/avatar-app`
   - **Prod mode** (default): launch the built Tauri binary from `apps/avatar-app/src-tauri/target/release/`
5. Reports status to stdout

```js
// Pseudocode for scripts/start.js
import { spawn } from "child_process";
import { readFileSync } from "fs";

const TTS_PORT = process.env.TTS_SERVER_PORT || 5111;
const isDev = process.argv.includes("--dev");

async function checkHealth(port) {
  try {
    const res = await fetch(`http://localhost:${port}/api/health`);
    return res.ok;
  } catch { return false; }
}

async function waitForHealth(port, timeoutMs = 30000) {
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    if (await checkHealth(port)) return true;
    await new Promise(r => setTimeout(r, 500));
  }
  throw new Error(`TTS server did not start within ${timeoutMs}ms`);
}

async function main() {
  console.log("Starting Vibe AI Partner...");

  // 1. TTS Server
  if (await checkHealth(TTS_PORT)) {
    console.log(`  TTS Server already running on port ${TTS_PORT}`);
  } else {
    console.log("  Starting TTS server...");
    const tts = spawn("python", ["-m", "uvicorn", "vibe_tts.server:app", "--port", String(TTS_PORT)], {
      cwd: "apps/tts-server",
      stdio: "pipe",
      detached: true
    });
    tts.unref();
    // Write PID for stop script
    writeFileSync(".tts-server.pid", String(tts.pid));
    await waitForHealth(TTS_PORT);
    console.log(`  TTS Server running on http://localhost:${TTS_PORT}`);
  }

  // 2. Avatar App
  console.log("  Starting avatar app...");
  if (isDev) {
    spawn("npm", ["run", "dev", "-w", "apps/avatar-app"], { stdio: "inherit" });
  } else {
    // Launch built Tauri binary
    const binary = getBinaryPath(); // platform-specific path resolution
    const avatar = spawn(binary, [], { stdio: "pipe", detached: true });
    avatar.unref();
    writeFileSync(".avatar-app.pid", String(avatar.pid));
  }

  console.log("\n  Avatar is alive! Open Claude Code to begin.");
}
```

### `scripts/stop.js`

Kills both processes using stored PID files.

```js
// Pseudocode for scripts/stop.js
import { readFileSync, unlinkSync, existsSync } from "fs";

function killPid(pidFile, name) {
  if (!existsSync(pidFile)) {
    console.log(`  ${name}: not running (no PID file)`);
    return;
  }
  const pid = parseInt(readFileSync(pidFile, "utf8"));
  try {
    process.kill(pid, "SIGTERM");
    unlinkSync(pidFile);
    console.log(`  ${name}: stopped (PID ${pid})`);
  } catch {
    unlinkSync(pidFile);
    console.log(`  ${name}: already stopped`);
  }
}

killPid(".tts-server.pid", "TTS Server");
killPid(".avatar-app.pid", "Avatar App");
```

### `scripts/status.js`

Checks health of all components.

```js
// Pseudocode for scripts/status.js
const TTS_PORT = process.env.TTS_SERVER_PORT || 5111;

async function main() {
  console.log("Vibe AI Partner Status:\n");

  // TTS Server
  try {
    const res = await fetch(`http://localhost:${TTS_PORT}/api/health`);
    const data = await res.json();
    console.log(`  TTS Server:  OK (http://localhost:${TTS_PORT}, engine: ${data.engine})`);
  } catch {
    console.log("  TTS Server:  NOT RUNNING");
  }

  // Avatar App (check PID file)
  if (existsSync(".avatar-app.pid")) {
    const pid = parseInt(readFileSync(".avatar-app.pid", "utf8"));
    try {
      process.kill(pid, 0); // signal 0 = check if alive
      console.log(`  Avatar App:  OK (PID ${pid})`);
    } catch {
      console.log("  Avatar App:  NOT RUNNING (stale PID)");
    }
  } else {
    console.log("  Avatar App:  NOT RUNNING");
  }
}
```

---

## CLI Tool (`apps/cli/`)

Lightweight CLI for sending commands to the TTS server. Uses `commander.js` for argument parsing and native `fetch()` for HTTP.

### File structure

```
apps/cli/
├── package.json
├── tsconfig.json
└── src/
    ├── index.ts              # CLI entry point (commander.js)
    └── commands/
        ├── speak.ts          # POST /api/speak
        ├── feeling.ts        # POST /api/feeling
        └── action.ts         # POST /api/action
```

### `apps/cli/package.json`

```json
{
  "name": "@vibe/cli",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "main": "dist/index.js",
  "scripts": {
    "build": "tsc",
    "dev": "tsx src/index.ts"
  },
  "dependencies": {
    "commander": "^12.0.0"
  },
  "devDependencies": {
    "@vibe/shared": "workspace:*",
    "typescript": "^5.4.0",
    "tsx": "^4.0.0"
  }
}
```

### `apps/cli/src/index.ts`

```ts
import { Command } from "commander";
import { speak } from "./commands/speak.js";
import { feeling } from "./commands/feeling.js";
import { action } from "./commands/action.js";

const program = new Command();
const TTS_URL = `http://localhost:${process.env.TTS_SERVER_PORT || 5111}`;

program
  .name("vibe")
  .description("Vibe AI Partner CLI");

program
  .command("speak <text>")
  .description("Speak text with TTS and lip sync")
  .option("-v, --voice <voice>", "Voice name")
  .option("-s, --speed <speed>", "Playback speed", "1.0")
  .action((text, opts) => speak(TTS_URL, text, opts));

program
  .command("feeling <name>")
  .description("Set the avatar feeling (happy, sad, curious, etc.)")
  .action((name) => feeling(TTS_URL, name));

program
  .command("action <name>")
  .description("Trigger a self-expression (wave, nod, laugh, etc.)")
  .action((name) => action(TTS_URL, name));

program.parse();
```

### `apps/cli/src/commands/speak.ts`

```ts
export async function speak(
  baseUrl: string,
  text: string,
  opts: { voice?: string; speed?: string }
) {
  const res = await fetch(`${baseUrl}/api/speak`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      text,
      voice: opts.voice,
      speed: opts.speed ? parseFloat(opts.speed) : undefined,
    }),
  });

  if (!res.ok) {
    console.error(`Error: ${res.status} ${res.statusText}`);
    process.exit(1);
  }

  const data = await res.json();
  console.log(`Speaking: "${text}" (estimated ${data.duration_estimate}s)`);
}
```

### `apps/cli/src/commands/feeling.ts`

```ts
export async function feeling(baseUrl: string, name: string) {
  const res = await fetch(`${baseUrl}/api/feeling`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  });

  if (!res.ok) {
    console.error(`Error: ${res.status} ${res.statusText}`);
    process.exit(1);
  }

  console.log(`Feeling set: ${name}`);
}
```

### `apps/cli/src/commands/action.ts`

```ts
export async function action(baseUrl: string, name: string) {
  const res = await fetch(`${baseUrl}/api/action`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  });

  if (!res.ok) {
    console.error(`Error: ${res.status} ${res.statusText}`);
    process.exit(1);
  }

  console.log(`Action triggered: ${name}`);
}
```

---

## npm Scripts (Root package.json)

These scripts are the user-facing interface. They delegate to the scripts and CLI defined above.

```json
{
  "scripts": {
    "setup":      "node scripts/setup.js",
    "start":      "node scripts/start.js",
    "stop":       "node scripts/stop.js",
    "restart":    "npm stop && npm start",
    "status":     "node scripts/status.js",

    "dev":        "npm run dev -w apps/avatar-app",
    "build":      "npm run build -ws",
    "test":       "npm run test -ws",

    "tts:start":  "node scripts/tts-start.js",
    "tts:stop":   "node scripts/tts-stop.js",
    "tts:install": "node scripts/tts-install.js",

    "speak":      "node scripts/cli.js speak",
    "feeling":    "node scripts/cli.js feeling",
    "action":     "node scripts/cli.js action",

    "switch":     "node scripts/switch.js"
  }
}
```

### `scripts/cli.js` (Thin wrapper)

```js
// scripts/cli.js — forwards args to the CLI package
import { execSync } from "child_process";

const args = process.argv.slice(2).join(" ");
execSync(`node apps/cli/dist/index.js ${args}`, { stdio: "inherit" });
```

This wrapper lets users run `npm run feeling happy` from the project root without knowing about the `apps/cli/` package.

---

## End-to-End Test Flow

```bash
# 1. Start everything
npm start
# Expected output:
#   Starting Vibe AI Partner...
#     TTS Server running on http://localhost:5111
#     Starting avatar app...
#     Avatar is alive! Open Claude Code to begin.

# 2. Test health
npm run status
# Expected output:
#   Vibe AI Partner Status:
#     TTS Server:  OK (http://localhost:5111, engine: kittentts)
#     Avatar App:  OK (PID 12345)

# 3. Test feelings (all 14)
npm run feeling happy
# Expected: avatar shows happy expression (Happy.exp3.json applied)

npm run feeling curious
# Expected: avatar shows curious expression

npm run feeling sad
# Expected: avatar shows sad expression

# 4. Test self-expressions
npm run action wave
# Expected: avatar plays Waving.motion3.json

npm run action nod
# Expected: avatar plays Nodding.motion3.json

npm run action celebrate
# Expected: avatar plays Celebrating.motion3.json

# 5. Test speech with lip sync
npm run speak "Hello world"
# Expected: TTS generates audio, avatar lip syncs via PARAM_MOUTH_OPEN_Y,
#           amplitude streamed at ~30Hz via /ws/status

npm run speak "I am your AI partner" -- --voice Bella
# Expected: speaks with Bella voice

# 6. Test state adjustment (direct API)
curl -X POST http://localhost:5111/api/state \
  -H "Content-Type: application/json" \
  -d '{"adjustments": [{"state": "confidence", "delta": 20}]}'
# Expected: returns updated states, feelings, and any triggered expressions

# 7. Stop everything
npm stop
# Expected output:
#   TTS Server: stopped (PID 12340)
#   Avatar App: stopped (PID 12345)
```

---

## Troubleshooting

| Problem | Check | Fix |
|---------|-------|-----|
| Avatar window doesn't appear | `npm run status` | Restart: `npm stop && npm start` |
| TTS server not running | `curl localhost:5111/api/health` | `npm run tts:start` |
| No lip sync | Check WebSocket in browser devtools | Verify ws://localhost:5111/ws/status is sending amplitude messages |
| Model not loading | Check `AVATAR_MODEL` in `.env` | Ensure model files exist in `models/live2d/shizuku/` |
| Wrong model displayed | Check `AVATAR_RENDERER` in `.env` | Must match capabilities.json `renderer` field |
| Expression not working | Check capabilities.json | Ensure feeling has non-null mapping, file exists |
| Self-expression not playing | Check capabilities.json `selfExpressions` | Verify motion file exists at referenced path |
| Python not found | `python3 --version` | Install Python 3.10+ from python.org |
| Port already in use | `lsof -i :5111` | Kill the process or change `TTS_SERVER_PORT` in `.env` |
| WebSocket disconnects | Check avatar app console logs | TTS server may have crashed — check `npm run status` |
| Rust build fails | `rustc --version` | Install via `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs \| sh` |

---

## What Phase 2 Integration Does NOT Include

These are deferred to Phase 3+:

- **Claude Code hooks** — Automatic avatar reactions to Claude events (Phase 3)
- **Memory/PostgreSQL** — State persistence across sessions (Phase 3)
- **Entity context loading** — SOUL.md, identity, backstory injection (Phase 3)
- **Consciousness system** — Self-observation, pattern recognition (Phase 3+)
- **Temporal self** — Daily/weekly/monthly self-records (Phase 3+)
- **Loop tasks** — Scheduled idle behaviors, mood decay (Phase 3+)
- **Semantic search** — pgvector-based memory retrieval (Phase 3+)

Phase 2 delivers the **working pipeline**: CLI sends command, TTS server processes it, avatar app renders it. This is the foundation that all Phase 3+ features build on.
