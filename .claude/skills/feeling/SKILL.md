---
name: feeling
description: "Set the VAPE avatar's emotional expression (happy, curious, proud, …). Use to make the avatar's face/mood match the moment."
---

# Feeling

Set the avatar's feeling via the `vape feeling` CLI, which POSTs to the local
server (resolving the port from config).

## Usage

Run from the repo root:

```bash
uv run vape feeling FEELING_NAME
```

Examples: `happy`, `curious`, `proud`, `sad`, `surprised`, `neutral`. The exact
set depends on the active renderer's expressions.

## If it fails

If the CLI prints "Server not running", start the avatar with `uv run vape start`.
