# Vibe AI Partner

A Live2D avatar companion for Claude Code. The avatar reacts to your coding session — expressions change based on state, motions trigger from events, and lip sync drives from TTS audio.

## Prerequisites

- **Node.js** >= 18 ([nvm](https://github.com/nvm-sh/nvm) recommended)
- **uv** — Python package manager ([install](https://docs.astral.sh/uv/getting-started/installation/))

```bash
# macOS
brew install uv

# or
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Setup

```bash
# 1. Install Node dependencies + build
npm install && npm run build

# 2. Choose and install a TTS engine
npm run setup
```

The setup command lets you pick a TTS engine:

| Engine | Size | Best for |
|--------|------|----------|
| **Kokoro ONNX** (recommended) | ~300MB | Good quality, CPU-only, fast |
| **Kokoro (PyTorch)** | ~2GB | Best quality, streaming, GPU optional |
| **KittenTTS** | ~150MB | Lightest, CPU-only, 15M params |

## Run

```bash
npm start
```

This single command:
1. Starts the TTS server on port 5111 (via `uv`)
2. Starts the avatar app dev server on http://localhost:1420

First run may take up to 2 minutes while the TTS model downloads. You'll see progress dots — don't interrupt.

```bash
npm stop        # stop both
npm run status  # check what's running
```

## CLI Commands

```bash
npm run speak "Hello world"    # speak with lip sync
npm run feeling happy          # set avatar expression
npm run action wave            # trigger a motion
```

Available feelings: `happy`, `sad`, `frustrated`, `curious`, `proud`, `anxious`, `excited`, `calm`, `bored`, `guilty`, `angry`, `blushing`, `surprised`, `relieved`

Available actions: `wave`, `nod`, `headTilt`, `laugh`, `giggle`, `surprisedGasp`, `think`, `celebrate`, `sweatDrop`, `bow`, `headShake`, `starryEyes`

## Project Structure

```
apps/
  avatar-app/     Tauri 2 desktop app — renders Live2D avatar
  tts-server/     Python FastAPI — TTS, state engine, WebSocket
  cli/            CLI commands — start, stop, speak, feeling, action

packages/
  core/           Interfaces, state engine, event bus
  shared/         Types, constants, protocol definitions
  plugin-avatar/
    live2d/       Live2D renderer plugin (PixiJS + pixi-live2d-display)

models/
  live2d/shizuku/ Shizuku model — expressions, motions, textures
```
