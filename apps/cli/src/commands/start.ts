import { spawn } from "child_process";
import { existsSync, writeFileSync } from "fs";
import { resolve } from "path";

const ROOT = resolve(import.meta.dirname, "../../../..");
const TTS_PORT = process.env.TTS_SERVER_PORT || 5111;

async function checkHealth(port: string | number): Promise<boolean> {
  try {
    const res = await fetch(`http://localhost:${port}/api/health`);
    return res.ok;
  } catch {
    return false;
  }
}

async function waitForHealth(
  port: string | number,
  timeoutMs = 120000,
): Promise<boolean> {
  const start = Date.now();
  let dots = 0;
  while (Date.now() - start < timeoutMs) {
    if (await checkHealth(port)) {
      if (dots > 0) process.stdout.write("\n");
      return true;
    }
    // Show progress so user knows it's not stuck
    if (dots === 0) {
      process.stdout.write("  Waiting for TTS server (first run downloads model)");
    }
    process.stdout.write(".");
    dots++;
    await new Promise((r) => setTimeout(r, 2000));
  }
  if (dots > 0) process.stdout.write("\n");
  throw new Error(
    `TTS server did not start within ${timeoutMs / 1000}s. Check logs: cd apps/tts-server && uv run uvicorn vibe_tts.server:app --port ${port}`,
  );
}

async function logEngineInfo(port: string | number): Promise<void> {
  try {
    const [healthRes, voicesRes] = await Promise.all([
      fetch(`http://localhost:${port}/api/health`),
      fetch(`http://localhost:${port}/api/voices`),
    ]);
    const health = (await healthRes.json()) as { engine?: string };
    const voices = (await voicesRes.json()) as { voices?: { id: string; name: string }[] };
    const engine = health.engine || "none";
    const voice = voices.voices?.[0]?.name || "default";
    console.log(`  TTS Server running on http://localhost:${port} (${engine}, voice: ${voice})`);
  } catch {
    console.log(`  TTS Server running on http://localhost:${port}`);
  }
}

export async function start(opts: { prod?: boolean }): Promise<void> {
  console.log("Starting Vibe AI Partner...");

  // 1. TTS Server
  if (await checkHealth(TTS_PORT)) {
    await logEngineInfo(TTS_PORT);
  } else {
    console.log("  Starting TTS server...");
    const env = { ...process.env };
    // macOS: PyTorch MPS fallback needed to avoid GPU errors
    if (process.platform === "darwin") {
      env.PYTORCH_ENABLE_MPS_FALLBACK = env.PYTORCH_ENABLE_MPS_FALLBACK || "1";
      // phonemizer can't auto-detect espeak-ng from homebrew
      if (!env.PHONEMIZER_ESPEAK_LIBRARY) {
        const lib = "/opt/homebrew/lib/libespeak-ng.dylib";
        if (existsSync(lib)) env.PHONEMIZER_ESPEAK_LIBRARY = lib;
      }
    }

    const tts = spawn(
      "uv",
      [
        "run",
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
        env,
      },
    );

    // Surface server errors (e.g. missing deps) instead of silent timeout
    let serverError = "";
    tts.stderr?.on("data", (chunk: Buffer) => {
      serverError += chunk.toString();
    });
    tts.on("exit", (code) => {
      if (code && code !== 0) {
        console.error(`\n  TTS server exited with code ${code}`);
        if (serverError) {
          // Show last 5 lines of error
          const lines = serverError.trim().split("\n").slice(-5);
          lines.forEach((l) => console.error(`    ${l}`));
        }
        process.exit(1);
      }
    });

    tts.unref();
    writeFileSync(resolve(ROOT, ".tts-server.pid"), String(tts.pid));
    await waitForHealth(TTS_PORT);
    await logEngineInfo(TTS_PORT);
  }

  // 2. Avatar App
  console.log("  Starting avatar app...");
  if (!opts.prod) {
    spawn("npm", ["run", "dev", "-w", "apps/avatar-app"], {
      cwd: ROOT,
      stdio: "inherit",
    });
  } else {
    const platform = process.platform;
    let binaryName: string;
    if (platform === "darwin") {
      binaryName = resolve(
        ROOT,
        "apps/avatar-app/src-tauri/target/release/bundle/macos/Vibe Avatar.app/Contents/MacOS/vibe-avatar",
      );
    } else if (platform === "win32") {
      binaryName = resolve(
        ROOT,
        "apps/avatar-app/src-tauri/target/release/vibe-avatar.exe",
      );
    } else {
      binaryName = resolve(
        ROOT,
        "apps/avatar-app/src-tauri/target/release/vibe-avatar",
      );
    }

    try {
      const avatar = spawn(binaryName, [], {
        stdio: "pipe",
        detached: true,
      });
      avatar.unref();
      writeFileSync(resolve(ROOT, ".avatar-app.pid"), String(avatar.pid));
    } catch {
      console.log(
        "  Avatar App: binary not found. Build it first or remove --prod flag.",
      );
    }
  }

  console.log("\n  Avatar is alive! Open Claude Code to begin.");
}
