use tauri::{WebviewUrl, WebviewWindowBuilder};

/// Native window host for the VAPE avatar server.
///
/// There is no bundled frontend: the window navigates to the FastAPI server's
/// HTTP origin (`http://localhost:<port>/`), which serves the active renderer.
/// `VAPE_PORT` (default `5111`) selects the server; `VAPE_WIDTH`/`VAPE_HEIGHT`/
/// `VAPE_TITLE` carry the active renderer's plugin.json "window" block (forwarded
/// by start.py), so the window matches the chosen renderer's size.
#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    let port = std::env::var("VAPE_PORT").unwrap_or_else(|_| "5111".to_string());
    let url = format!("http://localhost:{}/", port);
    let width: f64 = std::env::var("VAPE_WIDTH").ok().and_then(|v| v.parse().ok()).unwrap_or(420.0);
    let height: f64 = std::env::var("VAPE_HEIGHT").ok().and_then(|v| v.parse().ok()).unwrap_or(400.0);
    let title = std::env::var("VAPE_TITLE").unwrap_or_else(|_| "VAPE Avatar".to_string());

    tauri::Builder::default()
        .setup(move |app| {
            WebviewWindowBuilder::new(
                app,
                "main",
                WebviewUrl::External(url.parse().unwrap()),
            )
            .title(&title)
            .transparent(true)
            .decorations(false)
            .always_on_top(true)
            .resizable(false)
            .skip_taskbar(true)
            .inner_size(width, height)
            .build()?;

            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
