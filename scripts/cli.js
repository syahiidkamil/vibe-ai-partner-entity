#!/usr/bin/env node
// Thin wrapper that forwards args to the CLI package
import { execSync } from "child_process";

const args = process.argv.slice(2).join(" ");
try {
  execSync(`node apps/cli/dist/index.js ${args}`, {
    stdio: "inherit",
    cwd: new URL("..", import.meta.url).pathname,
  });
} catch {
  process.exit(1);
}
