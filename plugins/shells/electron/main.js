// Generic Electron host for VAPE avatars.
//
// Shell-agnostic by design: it hosts ANY renderer by loading the server's
// HTTP origin (http://localhost:<port>/), where the active renderer is served.
// Window geometry comes from the renderer's plugin.json "window" block, passed
// in as --window '<json>'. Renderers are plain web pages — no nodeIntegration.
//
// Args:
//   --port <n>        server port (default 5111)
//   --window '<json>' renderer window prefs {width,height,anchor,margin,title,...}

const { app, BrowserWindow, Tray, Menu, screen, nativeImage, ipcMain } = require('electron');
const path = require('path');

function argOf(flag, fallback) {
  const i = process.argv.indexOf(flag);
  return i >= 0 && process.argv[i + 1] ? process.argv[i + 1] : fallback;
}

const port = parseInt(argOf('--port', '5111'), 10);
let win = {};
try {
  win = JSON.parse(argOf('--window', '{}'));
} catch {
  win = {};
}

let mainWindow;
let tray;

function position(w, h) {
  const { width: sw, height: sh } = screen.getPrimaryDisplay().workAreaSize;
  const anchor = win.anchor || 'bottom-right';
  const m = win.margin || {};
  const x = anchor.includes('right') ? sw - (w + (m.right ?? 20)) : (m.left ?? 20);
  const y = anchor.includes('bottom') ? sh - (h + (m.bottom ?? 20)) : (m.top ?? 20);
  return { x, y };
}

function createWindow() {
  const w = win.width || 200;
  const h = win.height || 260;
  const { x, y } = position(w, h);

  mainWindow = new BrowserWindow({
    width: w,
    height: h,
    x,
    y,
    title: win.title || 'VAPE Avatar',
    transparent: win.transparent !== false,
    frame: win.frame === true,
    alwaysOnTop: win.alwaysOnTop !== false,
    hasShadow: false,
    resizable: win.resizable === true,
    skipTaskbar: true,
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      preload: path.join(__dirname, 'preload.js'),
    },
  });

  // Desktop-pet behaviour: clicks pass THROUGH the window to whatever is behind
  // it (your editor, etc). `forward: true` still delivers mousemove to the page
  // so hover works and the renderer can re-enable interaction over its chrome
  // (drag strip + close button) via window.vapeShell.setIgnoreMouse(false).
  mainWindow.setIgnoreMouseEvents(true, { forward: true });
  mainWindow.loadURL(`http://localhost:${port}/`);
  mainWindow.setVisibleOnAllWorkspaces(true, { visibleOnFullScreen: true });

  // Force a clean repaint when the window loses focus, so a transparent
  // always-on-top window never shows a stale frame on macOS.
  mainWindow.on('blur', () => mainWindow.webContents.invalidate());
}

ipcMain.on('vape:set-ignore-mouse', (_event, ignore) => {
  if (mainWindow) {
    mainWindow.setIgnoreMouseEvents(ignore, { forward: true });
  }
});

// Resize from the renderer's −/+ controls. The renderer re-renders its content
// at the new size; we just size the OS window to match. The window's bottom-
// right corner is pinned so the avatar grows/shrinks toward its anchor instead
// of crawling across the screen (and never marches off-screen when shrinking).
// resizable is toggled on around setSize because a frameless resizable:false
// window ignores programmatic resizes on some platforms. invalidate() forces a
// clean repaint of the transparent backing store after the resize.
ipcMain.on('vape:resize', (_event, { w, h }) => {
  if (!mainWindow) return;
  const nw = Math.round(w);
  const nh = Math.round(h);
  const [cx, cy] = mainWindow.getPosition();
  const [cw, ch] = mainWindow.getSize();
  const wasResizable = mainWindow.isResizable();
  if (!wasResizable) mainWindow.setResizable(true);
  mainWindow.setSize(nw, nh);
  mainWindow.setPosition(cx + cw - nw, cy + ch - nh);
  if (!wasResizable) mainWindow.setResizable(false);
  mainWindow.webContents.invalidate();
});

function createTray() {
  tray = new Tray(nativeImage.createEmpty());
  tray.setToolTip(win.title || 'VAPE Avatar');
  tray.setContextMenu(
    Menu.buildFromTemplate([
      { label: `Server: localhost:${port}`, enabled: false },
      { type: 'separator' },
      { label: 'Quit', click: () => app.quit() },
    ])
  );
}

app.whenReady().then(() => {
  createWindow();
  createTray();
});

app.on('window-all-closed', () => app.quit());
