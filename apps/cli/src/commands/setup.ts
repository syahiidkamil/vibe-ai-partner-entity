import { execSync } from "child_process";
import { createInterface } from "readline";
import { resolve } from "path";
import { writeFileSync, readFileSync, existsSync } from "fs";

const ROOT = resolve(import.meta.dirname, "../../../..");
const TTS_DIR = resolve(ROOT, "apps/tts-server");
const CONFIG_PATH = resolve(ROOT, "config.json");

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

function readConfig(): Record<string, unknown> {
  if (existsSync(CONFIG_PATH)) {
    return JSON.parse(readFileSync(CONFIG_PATH, "utf-8"));
  }
  return {};
}

function writeConfig(config: Record<string, unknown>): void {
  writeFileSync(CONFIG_PATH, JSON.stringify(config, null, 2) + "\n");
}

export async function setup(): Promise<void> {
  console.log("\nVibe AI Partner Setup\n");

  const currentConfig = readConfig();
  const currentEngine = (currentConfig.ttsEngine as string) || "none";
  if (currentEngine !== "none") {
    console.log(`  Current engine: ${currentEngine}\n`);
  }

  console.log("Choose a TTS engine:\n");

  for (let i = 0; i < ENGINES.length; i++) {
    const e = ENGINES[i];
    const tag = e.tag ? ` (${e.tag})` : "";
    const current = e.group === currentEngine ? " *" : "";
    console.log(`  ${i + 1}. ${e.name}${tag}${current}`);
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

    // Kokoro with Japanese support needs UniDic dictionary download
    if (engine.group === "kokoro") {
      const hasUnidic = (() => {
        try {
          const result = execSync(
            'uv run python -c "import unidic; import os; print(os.path.exists(os.path.join(os.path.dirname(unidic.__file__), \'dicdir\', \'mecabrc\')))"',
            { cwd: TTS_DIR, encoding: "utf-8", stdio: ["pipe", "pipe", "pipe"] },
          ).trim();
          return result === "True";
        } catch { return false; }
      })();

      if (!hasUnidic) {
        console.log("\nDownloading Japanese language dictionary (UniDic, ~526MB)...");
        try {
          execSync("uv run python -m unidic download", {
            cwd: TTS_DIR,
            stdio: "inherit",
          });
        } catch {
          console.log("  UniDic download skipped (Japanese may not work)");
        }
      } else {
        console.log("\n  UniDic dictionary already installed.");
      }
    }
  } catch {
    console.error(`\nFailed to install ${engine.name}. Check the error above.`);
    process.exit(1);
  }

  // Save choice to config.json
  writeConfig({ ...currentConfig, ttsEngine: engine.group });

  // Stop running server so next start picks up the new engine
  try {
    const { stop } = await import("./stop.js");
    stop();
  } catch {
    // Server wasn't running — that's fine
  }

  console.log(`\n${engine.name} installed successfully!`);
  console.log(`Config saved to config.json (ttsEngine: "${engine.group}")`);
  console.log("\nNext: npm start");
}
