# Step 1 — Live2D Avatar Plugin

## Directory Structure

```
packages/plugin-avatar/live2d/
├── package.json
├── tsconfig.json
├── src/
│   ├── index.ts                    # Export Live2DRenderer plugin
│   ├── live2d-renderer.ts          # Main class implements IAvatarRenderer
│   ├── pixi-setup.ts              # PixiJS Application + canvas init
│   ├── expression-manager.ts       # Load capabilities.json → map feelings to exp3.json
│   ├── motion-player.ts           # Load capabilities.json → map expressions to motion3.json
│   ├── lip-sync-driver.ts         # ParamMouthOpenY amplitude mapping
│   └── types.ts                   # Live2D-specific types
└── __tests__/
    ├── expression-manager.test.ts
    └── motion-player.test.ts
```

## 1.1 `package.json`

```json
{
  "name": "@vibe-ai-partner/plugin-avatar-live2d",
  "version": "0.1.0",
  "type": "module",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "scripts": {
    "build": "tsc",
    "test": "vitest run"
  },
  "dependencies": {
    "@vibe-ai-partner/core": "*",
    "@vibe-ai-partner/shared": "*",
    "pixi.js": "^7.0.0",
    "pixi-live2d-display": "^0.4.0"
  },
  "devDependencies": {
    "vitest": "^3.0.0"
  }
}
```

**Why PixiJS 7?** The submodule uses PixiJS 6, but pixi-live2d-display ^0.4.0 supports PixiJS 7. We upgrade to get the latest WebGL improvements. pixi-live2d-display handles all Cubism SDK integration — we do not import the Cubism SDK directly.

**Why not PixiJS 8?** pixi-live2d-display has not released a PixiJS 8-compatible version yet. Verify at build time and upgrade if available.

## 1.2 `tsconfig.json`

```json
{
  "extends": "../../../tsconfig.base.json",
  "compilerOptions": {
    "outDir": "dist",
    "rootDir": "src"
  },
  "include": ["src"],
  "references": [
    { "path": "../../core" },
    { "path": "../../shared" }
  ]
}
```

## 1.3 `src/types.ts` — Live2D-Specific Types

```typescript
import type { FeelingName, ExpressionGroup } from "@vibe-ai-partner/shared";

// ─── capabilities.json schema (Live2D variant) ────────────────

export interface Live2DCapabilities {
  renderer: "live2d";
  model: string;
  version?: string;

  feelings: Record<string, Live2DFeelingMapping | null>;
  selfExpressions: Record<string, Live2DSelfExpressionMapping>;
  lipSync: Live2DLipSyncConfig;
}

export interface Live2DFeelingMapping {
  /** Relative path to .exp3.json file within the model directory */
  expression: string;
}

export interface Live2DSelfExpressionMapping {
  /** Relative path to .motion3.json file within the model directory */
  motion: string;
  /** Expression group for categorization */
  group: ExpressionGroup;
}

export interface Live2DLipSyncConfig {
  method: "rms";
  /** Cubism parameter name (e.g., "ParamMouthOpenY" or "PARAM_MOUTH_OPEN_Y") */
  parameter: string;
  /** Min/max range for the parameter */
  range: [number, number];
}

// ─── Runtime types ─────────────────────────────────────────────

export interface Live2DRendererConfig {
  /** Absolute path to the model directory containing model3.json + capabilities.json */
  modelPath: string;
  /** Override canvas width (default: container width) */
  width?: number;
  /** Override canvas height (default: container height) */
  height?: number;
}
```

## 1.4 `src/live2d-renderer.ts` — Main Plugin Class

This is the core class that implements `IAvatarRenderer`. It delegates to the three supporting modules (expression, motion, lip sync) and manages the PixiJS render loop.

