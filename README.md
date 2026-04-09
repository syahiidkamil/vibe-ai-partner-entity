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
4. Choose an avatar plugin

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
uv run vape stop       # stop the server
uv run vape status     # check what's running
```

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
```

## WebSocket Protocol

The avatar connects to the server via two WebSocket channels:

**`/ws/status`** — control messages (feelings, actions)
```json
{"type": "feeling", "name": "happy"}
{"type": "action", "name": "wave"}
```

**`/ws/audio`** — audio delivery (file paths to temp WAV files)
```json
{"type": "audio", "path": "/tmp/tts-abc123.wav", "text": "Hello world", "isLast": true}
```

The avatar plays audio natively via `new Audio(path)` with AnalyserNode-driven lip sync.

## Project Structure

```
src/vape/
  cli/              CLI commands — setup, start, stop, speak, feeling, action
  server/           FastAPI server — REST + WebSocket
  apps/
    tts/            TTS pipeline — engine plugins, sentence splitting, WAV generation
    avatar/         Avatar plugin discovery + interface contracts

plugins/
  avatar-live2d-electron/   Live2D avatar + Electron shell (default)
  tts-kokoro-onnx/          Kokoro ONNX engine plugin
  tts-kokoro/               Kokoro PyTorch engine plugin
  tts-kitten/               KittenTTS engine plugin

config.json         User configuration (engine, voice, avatar plugin)
```
