# Step 1 — Scaffold Monorepo

## 1.1 Remove Git Submodule

```bash
git submodule deinit -f live-ai-partner-avatar
git rm -f live-ai-partner-avatar
rm -rf .git/modules/live-ai-partner-avatar
# Keep live-ai-partner-avatar/ contents in archive/ for reference if desired
```

Note: The submodule code becomes reference material. The actual extraction happens in later phases when we port Live2D rendering to `packages/plugin-avatar/live2d/`.

## 1.2 Root `package.json`

```json
{
  "name": "vibe-ai-partner",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "workspaces": [
    "packages/core",
    "packages/shared",
    "packages/plugin-avatar/*",
    "packages/plugin-tts/*",
    "packages/plugin-memory/*",
    "apps/*"
  ],
  "scripts": {
    "setup": "node scripts/setup.js",
    "start": "node scripts/start.js",
    "stop": "node scripts/stop.js",
    "restart": "npm stop && npm start",
    "status": "node scripts/status.js",
    "dev": "npm run dev -w apps/avatar-app",
    "build": "npm run build -ws",
    "test": "npm run test -ws",
    "tts:start": "node scripts/tts-start.js",
    "tts:stop": "node scripts/tts-stop.js",
    "tts:install": "node scripts/tts-install.js",
    "feeling": "node scripts/cli.js feeling",
    "action": "node scripts/cli.js action",
    "speak": "node scripts/cli.js speak",
    "switch": "node scripts/switch.js"
  },
  "devDependencies": {
    "typescript": "^5.7.0",
    "vitest": "^3.0.0"
  }
}
```

## 1.3 `tsconfig.base.json`

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "outDir": "dist",
    "rootDir": "src"
  }
}
```

## 1.4 Directory Skeleton

```bash
# Create all package directories
mkdir -p packages/core/src/{interfaces,state,events,config,utils}
mkdir -p packages/shared/src
mkdir -p packages/plugin-avatar
mkdir -p packages/plugin-tts
mkdir -p packages/plugin-memory
mkdir -p apps
mkdir -p scripts
mkdir -p models
```

## 1.5 `.env.example`

```bash
# Avatar
AVATAR_RENDERER=live2d          # live2d | vrm | threejs | html
AVATAR_MODEL=shizuku            # model name or path to model file

# TTS
TTS_ENGINE=kittentts            # kittentts | kokoro-onnx | kokoro
TTS_VOICE=Bella                 # voice name (depends on engine)
TTS_SPEED=1.0                   # playback speed
TTS_SERVER_PORT=5111            # server port
TTS_MODE=native                 # native | docker

# Entity
ENTITY_SOUL=./entity/SOUL.md   # path to soul definition
ENTITY_VOCAL_MODE=silent        # silent | reactive | conversational
ENTITY_HYPER_CONSCIOUSNESS_MODE=false  # true for GWT distributed consciousness

# Memory
MEMORY_MODE=basic               # basic | stateful | intelligent
DATABASE_URL=                   # only for stateful/intelligent
GEMINI_API_KEY=                 # only for intelligent

# Runtime
LOG_LEVEL=info                  # debug | info | warn | error
```

## 1.6 `.gitignore` Additions

```
# Models (downloaded by setup, not stored in git)
models/live2d/
models/vrm/
models/threejs/
!models/README.md

# Environment
.env
.env.local

# Build output
dist/
*.tsbuildinfo
```

## 1.7 Verification

```bash
npm install          # Should complete with no errors
ls packages/         # core/ shared/ plugin-avatar/ plugin-tts/ plugin-memory/
ls apps/             # (empty for now)
```