```typescript
import type { IPluginManifest } from "@vibe-ai-partner/core";
import type { IAvatarRenderer } from "@vibe-ai-partner/core";
import type { Live2DRendererConfig, Live2DCapabilities } from "./types.js";
import { createPixiApp, type PixiAppHandle } from "./pixi-setup.js";
import { ExpressionManager } from "./expression-manager.js";
import { MotionPlayer } from "./motion-player.js";
import { LipSyncDriver } from "./lip-sync-driver.js";

export class Live2DRenderer implements IAvatarRenderer {
  // ─── IPlugin ─────────────────────────────────────────────────
  readonly manifest: IPluginManifest = {
    id: "live2d",
    name: "Live2D Cubism Renderer",
    version: "0.1.0",
    type: "avatar-renderer",
    capabilities: ["expressions", "motions", "lipsync", "physics"],
  };

  // ─── Private state ──────────────────────────────────────────
  private config: Live2DRendererConfig | null = null;
  private capabilities: Live2DCapabilities | null = null;
  private pixiHandle: PixiAppHandle | null = null;
  private model: any = null; // pixi-live2d-display Live2DModel instance
  private expressionManager: ExpressionManager | null = null;
  private motionPlayer: MotionPlayer | null = null;
  private lipSyncDriver: LipSyncDriver | null = null;
  private mounted = false;

  // ─── IPlugin lifecycle ──────────────────────────────────────

  async initialize(config: Record<string, unknown>): Promise<void> {
    this.config = config as unknown as Live2DRendererConfig;

    // Load capabilities.json from model directory
    const capabilitiesUrl = `${this.config.modelPath}/capabilities.json`;
    const response = await fetch(capabilitiesUrl);
    if (!response.ok) {
      throw new Error(`Failed to load capabilities.json from ${capabilitiesUrl}`);
    }
    this.capabilities = await response.json();

    if (this.capabilities!.renderer !== "live2d") {
      throw new Error(
        `capabilities.json renderer is "${this.capabilities!.renderer}", expected "live2d"`
      );
    }

    // Initialize sub-modules with capabilities data
    this.expressionManager = new ExpressionManager(this.capabilities!.feelings);
    this.motionPlayer = new MotionPlayer(this.capabilities!.selfExpressions);
    this.lipSyncDriver = new LipSyncDriver(this.capabilities!.lipSync);
  }

  async dispose(): Promise<void> {
    if (this.mounted) {
      this.unmount();
    }
    this.model = null;
    this.expressionManager = null;
    this.motionPlayer = null;
    this.lipSyncDriver = null;
    this.capabilities = null;
    this.config = null;
  }

  // ─── IAvatarRenderer ────────────────────────────────────────

  async mount(container: HTMLElement): Promise<void> {
    if (!this.config || !this.capabilities) {
      throw new Error("Plugin not initialized. Call initialize() first.");
    }

    const width = this.config.width ?? container.clientWidth;
    const height = this.config.height ?? container.clientHeight;

    // Create PixiJS application with transparent background
    this.pixiHandle = createPixiApp(container, width, height);

    // Load model via pixi-live2d-display
    // Ported from submodule: index.html init() function
    const { Live2DModel, MotionPreloadStrategy } = await import("pixi-live2d-display");
    const modelPath = `${this.config.modelPath}/shizuku.model3.json`;

    this.model = await Live2DModel.from(modelPath, {
      motionPreload: MotionPreloadStrategy.ALL,
    });

    // Scale and center the model to fill the container
    // Ported from submodule: scale calculation in init()
    const scale = Math.min(width / this.model.width, height / this.model.height) * 0.95;
    this.model.scale.set(scale);
    this.model.anchor.set(0.5, 0.5);
    this.model.x = width / 2;
    this.model.y = height / 2 - 20;

    // Disable auto eye blink to prevent conflict with motion blink curves
    // Ported from submodule: model.internalModel.eyeBlink = null
    this.model.internalModel.eyeBlink = null;

    this.pixiHandle.app.stage.addChild(this.model);

    // Bind sub-modules to the loaded model
    this.expressionManager!.bind(this.model);
    this.motionPlayer!.bind(this.model);
    this.lipSyncDriver!.bind(this.model);

    // Start idle motion
    // Ported from submodule: model.motion('Idle', 0)
    this.model.motion("Idle", 0);

    this.mounted = true;
  }

  update(deltaTime: number): void {
    // PixiJS handles its own render loop via requestAnimationFrame.
    // This method exists for the host to call if it needs explicit frame control.
    // The Live2D model's Cubism physics and idle animations update automatically
    // through pixi-live2d-display's internal ticker.
    //
    // If we need manual control later (e.g., pausing physics), we can
    // intercept the ticker here.
  }

  setFeeling(feeling: string, intensity: number): void {
    if (!this.expressionManager || !this.mounted) return;
    this.expressionManager.apply(feeling, intensity);
  }

  async playSelfExpression(name: string): Promise<void> {
    if (!this.motionPlayer || !this.mounted) return;
    await this.motionPlayer.play(name);
  }

  setLipSyncAmplitude(amplitude: number): void {
    if (!this.lipSyncDriver || !this.mounted) return;
    this.lipSyncDriver.setAmplitude(amplitude);
  }

  resize(width: number, height: number): void {
    if (!this.pixiHandle || !this.model) return;

    this.pixiHandle.app.renderer.resize(width, height);

    // Recalculate model scale and position
    const scale = Math.min(width / this.model.width, height / this.model.height) * 0.95;
    this.model.scale.set(scale);
    this.model.x = width / 2;
    this.model.y = height / 2 - 20;
  }

  getAvailableFeelings(): string[] {
    if (!this.capabilities) return [];
    return Object.entries(this.capabilities.feelings)
      .filter(([_, mapping]) => mapping !== null)
      .map(([name]) => name);
  }

  getAvailableSelfExpressions(): string[] {
    if (!this.capabilities) return [];
    return Object.keys(this.capabilities.selfExpressions);
  }

  unmount(): void {
    if (this.pixiHandle) {
      this.pixiHandle.destroy();
      this.pixiHandle = null;
    }
    this.model = null;
    this.mounted = false;
  }
}
```

