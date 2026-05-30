---
name: speak
description: "Speak text aloud through the VAPE avatar with lip sync (Kokoro TTS). Use when the user asks to speak, say, or read something aloud, or when you want to vocalize a response."
---

# Speak

Vocalize text through the running VAPE avatar. This wraps the `vape speak` CLI,
which POSTs to the local TTS server — it resolves the port from config, uses an
HTTP client, and reports errors. Don't hardcode a port or hand-build the request.

## Usage

Run from the repo root:

```bash
uv run vape speak 'TEXT TO SPEAK'
```

Parse the argument: everything is the text to speak, except a `v=<voice>` token,
which becomes `--voice <voice>`:

```bash
uv run vape speak 'TEXT TO SPEAK' --voice VOICE_NAME
```

Optional `--speed <float>` (default `1.0`) adjusts pacing.

## Voice prefixes (language auto-detected by prefix)

- `af_*` / `am_*` — American English
- `bf_*` / `bm_*` — British English
- `jf_*` / `jm_*` — Japanese

## Quoting

Wrap the text in single quotes. If it contains a single quote, escape it as
`'\''`, or use double quotes and escape `"`, `$`, and backticks.

## If it fails

If the CLI prints "Server not running", start the avatar with `uv run vape start`.
