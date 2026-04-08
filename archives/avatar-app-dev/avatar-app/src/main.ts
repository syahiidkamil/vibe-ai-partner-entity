import { App } from "./app.js";

const config = {
  ttsServerUrl: import.meta.env.VITE_TTS_SERVER_URL || "http://localhost:5111",
  wsStatusUrl: import.meta.env.VITE_WS_STATUS_URL || "ws://localhost:5111/ws/status",
  renderer: import.meta.env.VITE_AVATAR_RENDERER || "live2d",
  modelPath: import.meta.env.VITE_MODEL_PATH || "/models/live2d/shizuku",
};

const app = new App(config);
app.start().catch(console.error);