### Key porting notes

| Submodule code | Plugin equivalent | What changed |
|----------------|-------------------|-------------|
| `new PIXI.Application({ view: canvas, transparent: true, ... })` | `createPixiApp(container, width, height)` | Extracted to `pixi-setup.ts`, container-based instead of fixed canvas |
| `Live2DModel.from('shizuku/runtime/shizuku.model3.json', ...)` | `Live2DModel.from(\`${modelPath}/shizuku.model3.json\`, ...)` | Path from config, not hardcoded |
| `EXPRESSION_MAP` hardcoded object | `ExpressionManager` reads `capabilities.json` | Data-driven, not code-driven |
| `SELF_EXPRESSION_MAP` hardcoded indices | `MotionPlayer` reads `capabilities.json` | No more index-based lookup |
| `model.internalModel.coreModel.setParameterValueById('PARAM_MOUTH_OPEN_Y', value)` | `LipSyncDriver.setAmplitude(value)` | Smoothing logic extracted, parameter name from config |
| Electron IPC (`ipcRenderer.on(...)`) | HTTP REST API in avatar app | Plugin has no IPC knowledge — it just receives method calls |

## 1.5 `src/pixi-setup.ts` — PixiJS Application Factory

```typescript
import * as PIXI from "pixi.js";

export interface PixiAppHandle {
  app: PIXI.Application;
  destroy(): void;
}

/**
 * Create a transparent PixiJS application inside a container element.
 *
 * Ported from submodule index.html:
 *   new PIXI.Application({ view: canvas, transparent: true, width: 280, height: 400, ... })
 *
 * Changes from submodule:
 *   - Creates its own canvas (no pre-existing <canvas> element required)
 *   - Container-based sizing instead of fixed 280x400
 *   - Returns a handle for clean destruction
 */
export function createPixiApp(
  container: HTMLElement,
  width: number,
  height: number
): PixiAppHandle {
  const app = new PIXI.Application({
    width,
    height,
    backgroundAlpha: 0, // transparent background
    resolution: window.devicePixelRatio || 1,
    autoDensity: true,
  });

  // PixiJS 7 creates its own canvas. Append it to the container.
  container.appendChild(app.view as HTMLCanvasElement);

  return {
    app,
    destroy() {
      app.destroy(true, { children: true, texture: true, baseTexture: true });
    },
  };
}
```

## 1.6 `src/expression-manager.ts` — Feeling-to-Expression Mapping

```typescript
import type { Live2DFeelingMapping } from "./types.js";

/**
 * Maps feeling names to Live2D expression files (.exp3.json) and applies them.
 *
 * Ported from submodule index.html:
 *   const EXPRESSION_MAP = { normal: 'Normal', happy: 'Happy', ... };
 *   function setExpression(name) {
 *     const em = model.internalModel.motionManager.expressionManager;
 *     const idx = em?.definitions?.findIndex(d => d.Name === exprName);
 *     if (idx >= 0) model.expression(idx);
 *   }
 *
 * Changes from submodule:
 *   - Reads mappings from capabilities.json instead of hardcoded EXPRESSION_MAP
 *   - Supports intensity parameter (0-100) for future weighted blending
 *   - Graceful degradation: unknown feelings silently ignored
 */
export class ExpressionManager {
  private feelings: Record<string, Live2DFeelingMapping | null>;
  private model: any = null;

  constructor(feelings: Record<string, Live2DFeelingMapping | null>) {
    this.feelings = feelings;
  }

  /** Bind to a loaded Live2D model. Must be called after model loads. */
  bind(model: any): void {
    this.model = model;
  }

  /**
   * Apply a feeling as an expression on the Live2D model.
   *
   * @param feeling - Feeling name (e.g., "happy", "sad")
   * @param intensity - 0-100 (currently used as boolean: >0 applies, 0 resets to normal)
   *
   * Implementation notes:
   *   - pixi-live2d-display's expression system works by index, not by name
   *   - We find the index by matching the expression Name from model3.json definitions
   *   - intensity is available for future use (Cubism expressions don't natively support
   *     weighted blending, but we can simulate it by interpolating parameter values)
   */
  apply(feeling: string, intensity: number): void {
    if (!this.model) return;

    // If intensity is 0, reset to normal
    if (intensity <= 0) {
      this.applyByName("Normal");
      return;
    }

    const mapping = this.feelings[feeling];
    if (!mapping) return; // Unsupported feeling — silently ignore

    // Extract expression name from file path: "Happy.exp3.json" → "Happy"
    const exprName = mapping.expression.replace(".exp3.json", "");
    this.applyByName(exprName);
  }

  /** Get list of feelings this model supports (non-null mappings). */
  getAvailable(): string[] {
    return Object.entries(this.feelings)
      .filter(([_, mapping]) => mapping !== null)
      .map(([name]) => name);
  }

  /**
   * Apply an expression by its Name field in the model3.json Expressions array.
   *
   * Ported directly from submodule setExpression():
   *   const em = model.internalModel.motionManager.expressionManager;
   *   const idx = em?.definitions?.findIndex(d => d.Name === exprName);
   *   if (idx >= 0) model.expression(idx);
   */
  private applyByName(name: string): void {
    const em = this.model.internalModel?.motionManager?.expressionManager;
    if (!em?.definitions) return;

    const idx = em.definitions.findIndex(
      (d: { Name: string }) => d.Name === name
    );
    if (idx >= 0) {
      this.model.expression(idx);
    }
  }
}
```

