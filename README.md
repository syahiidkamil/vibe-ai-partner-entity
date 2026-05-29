# VAPE — Vibe AI Partner Entity

A Live2D avatar companion for Claude Code. The avatar reacts to your coding session — expressions change based on state, motions trigger from events, and lip sync drives from TTS audio.

## Prerequisites

- **Node.js** >= 18 ([nvm](https://github.com/nvm-sh/nvm) recommended)
- **uv** — Python package manager ([install](https://docs.astral.sh/uv/getting-started/installation/))

```bash
# macOS
brew install uv node

# or
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Setup

```bash
uv run vape setup
```

The setup wizard lets you:
1. Choose a TTS engine
2. Download model files
3. Select language packs
4. Choose an avatar **renderer** (the look) and a **shell** (the window host)

For the Live2D renderer, setup also downloads the proprietary Live2D Cubism Core
(not redistributable via git) from Live2D's official CDN.

| Engine | Size | Best for |
|--------|------|----------|
| **Kokoro ONNX** (recommended) | ~300MB | Good quality, CPU-only, fast |
| **Kokoro (PyTorch)** | ~2GB | Best quality, GPU optional |
| **KittenTTS** | ~150MB | Lightest, CPU-only |

## Run

```bash
uv run vape start
```

This starts the TTS server on port 5111 and launches the avatar desktop window.

```bash
uv run vape stop       # stop the server (and the avatar window)
uv run vape status     # check what's running
```

## Avatar: mix-and-match renderers + shells

The avatar is split into two independent, swappable pieces:

- **Renderer** — the avatar itself (content + assets), served by the server as a
  plain web page. `avatar-live2d` (default), `avatar-threejs`, `avatar-html`.
- **Shell** — the native window that hosts it. `electron` (default), `tauri` (experimental).

Pick any combination in `config.json`:

```json
"avatar": {
  "renderer": "avatar-html",
  "shell": "tauri"
}
```

| | `electron` | `tauri` |
|---|---|---|
| `avatar-live2d` | ✅ default | ✅ experimental |
| `avatar-threejs` | ✅ | ✅ experimental |
| `avatar-html` | ✅ | ✅ experimental |

Electron works out of the box. Tauri is a smaller/faster native window; its Rust
binary is compiled when you select it in `vape setup`. (The legacy
`"avatar": {"plugin": "live2d-electron"}` config is migrated automatically.)

## CLI Commands

### Speech

```bash
uv run vape speak "Hello world"                     # speak with lip sync
uv run vape speak "Konnichiwa" --voice jf_alpha      # specific voice
uv run vape speak "Faster speech" --speed 1.5        # adjust speed
```

### Feelings (expressions)

```bash
uv run vape feeling happy
```

Available: `normal`, `happy`, `sad`, `angry`, `frustrated`, `curious`, `proud`, `anxious`, `excited`, `calm`, `bored`, `guilty`, `blushing`, `surprised`

### Actions (motions)

```bash
uv run vape action wave
```

Available: `nod`, `headshake`, `headtilt`, `laugh`, `giggle`, `gasp`, `think`, `celebrate`, `sweat`, `wave`, `bow`, `starryeyes`

## REST API

For integrations (server must be running):

```
POST /api/speak     {"text": "Hello", "voice": "af_heart", "speed": 1.0}
POST /api/feeling   {"name": "happy"}
POST /api/action    {"name": "wave"}
POST /api/stop
POST /api/voice     {"voice": "bf_emma"}
GET  /api/health
GET  /api/voices
GET  /api/avatar/interface
GET  /audio/{id}.wav   (TTS clip, referenced by /ws/audio messages)
```

## WebSocket Protocol

The avatar connects to the server via two WebSocket channels:

**`/ws/status`** — control messages (feelings, actions)
```json
{"type": "feeling", "name": "happy"}
{"type": "action", "name": "wave"}
```

**`/ws/audio`** — audio delivery (HTTP URLs, served same-origin by the server)
```json
{"type": "audio", "url": "/audio/abc123.wav", "text": "Hello world", "isLast": true}
```

The avatar plays audio via `new Audio(url)` with AnalyserNode-driven lip sync.
Serving audio over HTTP (rather than a local file path) is what lets renderers
run in any shell — Electron, Tauri, or a plain browser — with no Node access.

## Project Structure

```
vape/                       Project source root (import package: engine)
  engine/                   Python package — `import engine`
    cli/              CLI commands — setup, start, stop, speak, feeling, action
    server/           FastAPI server — REST + WebSocket
    apps/
      tts/            TTS pipeline — engine plugins, sentence splitting, WAV generation
      avatar/         Avatar plugin discovery + interface contracts
  entity/                   The companion's persistent memory, soul, and runtime state
  plugins/
    renderers/              Avatar content (served as web pages)
      avatar-live2d/        Live2D Cubism avatar (default)
      avatar-threejs/       Three.js 3D chibi avatar
      avatar-html/          Lightweight HTML/CSS avatar
    shells/                 Native window hosts
      electron/             Electron host (default)
      tauri/                Tauri host (experimental, Rust)
    tts-kokoro-onnx/        Kokoro ONNX engine plugin
    tts-kokoro/             Kokoro PyTorch engine plugin
    tts-kitten/             KittenTTS engine plugin
  model-stocks/             Avatar model files (downloaded by setup, gitignored)

config.json                 User configuration (engine, voice, avatar renderer + shell)
```
