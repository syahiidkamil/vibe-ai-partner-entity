# Phase 01: Easy Setup Vibe AI Partner

## Objective

Replace the current multi-runtime setup (Node.js + Python + uv) with a Python-only CLI that lets users go from `git clone` to working avatar in two commands: `uv run vibe setup` and `uv run vibe start`. Plugin-based architecture ensures users only download what they choose.

## Deliverables

- **Python CLI** (typer) replacing Node.js CLI — commands: `setup`, `start`, `stop`, `status`, `download`, `speak`, `feeling`, `action`
- **Plugin manifest system** (`plugin.json`) — each TTS plugin declares models, languages, download sizes
- **Interactive setup wizard** — prerequisite checks, engine selection, explicit model downloads with progress bars, per-language opt-in
- **Avatar served by FastAPI** — pre-built static files committed to repo, served alongside TTS API on port 5111
- **Download management** — skip-if-cached, progress bars, atomic downloads, post-setup language additions via `vibe download`
- **Cross-platform support** — macOS, Linux, Windows

## Out of Scope

- No new TTS engines
- No avatar app changes (just pre-build and serve existing)
- No CI/CD pipelines
- No Docker (future phase)

## Dependencies

- **Requires:** Current TTS server (FastAPI) and plugin architecture (already exists)
- **Enables:** Future Docker option, public release, contributor onboarding

## Technical Approach

### Architecture

```
User: uv run vibe setup → uv run vibe start → localhost:5111

apps/tts-server/
  pyproject.toml              # Add typer dep, [project.scripts] vibe entry
  src/vibe_tts/
    cli/                      # NEW: Python CLI
      main.py                 # Typer app entry
      setup.py                # Interactive wizard
      start.py                # Foreground uvicorn
      stop.py                 # HTTP shutdown + fallback
      download.py             # Model/language management
      _config.py              # config.json read/write
      _paths.py               # Central path resolution
      _progress.py            # Download with progress bars
      _prereqs.py             # Prerequisite validation
    server.py                 # MODIFIED: add StaticFiles mount

packages/plugin-tts/
  kokoro-onnx/plugin.json     # Plugin manifest
  kokoro/plugin.json           
  kitten/plugin.json           

apps/avatar-app/dist/         # Pre-built, committed to repo
```

### Download Layers (explicit, user-controlled)

```
Layer 0: Core         ~5MB    Python deps + FastAPI (always)
Layer 1: Plugin deps  varies  Python deps for chosen engine
Layer 2: Models       ~300MB+ ONNX model files (during setup, with progress)
Layer 3: Languages    opt-in  Chinese model, UniDic, etc.
```

### Key Design Decisions

1. **Foreground server** — `vibe start` runs uvicorn in foreground (no detached/PID files). `--daemon` flag for background mode.
2. **Single port** — TTS API + avatar static files on port 5111. Eliminates cross-origin issues.
3. **Plugin manifests** — JSON files declaring models/languages/sizes. CLI reads these dynamically.
4. **Atomic downloads** — download to `.part` file, rename on completion. Skip if cached.
5. **Archive Node.js CLI** — move `apps/cli/` to `archives/cli-node/`. No side-by-side, clean break.

### Implementation Order

```
Phase A: Foundation
  A1. Root pyproject.toml + CLI skeleton (typer)
  A2. Plugin manifest files (plugin.json)
  A3. Path resolution + config modules

Phase B: Core Commands
  B1. vibe setup (interactive wizard, model downloads, language opt-in)
  B2. vibe start (foreground uvicorn + static avatar)
  B3. vibe stop (HTTP shutdown endpoint)
  B4. vibe status (health check)

Phase C: Static Avatar
  C1. Modify server.py to serve static files
  C2. Pre-build and commit avatar dist

Phase D: Polish
  D1. vibe speak/feeling/action (HTTP wrappers)
  D2. vibe download (post-setup language management)
  D3. Progress bar downloads in engine.py

Phase E: Transition
  E1. Archive Node.js CLI: move apps/cli/ → archives/cli-node/
  E2. Remove Node.js npm scripts from root package.json
  E3. Update README (uv run vibe as the only documented path)
```

## Acceptance Criteria

1. User can run `uv run vibe setup` from repo root — interactive wizard completes successfully
2. User can run `uv run vibe start` — TTS server + avatar accessible at `localhost:5111`
3. Setup wizard shows engine options with download sizes
4. Model downloads show progress bars with speed and ETA
5. Per-language opt-in works — user selects languages, only selected ones download
6. Already-cached models are skipped (no re-download)
7. `vibe stop` cleanly shuts down the server
8. Avatar renders correctly when served as static files by FastAPI
9. Lip-sync, emotions, and actions work through same-origin WebSocket
10. Works on macOS (Apple Silicon + Intel) and Linux
11. Node.js is NOT required for end users (only uv)
12. Old Node.js CLI archived to `archives/cli-node/` (not deleted, preserved for reference)

## Implementation Notes

### Critical Files to Modify

- `apps/tts-server/pyproject.toml` — add typer[all], httpx, [project.scripts] entry
- `apps/tts-server/src/vibe_tts/server.py` — add `StaticFiles` mount + `/api/shutdown` endpoint
- `packages/plugin-tts/kokoro-onnx/src/vibe_plugin_tts_kokoro_onnx/engine.py` — refactor downloads to support progress callbacks
- `.gitignore` — allow `apps/avatar-app/dist/` except `live2dcubismcore.min.js` (proprietary)

### Plugin Manifest Schema (plugin.json)

```json
{
  "name": "kokoro-onnx",
  "displayName": "Kokoro ONNX",
  "description": "Good quality, CPU-only",
  "tag": "Recommended",
  "uvExtra": "kokoro-onnx",
  "models": [
    { "name": "kokoro-v1.0.onnx", "url": "...", "size_mb": 300, "required": true }
  ],
  "languages": [
    { "code": "en", "name": "English", "size_mb": 0, "included": true },
    { "code": "ja", "name": "Japanese", "size_mb": 526, "included": false },
    { "code": "zh", "name": "Chinese", "size_mb": 305, "included": false }
  ]
}
```

### Cross-Platform Notes

- Use `pathlib.Path` everywhere
- Cache dir: `platformdirs.user_cache_dir("vibe-ai-partner")`
- espeak-ng: platform-specific install hints in plugin manifest
- Process stop: HTTP `/api/shutdown` (cross-platform), no `lsof` or `taskkill`
- Signals: uvicorn handles SIGINT/SIGTERM natively