## 1.7 `src/motion-player.ts` — Self-Expression Motion Playback

```typescript
import type { Live2DSelfExpressionMapping } from "./types.js";

/**
 * Maps self-expression names to Live2D motion files (.motion3.json) and plays them.
 *
 * Ported from submodule index.html:
 *   const SELF_EXPRESSION_MAP = {
 *     nod: 0, headshake: 1, headtilt: 2, laugh: 3, giggle: 4,
 *     gasp: 5, think: 6, celebrate: 7, sweat: 8, wave: 9, bow: 10, starryeyes: 11,
 *   };
 *   function playSelfExpression(name) {
 *     const idx = SELF_EXPRESSION_MAP[name];
 *     model.motion('SelfExpression', idx, 3);
 *   }
 *
 * Changes from submodule:
 *   - Reads mappings from capabilities.json instead of hardcoded index map
 *   - Resolves motion index dynamically from motion file path
 *   - Returns a Promise that resolves when the motion completes
 *   - Supports motion queuing (one motion at a time, queue the rest)
 */
export class MotionPlayer {
  private selfExpressions: Record<string, Live2DSelfExpressionMapping>;
  private model: any = null;
  private queue: Array<{ name: string; resolve: () => void }> = [];
  private playing = false;

  constructor(selfExpressions: Record<string, Live2DSelfExpressionMapping>) {
    this.selfExpressions = selfExpressions;
  }

  /** Bind to a loaded Live2D model. Must be called after model loads. */
  bind(model: any): void {
    this.model = model;
  }

  /**
   * Play a self-expression motion. Returns a Promise that resolves on completion.
   *
   * If a motion is already playing, the new motion is queued and will play
   * after the current one finishes.
   *
   * @param name - Self-expression name (e.g., "wave", "nod", "celebrate")
   */
  async play(name: string): Promise<void> {
    if (!this.model) return;

    const mapping = this.selfExpressions[name];
    if (!mapping) return; // Unknown expression — silently ignore

    return new Promise<void>((resolve) => {
      this.queue.push({ name, resolve });
      if (!this.playing) {
        this.processQueue();
      }
    });
  }

  /** Get list of available self-expression names. */
  getAvailable(): string[] {
    return Object.keys(this.selfExpressions);
  }

  /**
   * Process the motion queue. Plays one motion at a time.
   *
   * Motion playback uses pixi-live2d-display's motion() method with:
   *   - Group: "SelfExpression" (matches the motion group in model3.json)
   *   - Index: looked up from the model's motion definitions
   *   - Priority: 3 (force — overrides idle and other lower-priority motions)
   *
   * Ported from submodule:
   *   model.motion('SelfExpression', idx, 3)
   *
   * Change: instead of hardcoded indices (nod: 0, headshake: 1, ...),
   * we find the index by matching the motion file path from capabilities.json
   * against the SelfExpression motion definitions in model3.json.
   */
  private async processQueue(): Promise<void> {
    if (this.queue.length === 0) {
      this.playing = false;
      return;
    }

    this.playing = true;
    const { name, resolve } = this.queue.shift()!;

    const mapping = this.selfExpressions[name];
    const idx = this.findMotionIndex(mapping.motion);

    if (idx >= 0) {
      try {
        // Priority 3 = force (overrides idle motions)
        await this.model.motion("SelfExpression", idx, 3);
      } catch (err) {
        // Motion playback failed — log but don't break the queue
        console.error(`Motion "${name}" failed:`, err);
      }
    }

    resolve();
    this.processQueue();
  }

  /**
   * Find the index of a motion file within the SelfExpression motion group.
   *
   * The model3.json Motions.SelfExpression array contains objects like:
   *   { "File": "self-expression/Nodding.motion3.json" }
   *
   * We match against the filename portion of the capabilities.json motion path.
   */
  private findMotionIndex(motionFile: string): number {
    const motionManager = this.model.internalModel?.motionManager;
    if (!motionManager) return -1;

    // Access the motion definitions from the model's settings
    // In Cubism 4, this is stored in model.internalModel.settings.motions
    const motionGroups = this.model.internalModel?.settings?.motions;
    if (!motionGroups?.SelfExpression) return -1;

    const definitions: Array<{ File: string }> = motionGroups.SelfExpression;

    return definitions.findIndex((def) => {
      // Match by filename: "self-expression/Nodding.motion3.json" ends with "Nodding.motion3.json"
      return def.File.endsWith(motionFile);
    });
  }
}
```

