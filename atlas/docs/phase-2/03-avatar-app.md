# Avatar App Implementation

Tauri 2 desktop app. Transparent, always-on-top window that renders the avatar. Connects to the TTS server via WebSocket for amplitude, feelings, and actions. No audio handling -- the avatar app only receives events and drives the renderer.

---

## Directory Structure

```
apps/avatar-app/
├── package.json
├── tsconfig.json
├── vite.config.ts
├── index.html
├── src/
│   ├── main.ts                     # Entry, bootstrap app
│   ├── app.ts                      # Plugin orchestration, event wiring
│   ├── renderer-host.ts            # Mount/unmount avatar renderer
│   ├── ws-client.ts                # WebSocket client to TTS server
│   ├── event-loop.ts               # requestAnimationFrame loop
│   └── ui/
│       ├── speech-bubble.ts        # Overlay for spoken text
│       └── context-menu.ts         # Right-click menu UI
└── src-tauri/
    ├── Cargo.toml
    ├── tauri.conf.json
    └── src/
        ├── main.rs                 # Tauri entry point
        └── lib.rs                  # Window management, tray, commands
```

---

## package.json

```json
{
  "name": "@vibe-ai-partner/avatar-app",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "tauri": "tauri"
  },
  "dependencies": {
    "@vibe-ai-partner/core": "workspace:*",
    "@vibe-ai-partner/shared": "workspace:*",
    "@vibe-ai-partner/plugin-avatar-live2d": "workspace:*",
    "@tauri-apps/api": "^2.0.0",
    "@tauri-apps/plugin-shell": "^2.0.0"
  },
  "devDependencies": {
    "@tauri-apps/cli": "^2.0.0",
    "typescript": "^5.6.0",
    "vite": "^6.0.0"
  }
}
```

---

## tsconfig.json

```json
{
  "extends": "../../tsconfig.base.json",
  "compilerOptions": {
    "outDir": "dist",
    "rootDir": "src",
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "moduleResolution": "bundler",
    "module": "ESNext",
    "target": "ES2022",
    "strict": true,
    "noEmit": true
  },
  "include": ["src"],
  "references": [
    { "path": "../../packages/core" },
    { "path": "../../packages/shared" }
  ]
}
```

---

## vite.config.ts

```ts
import { defineConfig } from "vite";

export default defineConfig({
  // Prevent Vite from obscuring Rust errors
  clearScreen: false,

  // Tauri expects a fixed port for dev
  server: {
    port: 1420,
    strictPort: true,
  },

  // Env prefix for Tauri
  envPrefix: ["VITE_", "TAURI_"],

  build: {
    // Tauri uses Chromium on Windows and WebKit on macOS/Linux
    target: process.env.TAURI_PLATFORM === "windows" ? "chrome105" : "safari15",
    minify: !process.env.TAURI_DEBUG ? "esbuild" : false,
    sourcemap: !!process.env.TAURI_DEBUG,
    outDir: "dist",
  },
});
```

---

## index.html

Minimal HTML -- just the mount point for the avatar renderer. The `<canvas>` or DOM tree is created by the renderer plugin at runtime.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Vibe AI Partner</title>
  <style>
    /* Transparent background — Tauri handles window transparency */
    * { margin: 0; padding: 0; box-sizing: border-box; }
    html, body {
      width: 100%;
      height: 100%;
      overflow: hidden;
      background: transparent;
    }
    #avatar-container {
      width: 100%;
      height: 100%;
      position: relative;
    }
    /* Speech bubble overlay — positioned above the avatar */
    #speech-bubble {
      display: none;
      position: absolute;
      top: 10px;
      left: 50%;
      transform: translateX(-50%);
      max-width: 80%;
      padding: 12px 16px;
      background: rgba(0, 0, 0, 0.75);
      color: #fff;
      border-radius: 12px;
      font-family: system-ui, sans-serif;
      font-size: 14px;
      line-height: 1.4;
      z-index: 100;
      pointer-events: none;
    }
    #speech-bubble.visible { display: block; }
  </style>
</head>
<body>
  <div id="avatar-container"></div>
  <div id="speech-bubble"></div>
  <script type="module" src="/src/main.ts"></script>
