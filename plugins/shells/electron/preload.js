// Minimal, safe bridge from the served renderer page to the Electron shell.
// Lets the renderer toggle window click-through when the cursor is over its
// interactive chrome (drag strip + close button). contextIsolation stays on.
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('vapeShell', {
  // ignore=true  -> clicks pass through the window
  // ignore=false -> window captures the mouse (so drag / button clicks work)
  setIgnoreMouse: (ignore) => ipcRenderer.send('vape:set-ignore-mouse', !!ignore),
});
