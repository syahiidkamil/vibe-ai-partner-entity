# Phase 1 — Core Interfaces (`packages/core`)

## What This Delivers

The core package defines the **contracts** that all plugins must implement. It depends only on `@vibe-ai-partner/shared` for types. No DOM, no rendering, no TTS libraries — just interfaces, the EventBus, and the entity engine (FeelingEngine, ExpressionTrigger — covered in later docs).

```
packages/core/
├── package.json
├── tsconfig.json
└── src/
    └── interfaces/
        ├── plugin.ts            # IPlugin, IPluginManifest, IPluginRegistry
        ├── avatar-renderer.ts   # IAvatarRenderer
        ├── tts-engine.ts        # ITTSEngine + data types
        ├── communication.ts     # IEventBus + EventMap
        └── index.ts             # Barrel export
```

---

## `packages/core/package.json`

```json
{
  "name": "@vibe-ai-partner/core",
  "version": "0.1.0",
  "type": "module",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "scripts": {
    "build": "tsc",
    "test": "vitest run"
  },
  "dependencies": {
    "@vibe-ai-partner/shared": "workspace:*"
  },
  "devDependencies": {
    "vitest": "^3.0.0"
  },
  "files": ["dist"]
}
```

---

## `packages/core/tsconfig.json`

```json
{
  "extends": "../../tsconfig.base.json",
  "compilerOptions": {
    "outDir": "dist",
    "rootDir": "src"
  },
  "include": ["src"]
}
```

---

## `src/interfaces/plugin.ts` — IPlugin, IPluginManifest, IPluginRegistry

From [01-plugin-system](../architecture_after_review/01-plugin-system.md): every plugin declares a manifest, follows a lifecycle (initialize/dispose), and registers with a central registry that enforces one active plugin per type.

```typescript
import type { PluginType } from "@vibe-ai-partner/shared";

/**
 * Declares what a plugin is and what it can do.
 * Read at registration time. IDs must be unique within their plugin group.
 *
 * ID format: lowercase, hyphenated (e.g., "live2d", "kokoro-onnx", "kittentts")
 */
export interface IPluginManifest {
  /** Unique identifier within plugin group. Matches .env config values. */
  id: string;

  /** Human-readable display name (e.g., "Live2D Cubism Renderer") */
  name: string;

  /** Semver version string */
  version: string;

  /** Plugin category — only one plugin active per type at a time */
  type: PluginType;

  /** Feature flags the plugin supports (e.g., ["expressions", "motions", "lipsync"]) */
  capabilities: string[];
}

/**
 * Base interface for all plugins. Every plugin has a manifest,
 * can be initialized with config, and can be disposed.
 *
 * Lifecycle: register → initialize(config) → operate → dispose()
 */
export interface IPlugin {
  /** Static metadata about this plugin */
  readonly manifest: IPluginManifest;

  /**
   * Load resources, connect to services, prepare for operation.
   * Called once before the plugin becomes active.
   */
  initialize(config: Record<string, unknown>): Promise<void>;

  /**
   * Release all resources. Called when the plugin is no longer needed.
   * After dispose(), the plugin instance should not be used.
   */
  dispose(): Promise<void>;
}

/**
 * Manages plugin registration and activation.
 * Enforces one active plugin per type (Strategy pattern).
 *
 * Switching flow: deactivate old → initialize new → activate new
 */
export interface IPluginRegistry {
  /** Add a plugin to the registry. Does not initialize or activate it. */
  register(plugin: IPlugin): void;

  /** Get all registered plugins of a given type. */
  getPluginsByType(type: PluginType): IPlugin[];

  /** Get the currently active plugin for a type. Undefined if none active. */
  getActivePlugin(type: PluginType): IPlugin | undefined;

  /**
   * Switch the active plugin for a type.
   * Deactivates the current plugin (if any), initializes the new one, activates it.
   */
  setActivePlugin(type: PluginType, pluginId: string): Promise<void>;
}
```

---

## `src/interfaces/avatar-renderer.ts` — IAvatarRenderer

