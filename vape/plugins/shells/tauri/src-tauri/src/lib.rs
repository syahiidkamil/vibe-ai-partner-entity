use std::sync::Mutex;
use std::time::Duration;

use tauri::{Manager, WebviewUrl, WebviewWindowBuilder};

/// Interactive zones (logical CSS px, window-relative: [x, y, w, h]) reported by
/// the renderer — the drag strip and the close button.
struct Zones(Mutex<Vec<[f64; 4]>>);

/// The renderer calls this (via window.__TAURI__.core.invoke) to tell the shell
/// which on-screen rectangles should capture the mouse. Everything else is
/// click-through.
#[tauri::command]
fn vape_set_zones(zones: Vec<[f64; 4]>, state: tauri::State<'_, Zones>) {
    if let Ok(mut z) = state.0.lock() {
        *z = zones;
    }
}

/// Resize the avatar window to (width, height) logical px, pinning the window's
/// bottom-right corner so it grows/shrinks toward its anchor (matching Electron).
/// The renderer scales its content with a CSS transform; this only sizes the OS
/// window. Called by the renderer's −/+ controls via window.__TAURI__.core.invoke.
#[tauri::command]
fn vape_resize(width: f64, height: f64, window: tauri::WebviewWindow) {
    let sf = window.scale_factor().unwrap_or(1.0);
    if let (Ok(pos), Ok(size)) = (window.outer_position(), window.outer_size()) {
        let left = pos.x as f64 / sf;
        let top = pos.y as f64 / sf;
        let old_w = size.width as f64 / sf;
        let old_h = size.height as f64 / sf;
        let _ = window.set_position(tauri::LogicalPosition::new(
            left + old_w - width,
            top + old_h - height,
        ));
    }
    let _ = window.set_size(tauri::LogicalSize::new(width, height));
}

/// On macOS, make the avatar window float above EVERYTHING — including other
/// apps in native (green-button) fullscreen, which each get their own Space.
///
/// Tauri's `always_on_top` only sets `NSFloatingWindowLevel` and joins the
/// *current* Space, so a fullscreen app hides the avatar. We drop to AppKit and:
///   • raise the window level above fullscreen content, and
///   • set the collection behavior to `CanJoinAllSpaces | Stationary |
///     FullScreenAuxiliary` so the window rides into every Space, fullscreen
///     ones included.
/// The level is intentionally high (screen-saver); lower it if the pet floats
/// over UI you'd rather it stayed under.
#[cfg(target_os = "macos")]
fn float_over_fullscreen(window: &tauri::WebviewWindow) {
    use objc::runtime::Object;
    use objc::{msg_send, sel, sel_impl};

    // AppKit constants (AppKit/NSWindow.h)
    const NS_SCREEN_SAVER_WINDOW_LEVEL: i64 = 1000;
    const CAN_JOIN_ALL_SPACES: u64 = 1 << 0; //   1
    const STATIONARY: u64 = 1 << 4; //           16
    const FULLSCREEN_AUXILIARY: u64 = 1 << 8; // 256

    if let Ok(ptr) = window.ns_window() {
        let ns_window = ptr as *mut Object;
        let behavior = CAN_JOIN_ALL_SPACES | STATIONARY | FULLSCREEN_AUXILIARY;
        unsafe {
            let _: () = msg_send![ns_window, setLevel: NS_SCREEN_SAVER_WINDOW_LEVEL];
            let _: () = msg_send![ns_window, setCollectionBehavior: behavior];
        }
    }
}

#[cfg(not(target_os = "macos"))]
fn float_over_fullscreen(_window: &tauri::WebviewWindow) {}

