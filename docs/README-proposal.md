# Vibe AI Partner

What if your AI coding partner had a body?

Not a chatbot widget. Not a notification icon. A presence — something that sits on your screen, watches you work, and reacts because it *feels* something about what's happening. It nods when it understands. It sighs when it's stuck. It celebrates when tests pass.

Vibe AI Partner gives your AI a virtual body with an internal emotional life.

<!-- TODO: screenshot or gif -->

## What Makes This Different

Most avatar projects are reactive puppets — they animate when you press a button. This one has an inner world:

- **6 internal states** (confidence, momentum, alignment...) that track what the AI knows about its situation
- **14 feelings** (happy, frustrated, curious, proud...) that emerge from those states — not random, not scripted
- **60+ physical expressions** (wave, nod, laugh, sigh, fist pump...) triggered when feelings cross thresholds

The avatar doesn't just move. It *feels* — and you can see it.

## Quick Start

```bash
git clone https://github.com/.../vibe-ai-partner.git
cd vibe-ai-partner
npm run setup
```

Setup walks you through choosing your avatar style and voice engine. It only installs what you pick.

```bash
npm start     # launch
npm stop      # shutdown
```

That's it.

## You Choose What to Install

### Avatar (how it looks)

| Option | Style | What you need |
|--------|-------|--------------|
| **Live2D** | 2D anime | Included model (Shizuku) |
| **VRM** | 3D character | Bring your own .vrm file |
| **Three.js** | 3D custom | Bring your own .glb model |

### Voice (how it speaks)

All sizes are storage on disk — not RAM.

| Option | Storage | GPU? | Best for |
|--------|---------|------|----------|
| **KittenTTS** | ~25MB | No | Quick setup, low-spec machines |
| **Kokoro ONNX** | ~80MB (quantized) | No | Good quality on CPU, multilingual |
| **Kokoro** | ~350MB model + ~1.5GB PyTorch | Recommended | Best quality, streaming |

Don't have a GPU? Pick KittenTTS or Kokoro ONNX — both run great on CPU. You can always switch later in `.env`.

## Requirements

| What | Why | Install |
|------|-----|---------|
| **Node.js** 20+ | Avatar app, CLI, setup scripts | [nodejs.org](https://nodejs.org) |
| **Python** 3.10-3.12 | TTS server (Kokoro/KittenTTS are Python libraries) | [python.org](https://python.org) |
| **Rust** 1.86+ | Tauri 2 compiles to native binary | Auto-installed via [rustup](https://rustup.rs) — `npm run setup` handles this |
| **Claude Code** | Hook integration (avatar reacts to Claude) | [docs](https://docs.anthropic.com/en/docs/claude-code) |

**Optional:**

| What | Why | When |
|------|-----|------|
| **GPU** (MPS/CUDA) | Faster TTS inference | Only if you choose Kokoro (full). KittenTTS and Kokoro ONNX run on CPU. |
| **PostgreSQL** | Feeling history, state persistence | Only for stateful/intelligent memory mode |
| **Gemini API key** | Semantic search across memories | Only for intelligent memory mode (free tier available) |
| **Docker** | TTS server isolation | Only if you prefer containerized Python |

## How It Works

The avatar connects to Claude Code through hooks. When Claude thinks, edits code, runs tests, or finishes a response — the avatar knows, and reacts.

```
Claude Code ──hooks──→ TTS Server ──WebSocket──→ Avatar App
                                                    │
                                        Entity Engine (internal)
                                        States → Feelings → Expressions
```

A fast model analyzes Claude's response sentiment. The entity engine translates that into feelings. Feelings drive the body.

## Settings

Everything lives in `.env`:

```bash
AVATAR_RENDERER=live2d       # live2d | vrm | threejs
TTS_ENGINE=kittentts         # kittentts | kokoro-onnx | kokoro
TTS_VOICE=Bella              # voice name (depends on engine)
```

Change, restart, done.

## Works On

macOS, Windows, Linux. The avatar app is built with Tauri 2 (~5MB binary).

## Architecture

The system is designed so avatar renderers and TTS engines are swappable — same interfaces, different implementations. See [docs/architecture/](docs/architecture/00-overview.md) for the full picture.

## Research

The entity model (how AI feels) is documented in [self-research/](self-research/) — this is original research into AI consciousness simulation, not borrowed from existing projects.

## License

<!-- TODO -->