From [02-avatar-system](../architecture_after_review/02-avatar-system.md): the universal interface that Live2D, VRM, Three.js, and HTML renderers all implement. The interface uses string-based feelings and expressions — each plugin maps these to its native mechanism via `capabilities.json`.

```typescript
import type { IPlugin } from "./plugin.js";

/**
 * Universal avatar renderer interface.
 *
 * All renderers follow the same lifecycle:
 *   mount(container) → update loop → setFeeling/playSelfExpression/setLipSyncAmplitude → unmount()
 *
 * Feelings are persistent mood states (the avatar's face stays happy).
 * Self-expressions are one-shot motions (the avatar waves once).
 * Lip sync is driven by a normalized amplitude value from the TTS pipeline.
 *
 * What each method maps to internally depends on the renderer:
 *   - Live2D: .exp3.json presets, .motion3.json keyframes, ParamMouthOpenY
 *   - VRM: FACS blend shapes, bone quaternions, jaw + visemes
 *   - Three.js: morph targets, AnimationClip, morph target weights
 *   - HTML: CSS classes, CSS animations, CSS property transitions
 */
export interface IAvatarRenderer extends IPlugin {
  /**
   * Create canvas/DOM, load model, start render loop.
   * Called once when the renderer becomes active.
   */
  mount(container: HTMLElement): Promise<void>;

  /**
   * Per-frame update. Drives idle animations, physics, spring smoothing.
   * Called every requestAnimationFrame by the host.
   * @param deltaTime - Time since last frame in seconds
   */
  update(deltaTime: number): void;

  /**
   * Set a persistent feeling (mood). Maps to renderer-specific expression.
   * Unknown or unsupported feelings are silently ignored.
   * @param feeling - Feeling name (e.g., "happy", "frustrated")
   * @param intensity - Intensity 0-100
   */
  setFeeling(feeling: string, intensity: number): void;

  /**
   * Play a one-shot self-expression motion (e.g., wave, nod, laugh).
   * Resolves when the motion completes. Unknown expressions silently ignored.
   * @param name - Expression name (e.g., "wave", "celebrate")
   */
  playSelfExpression(name: string): Promise<void>;

  /**
   * Drive lip sync from audio amplitude.
   * Called at ~30Hz during TTS playback.
   * @param amplitude - Normalized 0-1 value (0 = closed, 1 = fully open)
   */
  setLipSyncAmplitude(amplitude: number): void;

  /**
   * Handle container resize. Updates canvas/camera/viewport.
   * @param width - New width in pixels
   * @param height - New height in pixels
   */
  resize(width: number, height: number): void;

  /**
   * Query which feelings this renderer supports.
   * Reads from the model's capabilities.json at runtime.
   * @returns Array of supported feeling names
   */
  getAvailableFeelings(): string[];

  /**
   * Query which self-expressions this renderer supports.
   * Reads from the model's capabilities.json at runtime.
   * @returns Array of supported expression names
   */
  getAvailableSelfExpressions(): string[];

  /**
   * Remove canvas/DOM elements. Release WebGL context.
   * The plugin can be remounted later without re-initialization
   * (e.g., switching tabs — model data stays loaded).
   */
  unmount(): void;
}
```

---

## `src/interfaces/tts-engine.ts` — ITTSEngine

From [03-tts-system](../architecture_after_review/03-tts-system.md): the universal TTS interface that Kokoro, Kokoro ONNX, KittenTTS, and custom engines implement. Supports both full generation and streaming.