</body>
</html>
```

---

## main.ts

Entry point. Reads config, determines which renderer plugin to load, creates the `App` instance.

```ts
/**
 * Avatar app entry point.
 *
 * Bootstrap sequence:
 *   1. Read config (.env via Tauri)
 *   2. Determine renderer plugin (live2d, vrm, etc.)
 *   3. Create App instance (orchestrates everything)
 *   4. Start animation loop
 */

import { App } from "./app.js";

async function main(): Promise<void> {
  // Config comes from .env via Tauri env vars (VITE_ prefix)
  const config = {
    ttsServerUrl: import.meta.env.VITE_TTS_SERVER_URL ?? "http://localhost:5111",
    wsStatusUrl: import.meta.env.VITE_WS_STATUS_URL ?? "ws://localhost:5111/ws/status",
    wsAudioUrl: import.meta.env.VITE_WS_AUDIO_URL ?? "ws://localhost:5111/ws/audio",
    renderer: import.meta.env.VITE_AVATAR_RENDERER ?? "live2d",
    model: import.meta.env.VITE_AVATAR_MODEL ?? "shizuku",
  };

  const container = document.getElementById("avatar-container");
  if (!container) {
    throw new Error("Missing #avatar-container element");
  }

  const app = new App(config, container);
  await app.start();
}

main().catch((err) => {
  console.error("Fatal: avatar app failed to start", err);
});
```

---

## app.ts

Central orchestration. Loads the renderer plugin, connects WebSocket, wires events.

```ts
/**
 * App — plugin orchestration and event wiring.
 *
 * Responsibilities:
 *   - Load and mount the active avatar renderer
 *   - Connect WebSocket to TTS server
 *   - Wire WebSocket messages to renderer methods:
 *       amplitude -> renderer.setLipSyncAmplitude()
 *       feeling   -> renderer.setFeeling()
 *       action    -> renderer.playSelfExpression()
 *   - Run the animation loop
 */

import type { IAvatarRenderer } from "@vibe-ai-partner/core";
import type {
  WSStatusMessage,
  WSAmplitude,
  WSFeelingUpdate,
  WSActionUpdate,
} from "@vibe-ai-partner/shared";

import { RendererHost } from "./renderer-host.js";
import { WSClient } from "./ws-client.js";
import { EventLoop } from "./event-loop.js";
import { SpeechBubble } from "./ui/speech-bubble.js";
import { ContextMenu } from "./ui/context-menu.js";

export interface AppConfig {
  ttsServerUrl: string;
  wsStatusUrl: string;
  wsAudioUrl: string;
  renderer: string;
  model: string;
}

export class App {
  private rendererHost: RendererHost;
  private wsClient: WSClient;
  private eventLoop: EventLoop;
  private speechBubble: SpeechBubble;
  private contextMenu: ContextMenu;

  constructor(
    private config: AppConfig,
    private container: HTMLElement,
  ) {
    this.rendererHost = new RendererHost(container);
    this.wsClient = new WSClient(config.wsStatusUrl);
    this.eventLoop = new EventLoop();
    this.speechBubble = new SpeechBubble();
    this.contextMenu = new ContextMenu(config.ttsServerUrl);
  }

  async start(): Promise<void> {
    // 1. Load renderer plugin dynamically based on config
    const renderer = await this.loadRenderer(this.config.renderer);

    // 2. Mount renderer (creates canvas, loads model)
    await this.rendererHost.mount(renderer);

    // 3. Connect WebSocket to TTS server
    this.wsClient.connect();

    // 4. Wire WebSocket events to renderer
    this.wireEvents(renderer);

    // 5. Start animation loop
    this.eventLoop.start((deltaTime) => {
      renderer.update(deltaTime);
    });

    // 6. Initialize context menu
    this.contextMenu.attach(this.container);
  }

  async stop(): Promise<void> {
    this.eventLoop.stop();
    this.wsClient.disconnect();
    this.rendererHost.unmount();
    this.contextMenu.detach();
  }

  private async loadRenderer(rendererId: string): Promise<IAvatarRenderer> {
    // Dynamic import based on renderer selection.
    // Each plugin-avatar package exports a class implementing IAvatarRenderer.
    switch (rendererId) {
      case "live2d": {
        const { Live2DRenderer } = await import("@vibe-ai-partner/plugin-avatar-live2d");
        return new Live2DRenderer();
      }
      // Future: case "vrm", case "threejs", etc.
      default:
        throw new Error(`Unknown renderer: ${rendererId}`);
    }
  }

