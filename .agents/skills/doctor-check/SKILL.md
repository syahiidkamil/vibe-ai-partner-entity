---
name: doctor-check
description: "Run a whole-system VAPE health check covering dependencies, prerequisites, voice, avatar, and memory."
---

# doctor-check — VAPE skill (Antigravity wrapper)

The canonical instructions live in `.claude/commands/doctor/check.md` (workspace-relative).
Read that file now and follow it as this skill's full instructions.

Summary of steps:
1. Run `uv run vape doctor` — the CLI is the source of truth; relay the verdict plainly.
2. For each failure, explain it in one sentence and offer the printed fix command (run fixes only with the user's yes). For each warning, say why it is advisory.
3. If memory shows a lower tier than configured: `uv run vape memory doctor` gives the fuller ladder, `uv run vape memory index` heals staleness.
