#!/usr/bin/env node
import { Command } from "commander";
import { speak } from "./commands/speak.js";
import { feeling } from "./commands/feeling.js";
import { action } from "./commands/action.js";

const program = new Command();
const TTS_URL = `http://localhost:${process.env.TTS_SERVER_PORT || 5111}`;

program
  .name("vibe")
  .description("Vibe AI Partner CLI")
  .version("0.1.0");

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