  private wireEvents(renderer: IAvatarRenderer): void {
    this.wsClient.onMessage((msg: WSStatusMessage) => {
      switch (msg.type) {
        case "amplitude": {
          const amp = msg as WSAmplitude;
          renderer.setLipSyncAmplitude(amp.value);
          break;
        }
        case "feeling": {
          const feel = msg as WSFeelingUpdate;
          // Use intensity 80 as default when set via command
          // (hooks provide fine-grained intensity via /api/state)
          renderer.setFeeling(feel.name, 80);
          break;
        }
        case "action": {
          const act = msg as WSActionUpdate;
          renderer.playSelfExpression(act.name);
          break;
        }
        case "state": {
          // State updates (mode: "speaking" / "idle") — drive speech bubble
          if ("mode" in msg) {
            if (msg.mode === "speaking") {
              this.speechBubble.show();
            } else {
              this.speechBubble.hide();
            }
          }
          break;
        }
      }
    });
  }
}
```

---

## renderer-host.ts

Manages the active avatar plugin lifecycle: mount, resize, unmount.

```ts
/**
 * RendererHost — mount/unmount lifecycle for the active avatar plugin.
 *
 * Handles:
 *   - Mounting renderer into the container element
 *   - Window resize events -> renderer.resize()
 *   - Clean unmount (releases WebGL context, DOM elements)
 */

import type { IAvatarRenderer } from "@vibe-ai-partner/core";

export class RendererHost {
  private renderer: IAvatarRenderer | null = null;
  private resizeObserver: ResizeObserver | null = null;

  constructor(private container: HTMLElement) {}

  async mount(renderer: IAvatarRenderer): Promise<void> {
    // Initialize plugin (loads model data, prepares WebGL)
    await renderer.initialize({});

    // Mount into container (creates canvas)
    await renderer.mount(this.container);

    this.renderer = renderer;

    // Observe container size changes
    this.resizeObserver = new ResizeObserver((entries) => {
      for (const entry of entries) {
        const { width, height } = entry.contentRect;
        this.renderer?.resize(width, height);
      }
    });
    this.resizeObserver.observe(this.container);
  }

  unmount(): void {
    this.resizeObserver?.disconnect();
    this.resizeObserver = null;

    if (this.renderer) {
      this.renderer.unmount();
      this.renderer = null;
    }
  }

  getRenderer(): IAvatarRenderer | null {
    return this.renderer;
  }
}
```

---

## ws-client.ts

WebSocket client with auto-reconnect. Connects to `ws://localhost:5111/ws/status`, parses typed messages, calls registered handler.

```ts
/**
 * WSClient — WebSocket connection to the TTS server /ws/status channel.
 *
 * Features:
 *   - Auto-reconnect on disconnect (exponential backoff, max 30s)
 *   - Parses JSON messages as WSStatusMessage union type
 *   - Single onMessage callback (App wires this to the renderer)
 *
 * Message types received (from shared/protocol.ts):
 *   - WSStateUpdate:   { type: "state", mode: string, mood: string }
 *   - WSAmplitude:     { type: "amplitude", value: number, timestamp: number }
 *   - WSFeelingUpdate: { type: "feeling", name: FeelingName }
 *   - WSActionUpdate:  { type: "action", name: string }
 */

import type { WSStatusMessage } from "@vibe-ai-partner/shared";

type MessageHandler = (msg: WSStatusMessage) => void;

const INITIAL_RECONNECT_MS = 1000;
const MAX_RECONNECT_MS = 30_000;

export class WSClient {
  private ws: WebSocket | null = null;
  private handler: MessageHandler | null = null;
  private reconnectMs = INITIAL_RECONNECT_MS;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private intentionalClose = false;

  constructor(private url: string) {}

  connect(): void {
    this.intentionalClose = false;
    this.tryConnect();
  }

  disconnect(): void {
    this.intentionalClose = true;
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  onMessage(handler: MessageHandler): void {
    this.handler = handler;
  }

  private tryConnect(): void {
    const ws = new WebSocket(this.url);

    ws.onopen = () => {
      console.log(`[WSClient] Connected to ${this.url}`);
      this.reconnectMs = INITIAL_RECONNECT_MS;
    };

    ws.onmessage = (event: MessageEvent) => {
      try {
        const msg: WSStatusMessage = JSON.parse(event.data);
        this.handler?.(msg);
      } catch {
        // Ignore unparseable messages
      }
    };

    ws.onclose = () => {
      this.ws = null;
      if (!this.intentionalClose) {
        this.scheduleReconnect();
      }
    };

    ws.onerror = () => {
      // onerror is always followed by onclose — reconnect handled there
      ws.close();
    };

    this.ws = ws;
  }

  private scheduleReconnect(): void {
    console.log(`[WSClient] Reconnecting in ${this.reconnectMs}ms...`);
    this.reconnectTimer = setTimeout(() => {
      this.tryConnect();
    }, this.reconnectMs);

    // Exponential backoff with jitter
    this.reconnectMs = Math.min(
      this.reconnectMs * 2 + Math.random() * 500,
      MAX_RECONNECT_MS,
    );
  }
}
```

