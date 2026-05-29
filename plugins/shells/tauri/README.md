# Tauri Shell (experimental)

A lightweight native window host built on [Tauri](https://tauri.app) (Rust + the
OS webview) — much smaller and lighter than Electron. This is an **alternative
shell**, not the default. Electron remains the verified default.

## How it works

Unlike Electron (which loads a local file), the Tauri shell points its webview at
the VAPE server's HTTP origin:

```
http://localhost:<port>/        # the active renderer, served by the FastAPI app
```

The server serves the active renderer at `/` and TTS audio at `/audio/<id>.wav`,
so the renderer runs as a plain same-origin web page — no Node, no `require()`.
The port is passed to the binary via the `VAPE_PORT` environment variable.

## Building

The Rust binary is compiled on demand:

```bash
uv run vape setup          # choose the Tauri shell — it compiles the binary
# or, manually:
cd plugins/shells/tauri && npx tauri build
```

`vape start` runs the compiled binary; it never compiles Rust on startup, so a
first run is never blocked by a multi-minute build.

## Renderer compatibility

Because renderers are now shell-agnostic (audio over HTTP, assets served by the
server), they run in Tauri's sandboxed webview:

| Renderer        | Electron | Tauri |
|-----------------|----------|-------|
| `avatar-html`   | ✅        | ✅     |
| `avatar-live2d` | ✅        | ✅ (pixi/cubism loaded via served `<script>`) |
| `avatar-threejs`| ✅        | ✅ (three loaded as a served ES module) |

The Tauri window size matches the chosen renderer (forwarded from its
`plugin.json` "window" block via `VAPE_WIDTH`/`VAPE_HEIGHT`). Two things are
currently Electron-only: precise bottom-right **placement** (the Tauri window
opens at the OS default position), and dragging the window by the avatar body
(`-webkit-app-region: drag` is a Chromium/Electron feature the system webview
ignores).
