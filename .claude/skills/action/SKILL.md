---
name: action
description: "Trigger a one-shot VAPE avatar animation or gesture (wave, nod, celebrate, …). Use to make the avatar physically react."
---

# Action

Trigger a one-shot avatar gesture via the `vape action` CLI, which POSTs to the
local server (resolving the port from config).

## Usage

Run from the repo root:

```bash
uv run vape action ACTION_NAME
```

Examples: `wave`, `nod`, `celebrate`, `shake`. The exact set depends on the
active renderer's motions.

## If it fails

If the CLI prints "Server not running", start the avatar with `uv run vape start`.
