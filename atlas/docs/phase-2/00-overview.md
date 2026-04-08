# Phase 2 — Live2D Plugin + TTS Server + Avatar App

## What Phase 2 Delivers

Phase 2 produces the first working end-to-end system: a Live2D avatar that appears on screen, shows feelings, plays self-expression motions, and speaks with real-time lip sync.

| Deliverable | Description |
|-------------|-------------|
| **Live2D plugin** | `packages/plugin-avatar/live2d/` — implements `IAvatarRenderer` with PixiJS + pixi-live2d-display |
| **TTS server** | `apps/tts-server/` — Python FastAPI wrapping Kokoro, serves REST + WebSocket for audio generation |
| **Avatar app** | `apps/avatar-app/` — Tauri 2 transparent window hosting the Live2D renderer with system tray controls |
| **CLI commands** | `npm run feeling`, `npm run action`, `npm run speak` — control the avatar from the terminal |
| **Model files** | Shizuku model extracted from submodule into `models/live2d/shizuku/` with `capabilities.json` |

## Goal

Avatar appears on screen, shows feelings, plays expressions, speaks with lip sync. All controllable from both the system tray menu and CLI.

## What Phase 2 Does NOT Deliver

These are Phase 3+:

- No VRM or Three.js avatar plugins
- No hooks integration (Claude Code hooks are Phase 8)
- No memory backend or PostgreSQL
- No consciousness persistence or hyper-consciousness mode
- No Claude Code integration
- No SOUL.md runtime parsing
- No HTML fallback renderer (simple enough to add later)

## Success Criteria

Every criterion is manually testable:

1. **`npm start` launches TTS server + avatar app** — Both processes start, health checks pass
2. **Shizuku Live2D model renders in transparent window** — Model visible, idle animation playing, window always-on-top with no background
3. **Right-click tray -> Feelings -> Happy -> avatar shows happy expression** — Expression changes visibly, reverts on "Normal"
4. **Right-click tray -> Actions -> Wave -> avatar plays wave motion** — One-shot motion plays and completes
5. **`npm run speak "Hello"` -> TTS generates audio -> lip sync on avatar** — Speech bubble appears, mouth moves in sync with audio, cleans up after
6. **`npm run feeling happy` / `npm run action wave` work from CLI** — HTTP requests hit the avatar app, same result as tray menu

## Dependency Order

```
1. Model files (extract Shizuku from submodule, create capabilities.json)
   |
2. Live2D plugin (implements IAvatarRenderer, loads capabilities.json)
   |
3. TTS server (Python FastAPI + Kokoro, REST API for audio generation)
   |
4. Avatar app (Tauri 2 window, hosts Live2D plugin, system tray, HTTP server)
   |
5. Integration (CLI scripts, npm start orchestration, end-to-end testing)
```

## What to Port vs Write New

### Port from submodule (`live-ai-partner-avatar/desktop/`)

| What | Source | Destination |
|------|--------|-------------|
| Live2D rendering | `index.html` — PixiJS app creation, model loading, scaling, idle motion | `live2d-renderer.ts` — `mount()`, `update()` |
| Expression application | `index.html` — `setExpression()`, `EXPRESSION_MAP`, expressionManager lookup | `expression-manager.ts` — capabilities.json-driven mapping |
| Motion playback | `index.html` — `playSelfExpression()`, `SELF_EXPRESSION_MAP`, motion group/index | `motion-player.ts` — capabilities.json-driven mapping |
| Lip sync | `index.html` — `updateLipSync()`, RMS calculation, smoothed mouth parameter | `lip-sync-driver.ts` — amplitude smoothing + ParamMouthOpenY |
| Kokoro TTS daemon | External Python process (currently via Unix socket) | `apps/tts-server/` — FastAPI with HTTP REST |
| Shizuku model files | `shizuku/runtime/` — .model3.json, .moc3, textures, expressions, motions | `models/live2d/shizuku/` — same files + capabilities.json |

### Write new

| What | Why |
|------|-----|
| **Tauri 2 app** | Replaces Electron — smaller binary, better security, Rust backend |
| **HTTP REST API** | Replaces Unix domain sockets — cross-platform, standard tooling |
| **`capabilities.json`** | New config-driven approach — replaces hardcoded maps in index.html |
| **TypeScript plugin structure** | New — implements `IAvatarRenderer` interface from Phase 1 |
| **npm orchestration scripts** | New — `scripts/start.js`, `scripts/cli.js` for unified commands |

## Phase 1 Dependencies Used

Phase 2 builds directly on Phase 1 artifacts:

| Phase 1 Package | What Phase 2 Uses |
|-----------------|-------------------|
| `@vibe-ai-partner/shared` | `FeelingName`, `FEELING_NAMES`, `ExpressionGroup`, `PluginType`, protocol types (`SpeakRequest`, `FeelingRequest`, `ActionRequest`, `WSAmplitude`) |
| `@vibe-ai-partner/core` | `IAvatarRenderer` interface (the contract Live2D plugin implements), `IPlugin`/`IPluginManifest` (manifest structure), `EventBus` (feeling/expression events), `FeelingEngine` (state-to-feeling derivation) |

## Implementation Docs

| Doc | What it covers |
|-----|---------------|
| [01-live2d-plugin](01-live2d-plugin.md) | Live2D avatar plugin — directory structure, Live2DRenderer class, expression/motion/lip-sync modules, tests |
| [02-tts-server](02-tts-server.md) | Python FastAPI TTS server — Kokoro integration, REST endpoints, WebSocket audio streaming |
| [03-avatar-app](03-avatar-app.md) | Tauri 2 desktop app — transparent window, system tray, HTTP server for CLI control |
| [04-model-setup](04-model-setup.md) | Model file extraction, capabilities.json creation, model registry, download scripts |
| [05-integration](05-integration.md) | npm start orchestration, CLI commands, end-to-end verification steps |