```typescript
import type { IPlugin } from "./plugin.js";

/**
 * Options for TTS generation.
 */
export interface TTSOptions {
  /** Voice ID (e.g., "af_heart", "Bella"). Engine-specific. */
  voice?: string;

  /** Playback speed multiplier. 1.0 = normal. */
  speed?: number;

  /** Output audio format. */
  format?: "wav" | "mp3" | "opus";
}

/**
 * Result of full (non-streaming) TTS generation.
 */
export interface TTSResult {
  /** Raw audio data */
  audio: ArrayBuffer;

  /** Sample rate in Hz (e.g., 24000) */
  sampleRate: number;

  /** Duration in seconds */
  duration: number;
}

/**
 * A single chunk from streaming TTS generation.
 */
export interface TTSChunk {
  /** Partial audio data */
  audio: ArrayBuffer;

  /** Sample rate in Hz */
  sampleRate: number;

  /** True for the final chunk — no more data coming */
  isFinal: boolean;
}

/**
 * Metadata about an available voice.
 */
export interface VoiceInfo {
  /** Engine-specific voice ID (e.g., "af_heart", "Bella") */
  id: string;

  /** Human-readable name (e.g., "Heart (Female)") */
  name: string;

  /** Language code (e.g., "en-us", "ja") */
  language: string;

  /** Voice gender */
  gender: "male" | "female" | "neutral";
}

/**
 * Universal TTS engine interface.
 *
 * All engines follow the same pattern: Text in → Audio out.
 * Streaming is optional — engines that don't natively stream
 * can return a single-chunk AsyncIterable.
 *
 * Engine implementations:
 *   - Kokoro: Python daemon, PyTorch, GPU recommended, 27 voices, native streaming
 *   - Kokoro ONNX: ONNX Runtime, CPU-friendly, 20+ voices, full-then-play
 *   - KittenTTS: 15M param model, CPU-only, 8 voices, full-then-play
 */
export interface ITTSEngine extends IPlugin {
  /**
   * Generate complete audio from text.
   * Resolves when all audio is ready.
   * @param text - Text to synthesize
   * @param options - Voice, speed, format overrides
   */
  generate(text: string, options?: TTSOptions): Promise<TTSResult>;

  /**
   * Generate audio as a stream of chunks.
   * For engines that don't natively stream, yields a single chunk with isFinal=true.
   * @param text - Text to synthesize
   * @param options - Voice, speed, format overrides
   */
  generateStream(
    text: string,
    options?: TTSOptions,
  ): AsyncIterable<TTSChunk>;

  /**
   * Abort current generation/playback immediately.
   */
  stop(): void;

  /**
   * List all voices available in this engine.
   */
  getAvailableVoices(): Promise<VoiceInfo[]>;

  /**
   * Set the active voice for subsequent generation calls.
   * @param voiceId - Voice ID from getAvailableVoices()
   */
  setVoice(voiceId: string): void;
}
```

---

## `src/interfaces/communication.ts` — IEventBus

From [05-communication](../architecture_after_review/05-communication.md): the internal event bus (Layer 3) that decouples all components. Typed event map ensures compile-time safety — you can only emit/listen to known event types with correct payloads.

```typescript
import type { InternalStates, FeelingMap } from "@vibe-ai-partner/shared";

/**
 * Complete event map for the internal event bus.
 *
 * Three categories:
 * 1. State/feeling changes (from FeelingEngine)
 * 2. Avatar/TTS commands (from WebSocket client or direct calls)
 * 3. Plugin lifecycle and configuration
 */
export interface EventMap {
  // ─── State changes ───────────────────────────────────────
  "state:changed": { state: InternalStates };
  "feeling:changed": { feelings: FeelingMap };
  "feeling:threshold": { feeling: string; level: number };

  // ─── Avatar commands ─────────────────────────────────────
  "avatar:feeling": { name: string; intensity: number };
  "avatar:self-expression": { name: string };

  // ─── TTS events ──────────────────────────────────────────
  "tts:amplitude": { value: number };
  "tts:speaking-start": { text: string };
  "tts:speaking-stop": Record<string, never>;

  // ─── External commands (CLI → server → WebSocket → app) ──
  "command:feeling": { name: string };
  "command:action": { name: string };
  "command:speak": { text: string; voice?: string };

  // ─── Plugin lifecycle ────────────────────────────────────
  "plugin:activated": { id: string; type: string };
  "plugin:deactivated": { id: string; type: string };

  // ─── Configuration ───────────────────────────────────────
  "config:changed": { key: string; value: unknown };
}

/**
 * Typed event bus for internal inter-component communication.
 *
 * All communication between components within the desktop app
 * goes through this bus. Components never import each other directly.
 *
 * Usage:
 *   eventBus.on("feeling:changed", ({ feelings }) => { ... });
 *   eventBus.emit("avatar:feeling", { name: "happy", intensity: 82 });
 */
export interface IEventBus {
  /**
   * Subscribe to an event. Returns an unsubscribe function.
   * @param event - Event name from EventMap
   * @param handler - Callback receiving the typed payload
   * @returns Unsubscribe function — call to remove this listener
   */
  on<K extends keyof EventMap>(
    event: K,
    handler: (payload: EventMap[K]) => void,
  ): () => void;

  /**
   * Subscribe to an event for a single firing. Auto-unsubscribes after first call.
   * @param event - Event name from EventMap
   * @param handler - Callback receiving the typed payload
   */
  once<K extends keyof EventMap>(
    event: K,
    handler: (payload: EventMap[K]) => void,
  ): void;

  /**
   * Emit an event to all subscribers.
   * @param event - Event name from EventMap
   * @param payload - Typed payload matching the event
   */
  emit<K extends keyof EventMap>(
    event: K,
    payload: EventMap[K],
  ): void;

  /**
   * Remove all listeners for a specific event, or all listeners entirely.
   * @param event - Optional. If provided, clears only that event's listeners.
   */
  off<K extends keyof EventMap>(event?: K): void;
}
```

