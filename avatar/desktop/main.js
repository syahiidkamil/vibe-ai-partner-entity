const { app, BrowserWindow, Tray, Menu, screen, nativeImage } = require('electron');
const path = require('path');

let win;
let tray;

function createWindow() {
  const { width: screenW, height: screenH } = screen.getPrimaryDisplay().workAreaSize;

  win = new BrowserWindow({
    width: 200,
    height: 250,
    x: screenW - 250,
    y: screenH - 300,
    transparent: true,
    frame: false,
    alwaysOnTop: true,
    hasShadow: false,
    resizable: false,
    skipTaskbar: true,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
  });

  // Make window ignore mouse events on transparent areas
  win.setIgnoreMouseEvents(false);

  win.loadFile('index.html');

  // Allow dragging from the renderer
  win.setVisibleOnAllWorkspaces(true, { visibleOnFullScreen: true });
}

function createTray() {
  // Create a tiny tray icon (1x1 pixel)
  const icon = nativeImage.createEmpty();
  tray = new Tray(icon);
  tray.setToolTip('Desktop Avatar');

  const contextMenu = Menu.buildFromTemplate([
    {
      label: 'Moods',
      submenu: [
        { label: 'Neutral', click: () => win.webContents.send('mood', 'neutral') },
        { label: 'Happy', click: () => win.webContents.send('mood', 'happy') },
        { label: 'Sad', click: () => win.webContents.send('mood', 'sad') },
        { label: 'Angry', click: () => win.webContents.send('mood', 'angry') },
        { label: 'Thinking', click: () => win.webContents.send('mood', 'thinking') },
      ],
    },
    {
      label: 'Actions',
      submenu: [
        { label: 'Wave', click: () => win.webContents.send('action', 'wave') },
        { label: 'Jump', click: () => win.webContents.send('action', 'jump') },
        { label: 'Dance', click: () => win.webContents.send('action', 'dance') },
      ],
    },
    { type: 'separator' },
    { label: 'Quit', click: () => app.quit() },
  ]);

  tray.setContextMenu(contextMenu);
}

app.whenReady().then(() => {
  createWindow();
  createTray();
});

app.on('window-all-closed', () => app.quit());
