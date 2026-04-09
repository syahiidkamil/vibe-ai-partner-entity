import { defineConfig } from "vite";
import { resolve } from "path";

export default defineConfig({
  clearScreen: false,
  server: {
    port: 1420,
    strictPort: true,
    fs: {
      allow: ["../../"],
    },
  },
  resolve: {
    alias: {
      "@vibe-ai-partner/plugin-avatar-live2d": resolve(__dirname, "packages/plugin-avatar-live2d/src"),
      "@vibe-ai-partner/core": resolve(__dirname, "packages/core/src"),
      "@vibe-ai-partner/shared": resolve(__dirname, "packages/shared/src"),
    },
  },
  envPrefix: ["VITE_"],
  build: {
    target: ["es2022", "chrome100"],
    minify: !process.env.TAURI_DEBUG ? "esbuild" : false,
    sourcemap: !!process.env.TAURI_DEBUG,
  },
});
