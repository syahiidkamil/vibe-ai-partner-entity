import { defineConfig } from "vite";

export default defineConfig({
  clearScreen: false,
  server: {
    port: 1420,
    strictPort: true,
    fs: {
      allow: ["../../"],  // Allow serving model files from project root
    },
  },
  envPrefix: ["VITE_"],
  build: {
    target: ["es2022", "chrome100"],
    minify: !process.env.TAURI_DEBUG ? "esbuild" : false,
    sourcemap: !!process.env.TAURI_DEBUG,
  },
});
