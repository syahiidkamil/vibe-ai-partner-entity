/**
 * VAPE Shell — Electron
 *
 * Loads the avatar from the TTS server (localhost:5111) which
 * already serves the avatar dist as static files.
 *
 * Usage: npx electron main.js [--port 5111]
 */

const { app, BrowserWindow, screen } = require('electron');

// Parse --port argument
let port = 5111;
for (let i = 0; i < process.argv.length; i++) {
  if (process.argv[i] === '--port' && process.argv[i + 1]) {
    port = parseInt(process.argv[i + 1], 10);
    break;
  }
}

let win;

app.whenReady().then(() => {
  const { width: screenW, height: screenH } = screen.getPrimaryDisplay().workAreaSize;

  win = new BrowserWindow({
    width: 400,
    height: 600,
    x: screenW - 420,
    y: screenH - 620,
    transparent: true,
    frame: false,
    alwaysOnTop: true,
    hasShadow: false,
    resizable: true,
    skipTaskbar: true,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
    },
  });

  win.setIgnoreMouseEvents(false);
  win.setVisibleOnAllWorkspaces(true, { visibleOnFullScreen: true });

  // Load from the TTS server which serves avatar static files at root
  win.loadURL(`http://localhost:${port}`);
});

app.on('window-all-closed', () => app.quit());