## 1.8 `src/lip-sync-driver.ts` — Amplitude-to-Parameter Mapping

```typescript
import type { Live2DLipSyncConfig } from "./types.js";

/**
 * Drives the Live2D model's mouth parameter from a normalized amplitude value.
 *
 * Ported from submodule index.html:
 *   function updateLipSync() {
 *     analyser.getByteTimeDomainData(dataArray);
 *     // ... RMS calculation ...
 *     const target = Math.min(Math.sqrt(gated * 8) * 1.2, 1);
 *     smoothedMouth += (target - smoothedMouth) * (target > smoothedMouth ? 0.8 : 0.3);
 *     model.internalModel.coreModel.setParameterValueById('PARAM_MOUTH_OPEN_Y', smoothedMouth);
 *   }
 *
 * Changes from submodule:
 *   - Does NOT do RMS calculation (that happens in the TTS/audio pipeline)
 *   - Receives pre-computed normalized amplitude (0-1) from setLipSyncAmplitude()
 *   - Smoothing is applied here to avoid jittery mouth movement
 *   - Parameter name comes from capabilities.json, not hardcoded
 *   - Range mapping from capabilities.json (e.g., [0, 1])
 */
export class LipSyncDriver {
  private config: Live2DLipSyncConfig;
  private model: any = null;
  private smoothedValue = 0;

  /** Smoothing factor for rising amplitude (0-1, higher = more responsive) */
  private readonly ATTACK_FACTOR = 0.8;
  /** Smoothing factor for falling amplitude (0-1, lower = slower decay) */
  private readonly RELEASE_FACTOR = 0.3;

  constructor(config: Live2DLipSyncConfig) {
    this.config = config;
  }

  /** Bind to a loaded Live2D model. Must be called after model loads. */
  bind(model: any): void {
    this.model = model;
  }

  /**
   * Set the lip sync amplitude. Called at ~30Hz during TTS playback.
   *
   * Applies asymmetric smoothing:
   *   - Fast attack (0.8): mouth opens quickly when amplitude rises
   *   - Slow release (0.3): mouth closes gradually when amplitude drops
   *
   * This prevents the "machine gun" effect of rapid open/close cycles
   * while keeping the mouth responsive to speech onset.
   *
   * @param amplitude - Normalized 0-1 value (0 = silent/closed, 1 = loud/fully open)
   */
  setAmplitude(amplitude: number): void {
    if (!this.model) return;

    // Clamp input to 0-1
    const clamped = Math.max(0, Math.min(1, amplitude));

    // Asymmetric smoothing (ported from submodule updateLipSync)
    if (clamped > this.smoothedValue) {
      this.smoothedValue += (clamped - this.smoothedValue) * this.ATTACK_FACTOR;
    } else {
      this.smoothedValue += (clamped - this.smoothedValue) * this.RELEASE_FACTOR;
    }

    // Map to configured range
    const [min, max] = this.config.range;
    const mapped = min + this.smoothedValue * (max - min);

    // Apply to Cubism parameter
    // The parameter name in capabilities.json uses the human-readable format
    // (e.g., "ParamMouthOpenY"), but the Cubism SDK uses the internal ID format
    // (e.g., "PARAM_MOUTH_OPEN_Y"). We try both.
    try {
      this.model.internalModel.coreModel.setParameterValueById(
        this.config.parameter,
        mapped
      );
    } catch {
      // Try the SCREAMING_SNAKE_CASE variant
      const snakeCase = this.config.parameter
        .replace(/([A-Z])/g, "_$1")
        .toUpperCase()
        .replace(/^_/, "");
      try {
        this.model.internalModel.coreModel.setParameterValueById(snakeCase, mapped);
      } catch {
        // Parameter not found — silently ignore
      }
    }
  }

  /** Reset mouth to closed position. Call when speech ends. */
  reset(): void {
    this.smoothedValue = 0;
    if (this.model) {
      const [min] = this.config.range;
      try {
        this.model.internalModel.coreModel.setParameterValueById(
          this.config.parameter,
          min
        );
      } catch {
        // Ignore
      }
    }
  }
}
```