---

## event-loop.ts

`requestAnimationFrame` loop that drives `renderer.update(deltaTime)`.

```ts
/**
 * EventLoop — requestAnimationFrame loop with deltaTime calculation.
 *
 * Responsibilities:
 *   - Call callback(deltaTime) every frame
 *   - Calculate deltaTime in seconds (clamped to prevent spiral of death)
 *   - Track FPS for diagnostics
 */

type FrameCallback = (deltaTime: number) => void;

// Clamp deltaTime to prevent physics explosions after tab switch
const MAX_DELTA = 1 / 15; // ~66ms (15 FPS minimum)

export class EventLoop {
  private running = false;
  private rafId: number | null = null;
  private lastTime = 0;
  private fps = 0;
  private frameCount = 0;
  private fpsTime = 0;

  start(callback: FrameCallback): void {
    if (this.running) return;

    this.running = true;
    this.lastTime = performance.now();
    this.fpsTime = this.lastTime;
    this.frameCount = 0;

    const loop = (now: number): void => {
      if (!this.running) return;

      // DeltaTime in seconds, clamped
      const rawDelta = (now - this.lastTime) / 1000;
      const deltaTime = Math.min(rawDelta, MAX_DELTA);
      this.lastTime = now;

      // FPS tracking (update once per second)
      this.frameCount++;
      if (now - this.fpsTime >= 1000) {
        this.fps = this.frameCount;
        this.frameCount = 0;
        this.fpsTime = now;
      }

      callback(deltaTime);

      this.rafId = requestAnimationFrame(loop);
    };

    this.rafId = requestAnimationFrame(loop);
  }

  stop(): void {
    this.running = false;
    if (this.rafId !== null) {
      cancelAnimationFrame(this.rafId);
      this.rafId = null;
    }
  }

  getFps(): number {
    return this.fps;
  }
}
```

---

## ui/speech-bubble.ts

Overlay that shows when TTS is speaking, hides when done.

```ts
/**
 * SpeechBubble — overlay div that appears during TTS playback.
 *
 * Controlled by WSStateUpdate messages:
 *   mode: "speaking" -> show
 *   mode: "idle"     -> hide
 *
 * The bubble element is defined in index.html (#speech-bubble).
 * This class just toggles the "visible" CSS class.
 */

export class SpeechBubble {
  private el: HTMLElement;

  constructor() {
    this.el = document.getElementById("speech-bubble")!;
  }

  show(text?: string): void {
    if (text) {
      this.el.textContent = text;
    }
    this.el.classList.add("visible");
  }

  hide(): void {
    this.el.classList.remove("visible");
  }
}
```

---

## ui/context-menu.ts

Right-click context menu. Built as an HTML/TS overlay (not native Rust menu) for flexibility -- supports submenus, text input, and dynamic content.

