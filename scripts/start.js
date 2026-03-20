#!/usr/bin/env node
import { spawn } from "child_process";
import { writeFileSync } from "fs";
import { resolve } from "path";

const ROOT = resolve(import.meta.dirname, "..");
const TTS_PORT = process.env.TTS_SERVER_PORT || 5111;
const isDev = process.argv.includes("--dev");

async function checkHealth(port) {
  try {
    const res = await fetch(`http://localhost:${port}/api/health`);
    return res.ok;
  } catch {
    return false;
  }
}

async function waitForHealth(port, timeoutMs = 30000) {
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    if (await checkHealth(port)) return true;
    await new Promise((r) => setTimeout(r, 500));
  }
  throw new Error(`TTS server did not start within ${timeoutMs}ms`);
}

async function main() {
  console.log("Starting Vibe AI Partner...");

  // 1. TTS Server
  if (await checkHealth(TTS_PORT)) {
    console.log(`  TTS Server already running on port ${TTS_PORT}`);
  } else {
    console.log("  Starting TTS server...");
    const tts = spawn(
      "python",
      [
        "-m",
        "uvicorn",
        "vibe_tts.server:app",
        "--port",
        String(TTS_PORT),
        "--host",
        "0.0.0.0",
      ],
      {
        cwd: resolve(ROOT, "apps/tts-server"),
        stdio: "pipe",
        detached: true,
      }
    );
    tts.unref();
    writeFileSync(resolve(ROOT, ".tts-server.pid"), String(tts.pid));
    await waitForHealth(TTS_PORT);
    console.log(`  TTS Server running on http://localhost:${TTS_PORT}`);
  }

  // 2. Avatar App
  console.log("  Starting avatar app...");
  if (isDev) {
    spawn("npm", ["run", "dev", "-w", "apps/avatar-app"], {
      cwd: ROOT,
      stdio: "inherit",
    });
  } else {
    // Launch built Tauri binary (platform-specific)
    const platform = process.platform;
    let binaryName;
    if (platform === "darwin") {
      binaryName = resolve(
        ROOT,
        "apps/avatar-app/src-tauri/target/release/bundle/macos/Vibe Avatar.app/Contents/MacOS/vibe-avatar"
      );
    } else if (platform === "win32") {
      binaryName = resolve(
        ROOT,
        "apps/avatar-app/src-tauri/target/release/vibe-avatar.exe"
      );
    } else {
      binaryName = resolve(
        ROOT,
        "apps/avatar-app/src-tauri/target/release/vibe-avatar"
      );
    }

    try {
      const avatar = spawn(binaryName, [], {
        stdio: "pipe",
        detached: true,
      });
      avatar.unref();
      writeFileSync(resolve(ROOT, ".avatar-app.pid"), String(avatar.pid));
    } catch (err) {
      console.log(
        "  Avatar App: binary not found. Build it first or use --dev flag."
      );
    }
  }

  console.log("\n  Avatar is alive! Open Claude Code to begin.");
}

main().catch((err) => {
  console.error("Startup failed:", err.message);
  process.exit(1);
});