## 1.9 `src/index.ts` — Public Export

```typescript
export { Live2DRenderer } from "./live2d-renderer.js";
export type {
  Live2DCapabilities,
  Live2DRendererConfig,
  Live2DFeelingMapping,
  Live2DSelfExpressionMapping,
  Live2DLipSyncConfig,
} from "./types.js";
```

## 1.10 Reference: What to Port from Submodule

This table maps every piece of submodule code to its new location:

| Submodule file | Submodule code | New file | New function/method |
|----------------|---------------|----------|-------------------|
| `index.html` | `new PIXI.Application({ view: canvas, transparent: true, ... })` | `pixi-setup.ts` | `createPixiApp()` |
| `index.html` | `Live2DModel.from('shizuku/runtime/shizuku.model3.json', { motionPreload: ... })` | `live2d-renderer.ts` | `mount()` |
| `index.html` | Scale/position calculation (`Math.min(280/model.width, ...)`) | `live2d-renderer.ts` | `mount()`, `resize()` |
| `index.html` | `model.internalModel.eyeBlink = null` | `live2d-renderer.ts` | `mount()` |
| `index.html` | `model.motion('Idle', 0)` | `live2d-renderer.ts` | `mount()` (start idle) |
| `index.html` | `EXPRESSION_MAP` + `setExpression()` | `expression-manager.ts` | `apply()` |
| `index.html` | `SELF_EXPRESSION_MAP` + `playSelfExpression()` | `motion-player.ts` | `play()` |
| `index.html` | `updateLipSync()` smoothing logic | `lip-sync-driver.ts` | `setAmplitude()` |
| `index.html` | `model.internalModel.coreModel.setParameterValueById('PARAM_MOUTH_OPEN_Y', ...)` | `lip-sync-driver.ts` | `setAmplitude()` |
| `main.js` | `VALID_FEELINGS`, `FEELING_ALIASES` | Removed | Handled by capabilities.json + core FeelingEngine |
| `main.js` | `VALID_ACTIONS`, `ACTION_ALIASES` | Removed | Handled by capabilities.json + avatar app HTTP API |
| `main.js` | Unix socket server | Removed | Replaced by HTTP REST in avatar app (doc 03) |
| `cli.js` | CLI argument parsing + socket client | Removed | Replaced by `scripts/cli.js` using HTTP (doc 05) |

### Code NOT ported (intentionally dropped)

| Submodule code | Why dropped |
|----------------|------------|
| `require('electron')` / `ipcRenderer` | Replaced by Tauri 2 |
| Unix domain socket server (`net.createServer`) | Replaced by HTTP REST API |
| `audioCtx.createMediaElementSource` + `analyser.getByteTimeDomainData` | RMS calculation moves to the audio pipeline; plugin receives pre-computed amplitude |
| `playQueue` / `processPlayQueue` for audio files | Audio queuing moves to the avatar app layer |
| `speechBubble` DOM manipulation | Speech bubble UI moves to the Tauri app frontend |
| `fs.writeFileSync(logFile, ...)` debug logging | Replaced by structured logging in the app |

## 1.11 Tests

### `__tests__/expression-manager.test.ts`