```ts
/**
 * ContextMenu — right-click overlay with feelings, actions, speak, settings.
 *
 * Uses HTML/TS overlay rather than Tauri native menu because:
 *   - Dynamic submenus (feelings list, actions list come from server)
 *   - Text input for "Speak..." command
 *   - Styled consistently across platforms
 *
 * All actions route through the TTS server REST API:
 *   - Feelings  -> POST /api/feeling  { name: "happy" }
 *   - Actions   -> POST /api/action   { name: "wave" }
 *   - Speak     -> POST /api/speak    { text: "..." }
 */

const FEELINGS = [
  "happy", "sad", "frustrated", "curious", "proud",
  "anxious", "excited", "calm", "bored", "guilty",
  "angry", "blushing", "surprised", "relieved",
] as const;

const ACTIONS = [
  "celebrate", "cry", "sigh", "head-tilt", "fist-pump",
  "tremble", "bounce", "nod", "yawn", "facepalm",
  "puff-cheeks", "cover-face", "gasp",
] as const;

export class ContextMenu {
  private overlay: HTMLElement | null = null;
  private container: HTMLElement | null = null;
  private boundHandler: ((e: MouseEvent) => void) | null = null;

  constructor(private serverUrl: string) {}

  attach(container: HTMLElement): void {
    this.container = container;
    this.boundHandler = (e: MouseEvent) => {
      e.preventDefault();
      this.showAt(e.clientX, e.clientY);
    };
    container.addEventListener("contextmenu", this.boundHandler);

    // Close on click outside
    document.addEventListener("click", () => this.hide());
  }

  detach(): void {
    if (this.container && this.boundHandler) {
      this.container.removeEventListener("contextmenu", this.boundHandler);
    }
    this.hide();
  }

  private showAt(x: number, y: number): void {
    this.hide(); // Remove previous

    const menu = document.createElement("div");
    menu.className = "vibe-context-menu";
    menu.style.cssText = `
      position: fixed; left: ${x}px; top: ${y}px; z-index: 1000;
      background: rgba(30, 30, 30, 0.95); border: 1px solid rgba(255,255,255,0.1);
      border-radius: 8px; padding: 4px 0; min-width: 180px;
      font-family: system-ui, sans-serif; font-size: 13px; color: #eee;
      backdrop-filter: blur(10px);
    `;

    // ─── Feelings submenu
    const feelingsItem = this.createSubmenu("Feelings", FEELINGS.map((f) => ({
      label: f.charAt(0).toUpperCase() + f.slice(1),
      action: () => this.postToServer("/api/feeling", { name: f }),
    })));
    menu.appendChild(feelingsItem);

    // ─── Actions submenu
    const actionsItem = this.createSubmenu("Actions", ACTIONS.map((a) => ({
      label: a,
      action: () => this.postToServer("/api/action", { name: a }),
    })));
    menu.appendChild(actionsItem);

    // ─── Separator
    menu.appendChild(this.createSeparator());

    // ─── Speak input
    const speakItem = this.createMenuItem("Speak...", () => {
      const text = prompt("Enter text to speak:");
      if (text) {
        this.postToServer("/api/speak", { text });
      }
    });
    menu.appendChild(speakItem);

    // ─── Separator
    menu.appendChild(this.createSeparator());

    // ─── Settings
    const settingsItem = this.createMenuItem("Settings", () => {
      // TODO: Open settings dialog (Phase 3)
      console.log("Settings not yet implemented");
    });
    menu.appendChild(settingsItem);

    document.body.appendChild(menu);
    this.overlay = menu;

    // Keep menu within viewport
    const rect = menu.getBoundingClientRect();
    if (rect.right > window.innerWidth) {
      menu.style.left = `${window.innerWidth - rect.width - 8}px`;
    }
    if (rect.bottom > window.innerHeight) {
      menu.style.top = `${window.innerHeight - rect.height - 8}px`;
    }
  }

  private hide(): void {
    if (this.overlay) {
      this.overlay.remove();
      this.overlay = null;
    }
  }

  private createMenuItem(label: string, action: () => void): HTMLElement {
    const item = document.createElement("div");
    item.textContent = label;
    item.style.cssText = `padding: 6px 16px; cursor: pointer;`;
    item.addEventListener("mouseenter", () => { item.style.background = "rgba(255,255,255,0.1)"; });
    item.addEventListener("mouseleave", () => { item.style.background = "transparent"; });
    item.addEventListener("click", (e) => {
      e.stopPropagation();
      action();
      this.hide();
    });
    return item;
  }

  private createSubmenu(label: string, items: { label: string; action: () => void }[]): HTMLElement {
    const wrapper = document.createElement("div");
    wrapper.style.cssText = "position: relative;";

    const trigger = document.createElement("div");
    trigger.textContent = `${label} >`;
    trigger.style.cssText = `padding: 6px 16px; cursor: pointer;`;
    trigger.addEventListener("mouseenter", () => { trigger.style.background = "rgba(255,255,255,0.1)"; });
    trigger.addEventListener("mouseleave", () => { trigger.style.background = "transparent"; });

    const sub = document.createElement("div");
    sub.style.cssText = `
      display: none; position: absolute; left: 100%; top: 0;
      background: rgba(30, 30, 30, 0.95); border: 1px solid rgba(255,255,255,0.1);
      border-radius: 8px; padding: 4px 0; min-width: 140px;
      backdrop-filter: blur(10px);
    `;

    for (const item of items) {
      sub.appendChild(this.createMenuItem(item.label, item.action));
    }

    wrapper.addEventListener("mouseenter", () => { sub.style.display = "block"; });
    wrapper.addEventListener("mouseleave", () => { sub.style.display = "none"; });

    wrapper.appendChild(trigger);
    wrapper.appendChild(sub);
    return wrapper;
  }

  private createSeparator(): HTMLElement {
    const sep = document.createElement("div");
    sep.style.cssText = "height: 1px; background: rgba(255,255,255,0.1); margin: 4px 0;";
    return sep;
  }

  private async postToServer(path: string, body: Record<string, unknown>): Promise<void> {
    try {
      await fetch(`${this.serverUrl}${path}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
    } catch (err) {
      console.error(`[ContextMenu] Failed to POST ${path}:`, err);
    }
  }
}
```

---

## Rust Backend (src-tauri/)

### Cargo.toml

```toml
[package]
name = "vibe-avatar-app"
version = "0.1.0"
edition = "2021"

