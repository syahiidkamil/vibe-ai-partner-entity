#!/usr/bin/env node
import { Command } from "commander";
import { speak } from "./commands/speak.js";
import { feeling } from "./commands/feeling.js";
import { action } from "./commands/action.js";
import { start } from "./commands/start.js";
import { stop } from "./commands/stop.js";
import { status } from "./commands/status.js";
import { setup } from "./commands/setup.js";

const program = new Command();
const TTS_URL = `http://localhost:${process.env.TTS_SERVER_PORT || 5111}`;

program
  .name("vibe")
  .description("Vibe AI Partner CLI")
  .version("0.1.0");

program
  .command("setup")
  .description("Install a TTS engine (interactive)")
  .action(() => setup());

program
  .command("start")
  .description("Start TTS server and avatar app")
  .option("--prod", "Launch Tauri binary instead of dev server")
  .action((opts) => start(opts));

program
  .command("stop")
  .description("Stop TTS server and avatar app")
  .action(() => stop());

program
  .command("status")
  .description("Check status of TTS server and avatar app")
  .action(() => status());

program
  .command("speak <text>")
  .description("Speak text with TTS and lip sync")
  .option("-v, --voice <voice>", "Voice name")
  .option("-s, --speed <speed>", "Playback speed", "1.0")
  .action((text, opts) => speak(TTS_URL, text, opts));

program
  .command("feeling <name>")
  .description("Set the avatar feeling (happy, sad, curious, etc.)")
  .action((name) => feeling(TTS_URL, name));

program
  .command("action <name>")
  .description("Trigger a self-expression (wave, nod, laugh, etc.)")
  .action((name) => action(TTS_URL, name));

program.parse();