```typescript
import { describe, it, expect, vi, beforeEach } from "vitest";
import { ExpressionManager } from "../src/expression-manager.js";
import type { Live2DFeelingMapping } from "../src/types.js";

// Mock capabilities.json feelings section
const mockFeelings: Record<string, Live2DFeelingMapping | null> = {
  happy: { expression: "Happy.exp3.json" },
  sad: { expression: "Sad.exp3.json" },
  frustrated: { expression: "Frustrated.exp3.json" },
  calm: null, // Not supported by this model
  curious: { expression: "Curious.exp3.json" },
};

// Mock Live2D model with expression definitions matching model3.json
function createMockModel() {
  const expressionFn = vi.fn();
  return {
    expression: expressionFn,
    internalModel: {
      motionManager: {
        expressionManager: {
          definitions: [
            { Name: "Normal" },
            { Name: "Happy" },
            { Name: "Sad" },
            { Name: "Frustrated" },
            { Name: "Curious" },
          ],
        },
      },
    },
    _expressionFn: expressionFn,
  };
}

describe("ExpressionManager", () => {
  let manager: ExpressionManager;
  let mockModel: ReturnType<typeof createMockModel>;

  beforeEach(() => {
    manager = new ExpressionManager(mockFeelings);
    mockModel = createMockModel();
    manager.bind(mockModel);
  });

  describe("getAvailable()", () => {
    it("returns only non-null feelings", () => {
      const available = manager.getAvailable();
      expect(available).toEqual(["happy", "sad", "frustrated", "curious"]);
      expect(available).not.toContain("calm");
    });
  });

  describe("apply()", () => {
    it("applies happy expression by finding index in definitions", () => {
      manager.apply("happy", 80);
      // "Happy" is at index 1 in the definitions array
      expect(mockModel._expressionFn).toHaveBeenCalledWith(1);
    });

    it("applies sad expression", () => {
      manager.apply("sad", 60);
      // "Sad" is at index 2
      expect(mockModel._expressionFn).toHaveBeenCalledWith(2);
    });

    it("resets to Normal when intensity is 0", () => {
      manager.apply("happy", 0);
      // "Normal" is at index 0
      expect(mockModel._expressionFn).toHaveBeenCalledWith(0);
    });

    it("silently ignores unsupported feelings (null in capabilities)", () => {
      manager.apply("calm", 80);
      expect(mockModel._expressionFn).not.toHaveBeenCalled();
    });

    it("silently ignores unknown feelings (not in capabilities at all)", () => {
      manager.apply("nonexistent", 80);
      expect(mockModel._expressionFn).not.toHaveBeenCalled();
    });
  });

  describe("without model bound", () => {
    it("does not throw when apply is called before bind", () => {
      const unbound = new ExpressionManager(mockFeelings);
      expect(() => unbound.apply("happy", 80)).not.toThrow();
    });
  });
});
```

### `__tests__/motion-player.test.ts`

```typescript
import { describe, it, expect, vi, beforeEach } from "vitest";
import { MotionPlayer } from "../src/motion-player.js";
import type { Live2DSelfExpressionMapping } from "../src/types.js";

// Mock capabilities.json selfExpressions section
const mockSelfExpressions: Record<string, Live2DSelfExpressionMapping> = {
  wave: { motion: "Waving.motion3.json", group: "social" },
  nod: { motion: "Nodding.motion3.json", group: "social" },
  laugh: { motion: "Laughing.motion3.json", group: "emotional" },
  celebrate: { motion: "Celebrating.motion3.json", group: "combo" },
};

// Mock Live2D model with motion definitions matching model3.json
function createMockModel() {
  const motionFn = vi.fn().mockResolvedValue(true);
  return {
    motion: motionFn,
    internalModel: {
      motionManager: {},
      settings: {
        motions: {
          SelfExpression: [
            { File: "self-expression/Nodding.motion3.json" },
            { File: "self-expression/HeadShake.motion3.json" },
            { File: "self-expression/Laughing.motion3.json" },
            { File: "self-expression/Celebrating.motion3.json" },
            { File: "self-expression/Waving.motion3.json" },
          ],
        },
      },
    },
    _motionFn: motionFn,
  };
}

describe("MotionPlayer", () => {
  let player: MotionPlayer;
  let mockModel: ReturnType<typeof createMockModel>;

  beforeEach(() => {
    player = new MotionPlayer(mockSelfExpressions);
    mockModel = createMockModel();
    player.bind(mockModel);
  });

  describe("getAvailable()", () => {
    it("returns all self-expression names", () => {
      const available = player.getAvailable();
      expect(available).toEqual(["wave", "nod", "laugh", "celebrate"]);
    });
  });

  describe("play()", () => {
    it("plays wave motion by finding index from file path", async () => {
      await player.play("wave");
      // "Waving.motion3.json" matches index 4 in SelfExpression group
      expect(mockModel._motionFn).toHaveBeenCalledWith("SelfExpression", 4, 3);
    });

    it("plays nod motion", async () => {
      await player.play("nod");
      // "Nodding.motion3.json" matches index 0
      expect(mockModel._motionFn).toHaveBeenCalledWith("SelfExpression", 0, 3);
    });

    it("silently ignores unknown expressions", async () => {
      await player.play("nonexistent");
      expect(mockModel._motionFn).not.toHaveBeenCalled();
    });

    it("resolves the promise when motion completes", async () => {
      const promise = player.play("wave");
      await expect(promise).resolves.toBeUndefined();
    });
  });

  describe("queuing", () => {
    it("plays motions sequentially when queued", async () => {
      const callOrder: string[] = [];

      // Make motion() resolve after a microtask to simulate async playback
      mockModel._motionFn.mockImplementation(
        (_group: string, idx: number, _priority: number) => {
          callOrder.push(`motion-${idx}`);
          return Promise.resolve(true);
        }
      );

      // Queue two motions simultaneously
      const p1 = player.play("wave");
      const p2 = player.play("nod");

      await Promise.all([p1, p2]);

      // Both should have played
      expect(callOrder).toHaveLength(2);
      // Wave first (index 4), then nod (index 0)
      expect(callOrder[0]).toBe("motion-4");
      expect(callOrder[1]).toBe("motion-0");
    });
  });

  describe("without model bound", () => {
    it("does not throw when play is called before bind", async () => {
      const unbound = new MotionPlayer(mockSelfExpressions);
      await expect(unbound.play("wave")).resolves.toBeUndefined();
    });
  });
});
```