[dependencies]
tauri = { version = "2", features = ["tray-icon"] }
tauri-plugin-shell = "2"
serde = { version = "1", features = ["derive"] }
serde_json = "1"

[build-dependencies]
tauri-build = { version = "2", features = [] }

[lib]
crate-type = ["cdylib", "rlib"]
name = "vibe_avatar_app"
```

### tauri.conf.json

Exact config for transparent, always-on-top, undecorated window with WebGL support.

```json
{
  "$schema": "https://raw.githubusercontent.com/nicedoctor/tauri/v2/crates/tauri-cli/config.schema.json",
  "productName": "Vibe AI Partner",
  "version": "0.1.0",
  "identifier": "com.vibe-ai-partner.avatar",
  "build": {
    "frontendDist": "../dist",
    "devUrl": "http://localhost:1420",
    "beforeDevCommand": "npm run dev",
    "beforeBuildCommand": "npm run build"
  },
  "app": {
    "withGlobalTauri": false,
    "windows": [
      {
        "title": "Vibe AI Partner",
        "label": "main",
        "width": 400,
        "height": 600,
        "x": null,
        "y": null,
        "resizable": true,
        "transparent": true,
        "decorations": false,
        "alwaysOnTop": true,
        "skipTaskbar": false,
        "shadow": false
      }
    ],
    "trayIcon": {
      "iconPath": "icons/icon.png",
      "iconAsTemplate": true,
      "tooltip": "Vibe AI Partner"
    },
    "security": {
      "csp": null
    }
  },
  "bundle": {
    "active": true,
    "targets": "all",
    "icon": [
      "icons/32x32.png",
      "icons/128x128.png",
      "icons/128x128@2x.png",
      "icons/icon.icns",
      "icons/icon.ico"
    ]
  }
}
```

Key settings:
- **`transparent: true`** -- window background is transparent, avatar floats on screen
- **`decorations: false`** -- no title bar, close/minimize buttons
- **`alwaysOnTop: true`** -- avatar stays above other windows
- **`shadow: false`** -- no window shadow (clean transparent look)
- **`csp: null`** -- no Content Security Policy restrictions (needed for WebGL + WebSocket to localhost)

### main.rs

```rust
// Tauri entry point — generated by `cargo tauri init`
// Delegates to lib.rs

