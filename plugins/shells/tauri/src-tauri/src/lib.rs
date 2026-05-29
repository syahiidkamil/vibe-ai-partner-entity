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
        .invoke_handler(tauri::generate_handler![vape_set_zones])
        .setup(move |app| {
            WebviewWindowBuilder::new(app, "main", WebviewUrl::External(url.parse().unwrap()))
                .title(&title)
                .transparent(true)
                .decorations(false)
                .always_on_top(true)
                .resizable(false)
                .skip_taskbar(true)
                .inner_size(width, height)
                .build()?;

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