/// Native window host for the VAPE avatar server.
///
/// There is no bundled frontend: the window navigates to the FastAPI server's
/// HTTP origin (`http://localhost:<port>/`), which serves the active renderer.
/// `VAPE_PORT` (default `5111`) selects the server; `VAPE_WIDTH`/`VAPE_HEIGHT`/
/// `VAPE_TITLE` carry the active renderer's plugin.json "window" block.
///
/// Click-through ("desktop pet"): the window starts interactive and a poll loop
/// makes it click-through whenever the cursor is NOT over a reported zone. Tauri
/// has no event-forwarding while ignoring the cursor (unlike Electron), so the
/// shell polls the global cursor position and toggles `set_ignore_cursor_events`
/// from the Rust side, hit-testing against the renderer-reported zones.
#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    let port = std::env::var("VAPE_PORT").unwrap_or_else(|_| "5111".to_string());
    let url = format!("http://localhost:{}/", port);
    let width: f64 = std::env::var("VAPE_WIDTH").ok().and_then(|v| v.parse().ok()).unwrap_or(420.0);
    let height: f64 = std::env::var("VAPE_HEIGHT").ok().and_then(|v| v.parse().ok()).unwrap_or(400.0);
    let title = std::env::var("VAPE_TITLE").unwrap_or_else(|_| "VAPE Avatar".to_string());

    tauri::Builder::default()
        .manage(Zones(Mutex::new(Vec::new())))
        .invoke_handler(tauri::generate_handler![vape_set_zones, vape_resize])
        .setup(move |app| {
            // Run as a Dock-less "agent": macOS only allows agent apps to float
            // their windows over OTHER apps' native fullscreen Spaces. This drops
            // the Dock tile while running — expected for a desktop pet.
            #[cfg(target_os = "macos")]
            app.set_activation_policy(tauri::ActivationPolicy::Accessory);

            let main_window = WebviewWindowBuilder::new(app, "main", WebviewUrl::External(url.parse().unwrap()))
                .title(&title)
                .transparent(true)
                .decorations(false)
                // No window shadow: macOS draws a shadow around the avatar's opaque
                // silhouette, and on a transparent window the idle motion shifts that
                // silhouette while the shadow goes stale — the mismatch reads as a
                // light edge-fringe that only clears when focus/drag forces macOS to
                // recompute it. Dropping the shadow removes the fringe for good while
                // keeping full transparency + click-through.
                .shadow(false)
                .always_on_top(true)
                .resizable(false)
                .skip_taskbar(true)
                .inner_size(width, height)
                .build()?;

            // Keep the avatar visible even over apps in native (green-button)
            // fullscreen, which live in their own Space.
            float_over_fullscreen(&main_window);

            // Poll the global cursor and toggle click-through. The window starts
            // interactive (the safe default): if this thread ever dies, the
            // window stays usable rather than permanently click-through.
            let handle = app.handle().clone();
            std::thread::spawn(move || {
                let mut interactive = true;
                loop {
                    std::thread::sleep(Duration::from_millis(60));
                    let Some(win) = handle.get_webview_window("main") else { break };
                    let zones = handle
                        .state::<Zones>()
                        .0
                        .lock()
                        .map(|z| z.clone())
                        .unwrap_or_default();

                    // Stay interactive until the renderer has reported its zones,
                    // so the window is never click-through with no way to grab it.
                    let want_interactive = if zones.is_empty() {
                        true
                    } else {
                        (|| {
                            let scale = win.scale_factor().ok()?;
                            let wpos = win.outer_position().ok()?;
                            let cur = win.cursor_position().ok()?;
                            let rx = (cur.x - wpos.x as f64) / scale;
                            let ry = (cur.y - wpos.y as f64) / scale;
                            Some(zones.iter().any(|z| {
                                rx >= z[0] && rx <= z[0] + z[2] && ry >= z[1] && ry <= z[1] + z[3]
                            }))
                        })()
                        .unwrap_or(true)
                    };

                    if want_interactive != interactive {
                        let _ = win.set_ignore_cursor_events(!want_interactive);
                        interactive = want_interactive;
                    }
                }
            });

            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