#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

fn main() {
    vibe_avatar_app::run();
}
```

### lib.rs

Window management, system tray, and Tauri commands.

```rust
use tauri::{
    AppHandle, Manager,
    tray::{MouseButton, MouseButtonState, TrayIconBuilder, TrayIconEvent},
};

/// Tauri command: toggle window visibility (called from tray)
#[tauri::command]
fn toggle_visibility(app: AppHandle) {
    if let Some(window) = app.get_webview_window("main") {
        if window.is_visible().unwrap_or(false) {
            let _ = window.hide();
        } else {
            let _ = window.show();
            let _ = window.set_focus();
        }
    }
}

/// Tauri command: move the window (for custom title bar drag)
#[tauri::command]
fn drag_window(app: AppHandle) {
    if let Some(window) = app.get_webview_window("main") {
        let _ = window.start_dragging();
    }
}

pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .setup(|app| {
            // System tray — click to toggle visibility
            let _tray = TrayIconBuilder::new()
                .tooltip("Vibe AI Partner")
                .on_tray_icon_event(|tray, event| {
                    if let TrayIconEvent::Click {
                        button: MouseButton::Left,
                        button_state: MouseButtonState::Up,
                        ..
                    } = event
                    {
                        let app = tray.app_handle();
                        if let Some(window) = app.get_webview_window("main") {
                            let _ = window.show();
                            let _ = window.set_focus();
                        }
                    }
                })
                .build(app)?;

            Ok(())
        })
        .invoke_handler(tauri::generate_handler![toggle_visibility, drag_window])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

**Note on context menu**: The right-click menu is implemented in TypeScript (`ui/context-menu.ts`) rather than Rust native menu because:
- Dynamic content (feelings/actions lists can change)
- Text input for "Speak..." command
- Consistent styling across platforms
- Easier to iterate on during development

The Rust side provides `drag_window` and `toggle_visibility` commands. The system tray uses Tauri 2's `TrayIconBuilder`.

---

## Verification

After setup:

```bash
# From project root — start TTS server first
cd apps/tts-server && source .venv/bin/activate && python -m uvicorn vibe_tts.server:app --port 5111 &

# Start avatar app in dev mode
npm run dev -w apps/avatar-app

# Expected:
# 1. Vite dev server starts on port 1420
# 2. Tauri window opens — transparent, no decorations, always on top
# 3. Shizuku Live2D model renders in the window
# 4. Right-click shows context menu with Feelings, Actions, Speak
# 5. Selecting "Happy" from Feelings -> POST /api/feeling -> WebSocket broadcasts
#    -> avatar expression changes
# 6. System tray icon appears — click to show/hide window
```

---

## Key Design Decisions

**Why HTML/TS context menu instead of native Rust?**
Native Tauri menus are static -- defined at build time. Our menu needs dynamic submenus (feelings, actions, speak input). TypeScript lets us fetch available actions from the server and update the menu accordingly. The trade-off is it doesn't look 100% native, but the blur/transparency styling gets close enough.

**Why single WebSocket connection (not two)?**
The avatar app only connects to `/ws/status` (not `/ws/audio`). Audio is played server-side by the TTS server's `AudioPlayer`. The avatar app receives amplitude as a 0-1 float -- it never handles PCM data. This keeps the client simple: no audio decoding, no AudioContext, no playback logic.

**Why dynamic import for renderers?**
`await import("@vibe-ai-partner/plugin-avatar-live2d")` ensures only the selected renderer's code is loaded. If the user chooses VRM, the Live2D PixiJS+Cubism SDK bundle is never downloaded. This matters because Live2D SDK is ~500KB and Three.js is ~600KB.

**Why `ResizeObserver` in RendererHost?**
The Tauri window is resizable. When the user resizes, the WebGL canvas must match the new dimensions. `ResizeObserver` fires once per layout change (more efficient than `window.onresize` + debounce). The renderer plugin handles the actual canvas/camera resize in its `resize()` method.

**Why clamp deltaTime?**
When the user switches to another app and comes back, `performance.now()` reports a huge gap (seconds or minutes). Feeding that to physics/spring animations causes explosions. Clamping to `1/15` (66ms) means the animation "pauses" during tab switches instead of fast-forwarding.