---

## `src/interfaces/index.ts` — Barrel Export

```typescript
// Plugin system
export type {
  IPlugin,
  IPluginManifest,
  IPluginRegistry,
} from "./plugin.js";

// Avatar renderer
export type { IAvatarRenderer } from "./avatar-renderer.js";

// TTS engine
export type {
  ITTSEngine,
  TTSOptions,
  TTSResult,
  TTSChunk,
  VoiceInfo,
} from "./tts-engine.js";

// Communication
export type {
  EventMap,
  IEventBus,
} from "./communication.js";
```

---

## Verification

After creating all files, verify:

```bash
# From project root
cd packages/core

# 1. TypeScript compiles with no errors
npx tsc --noEmit
# Expected: no output (clean compile)

# 2. Build produces dist/
npm run build
ls dist/interfaces/
# Expected: plugin.js, plugin.d.ts, avatar-renderer.js, avatar-renderer.d.ts,
#           tts-engine.js, tts-engine.d.ts, communication.js, communication.d.ts,
#           index.js, index.d.ts

# 3. Interfaces are importable
node -e "
  const core = require('./dist/interfaces/index.js');
  // Type-only exports won't have runtime values, but the module should load
  console.log('Core interfaces module loaded successfully');
"

# 4. Shared dependency resolves
node -e "
  const shared = require('@vibe-ai-partner/shared');
  console.log('Shared package resolves:', Object.keys(shared).length, 'exports');
"
```

### Checklist

- [ ] `package.json` depends on `@vibe-ai-partner/shared` via `workspace:*`
- [ ] `tsconfig.json` extends root `tsconfig.base.json`
- [ ] `IPlugin` has `manifest`, `initialize(config)`, `dispose()`
- [ ] `IPluginManifest` has `id`, `name`, `version`, `type`, `capabilities`
- [ ] `IPluginRegistry` has `register`, `getPluginsByType`, `getActivePlugin`, `setActivePlugin`
- [ ] `IAvatarRenderer` extends `IPlugin` with `mount`, `update`, `setFeeling`, `playSelfExpression`, `setLipSyncAmplitude`, `resize`, `getAvailableFeelings`, `getAvailableSelfExpressions`, `unmount`
- [ ] `ITTSEngine` extends `IPlugin` with `generate`, `generateStream`, `stop`, `getAvailableVoices`, `setVoice`
- [ ] `TTSOptions` has `voice?`, `speed?`, `format?`
- [ ] `TTSResult` has `audio: ArrayBuffer`, `sampleRate`, `duration`
- [ ] `TTSChunk` has `audio: ArrayBuffer`, `sampleRate`, `isFinal`
- [ ] `VoiceInfo` has `id`, `name`, `language`, `gender`
- [ ] `EventMap` covers all events from [05-communication](../architecture_after_review/05-communication.md)
- [ ] `IEventBus` has `on` (returns unsubscribe fn), `once`, `emit`, `off`
- [ ] All imports from `@vibe-ai-partner/shared` resolve correctly
- [ ] `npx tsc --noEmit` passes with zero errors
