import { execSync } from "child_process";
import { readFileSync, unlinkSync, existsSync } from "fs";
import { resolve } from "path";

const ROOT = resolve(import.meta.dirname, "../../../..");
const TTS_PORT = process.env.TTS_SERVER_PORT || 5111;
const AVATAR_PORT = 1420;

function stopByPid(pidFile: string, name: string): boolean {
  const path = resolve(ROOT, pidFile);
  if (!existsSync(path)) return false;
  const pid = parseInt(readFileSync(path, "utf-8").trim());
  try {
    process.kill(pid, "SIGTERM");
    unlinkSync(path);
    console.log(`  ${name}: stopped (PID ${pid})`);
    return true;
  } catch {
    unlinkSync(path);
    return false;
  }
}

function stopByPort(port: number | string, name: string): boolean {
  try {
    const pids = execSync(`lsof -ti:${port} 2>/dev/null`, { encoding: "utf-8" }).trim();
    if (!pids) return false;
    execSync(`lsof -ti:${port} | xargs kill 2>/dev/null`);
    console.log(`  ${name}: stopped (port ${port})`);
    return true;
  } catch {
    return false;
  }
}

export function stop(): void {
  console.log("Stopping Vibe AI Partner...");

  // TTS Server — try PID file first, fall back to port
  if (!stopByPid(".tts-server.pid", "TTS Server")) {
    if (!stopByPort(TTS_PORT, "TTS Server")) {
      console.log("  TTS Server: not running");
    }
  }

  // Avatar App — try PID file first, fall back to port
  if (!stopByPid(".avatar-app.pid", "Avatar App")) {
    if (!stopByPort(AVATAR_PORT, "Avatar App")) {
      console.log("  Avatar App: not running");
    }
  }
}
