import { execSync } from "child_process";
import { createInterface } from "readline";
import { resolve } from "path";

const ROOT = resolve(import.meta.dirname, "../../../..");
const TTS_DIR = resolve(ROOT, "apps/tts-server");

const ENGINES = [
  {
    name: "Kokoro ONNX",
    group: "kokoro-onnx",
    desc: "Good quality, CPU-only, ~300MB model download",
    tag: "Recommended",
  },
  {
    name: "Kokoro (PyTorch)",
    group: "kokoro",
    desc: "Best quality, streaming, ~2GB download (torch)",
    tag: "",
  },
  {
    name: "KittenTTS",
    group: "kitten",
    desc: "Lightest, CPU-only, 15M params, ~150MB download",
    tag: "",
  },
];

function ask(question: string): Promise<string> {
  const rl = createInterface({ input: process.stdin, output: process.stdout });
  return new Promise((resolve) => {
    rl.question(question, (answer) => {
      rl.close();
      resolve(answer.trim());
    });
  });
}

export async function setup(): Promise<void> {
  console.log("\nVibe AI Partner Setup\n");
  console.log("Choose a TTS engine:\n");

  for (let i = 0; i < ENGINES.length; i++) {
    const e = ENGINES[i];
    const tag = e.tag ? ` (${e.tag})` : "";
    console.log(`  ${i + 1}. ${e.name}${tag}`);
    console.log(`     ${e.desc}\n`);
  }

  const answer = await ask("Enter choice [1-3]: ");
  const choice = parseInt(answer) - 1;

  if (isNaN(choice) || choice < 0 || choice >= ENGINES.length) {
    console.error("Invalid choice. Run setup again.");
    process.exit(1);
  }

  const engine = ENGINES[choice];
  console.log(`\nInstalling ${engine.name}...`);

  try {
    execSync(`uv sync --extra ${engine.group}`, {
      cwd: TTS_DIR,
      stdio: "inherit",
    });
  } catch {
    console.error(`\nFailed to install ${engine.name}. Check the error above.`);
    process.exit(1);
  }

  console.log(`\n${engine.name} installed successfully!`);
  console.log("\nNext: npm start");
}