## 1.12 `capabilities.json` for Shizuku

This file lives at `models/live2d/shizuku/capabilities.json` and is created in [doc 04 (model setup)](04-model-setup.md). Shown here for reference since the plugin reads it at initialization.

```json
{
  "renderer": "live2d",
  "model": "shizuku",
  "version": "1.0",
  "feelings": {
    "happy":      { "expression": "Happy.exp3.json" },
    "sad":        { "expression": "Sad.exp3.json" },
    "frustrated": { "expression": "Frustrated.exp3.json" },
    "curious":    { "expression": "Curious.exp3.json" },
    "proud":      { "expression": "Proud.exp3.json" },
    "anxious":    { "expression": "Anxious.exp3.json" },
    "excited":    { "expression": "Excited.exp3.json" },
    "calm":       { "expression": "Calm.exp3.json" },
    "bored":      { "expression": "Bored.exp3.json" },
    "guilty":     { "expression": "Guilty.exp3.json" },
    "angry":      { "expression": "Angry.exp3.json" },
    "blushing":   { "expression": "Blushing.exp3.json" },
    "surprised":  { "expression": "Surprised.exp3.json" },
    "relieved":   null
  },
  "selfExpressions": {
    "nod":        { "motion": "Nodding.motion3.json",      "group": "social" },
    "headshake":  { "motion": "HeadShake.motion3.json",    "group": "social" },
    "headtilt":   { "motion": "HeadTilt.motion3.json",     "group": "social" },
    "wave":       { "motion": "Waving.motion3.json",       "group": "social" },
    "bow":        { "motion": "Bowing.motion3.json",       "group": "social" },
    "laugh":      { "motion": "Laughing.motion3.json",     "group": "emotional" },
    "giggle":     { "motion": "Giggling.motion3.json",     "group": "emotional" },
    "gasp":       { "motion": "SurprisedGasp.motion3.json","group": "reaction" },
    "think":      { "motion": "Thinking.motion3.json",     "group": "reaction" },
    "celebrate":  { "motion": "Celebrating.motion3.json",  "group": "combo" },
    "sweat":      { "motion": "SweatDrop.motion3.json",    "group": "reaction" },
    "starryeyes": { "motion": "StarryEyes.motion3.json",   "group": "reaction" }
  },
  "lipSync": {
    "method": "rms",
    "parameter": "ParamMouthOpenY",
    "range": [0, 1]
  }
}
```

Note: The Shizuku model supports 13 of 14 universal feelings (`relieved` is null — no expression file exists for it). All 12 self-expressions from the submodule are preserved.

## 1.13 Verification

After implementing this step, verify:

```bash
# 1. Package compiles
cd packages/plugin-avatar/live2d
npm run build
# Expected: dist/ directory created with .js and .d.ts files, no TypeScript errors

# 2. Tests pass
npm run test
# Expected: All expression-manager and motion-player tests pass

# 3. Exports are correct
node -e "import('@vibe-ai-partner/plugin-avatar-live2d').then(m => console.log(Object.keys(m)))"
# Expected: ['Live2DRenderer']

# 4. Interface compliance (build-time check)
# The TypeScript compiler will fail if Live2DRenderer doesn't satisfy IAvatarRenderer.
# No runtime check needed — this is enforced by `implements IAvatarRenderer`.

# 5. capabilities.json query works (after model setup in doc 04)
node -e "
  import { Live2DRenderer } from '@vibe-ai-partner/plugin-avatar-live2d';
  const r = new Live2DRenderer();
  await r.initialize({ modelPath: 'models/live2d/shizuku' });
  console.log('Feelings:', r.getAvailableFeelings());
  console.log('Expressions:', r.getAvailableSelfExpressions());
"
# Expected:
#   Feelings: ['happy','sad','frustrated','curious','proud','anxious','excited','calm','bored','guilty','angry','blushing','surprised']
#   Expressions: ['nod','headshake','headtilt','wave','bow','laugh','giggle','gasp','think','celebrate','sweat','starryeyes']
```
