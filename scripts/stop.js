#!/usr/bin/env node
import { readFileSync, unlinkSync, existsSync } from "fs";
import { resolve } from "path";

const ROOT = resolve(import.meta.dirname, "..");

function stopProcess(pidFile, name) {
  const path = resolve(ROOT, pidFile);
  if (!existsSync(path)) {
    console.log(`  ${name}: not running (no PID file)`);
    return;
  }
  const pid = parseInt(readFileSync(path, "utf-8").trim());
  try {
    process.kill(pid, "SIGTERM");
    unlinkSync(path);
    console.log(`  ${name}: stopped (PID ${pid})`);
  } catch {
    unlinkSync(path);
    console.log(`  ${name}: already stopped`);
  }
}

console.log("Stopping Vibe AI Partner...");
stopProcess(".tts-server.pid", "TTS Server");
stopProcess(".avatar-app.pid", "Avatar App");
