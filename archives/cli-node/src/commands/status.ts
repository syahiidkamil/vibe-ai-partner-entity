import { readFileSync, existsSync } from "fs";
import { resolve } from "path";

const ROOT = resolve(import.meta.dirname, "../../../..");
const TTS_PORT = process.env.TTS_SERVER_PORT || 5111;

export async function status(): Promise<void> {
  console.log("Vibe AI Partner Status:\n");

  // TTS Server
  try {
    const res = await fetch(`http://localhost:${TTS_PORT}/api/health`);
    const data = (await res.json()) as { engine: string };
    console.log(
      `  TTS Server:  OK (http://localhost:${TTS_PORT}, engine: ${data.engine})`,
    );
  } catch {
    console.log("  TTS Server:  NOT RUNNING");
  }

  // Avatar App (check PID file)
  const pidPath = resolve(ROOT, ".avatar-app.pid");
  if (existsSync(pidPath)) {
    const pid = parseInt(readFileSync(pidPath, "utf-8").trim());
    try {
      process.kill(pid, 0);
      console.log(`  Avatar App:  OK (PID ${pid})`);
    } catch {
      console.log("  Avatar App:  NOT RUNNING (stale PID)");
    }
  } else {
    console.log("  Avatar App:  NOT RUNNING");
  }
}
