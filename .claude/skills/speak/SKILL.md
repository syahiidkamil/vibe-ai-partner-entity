---
name: speak
description: "Speak text aloud through the VAPE avatar with lip sync (Kokoro TTS). Use when the user asks to speak, say, or read something aloud, or when you want to vocalize a response."
---

# Speak

Vocalize text through the running VAPE avatar. There are two ways in, and both hit
the same endpoint (`POST /api/speak` on the local TTS server):

- **CLI** (`uv run vape speak`) — the default. Auto-resolves the port from config
  and handles quoting. Works from anywhere **inside** the repo.
- **HTTP** (`curl`) — the fallback. Works from **anywhere at all**, including
  outside the repo and with no `uv`. You only need the port.

## CLI — from inside the repo (default)

```bash
uv run vape speak 'TEXT TO SPEAK'
```

`uv` walks up to find the project and the CLI resolves `config.json` from its own
location, so this works from the repo root **or any subfolder** — not only the
root. Parse the argument: everything is the text to speak, except a `v=<voice>`
token, which becomes `--voice <voice>`:

```bash
uv run vape speak 'TEXT TO SPEAK' --voice VOICE_NAME
```

Optional `--speed <float>` (default `1.0`) adjusts pacing.

If the working directory is **outside** the repo, `uv` can't find the project
(`Failed to spawn: vape`). Point it at the project explicitly:

```bash
uv run --project /Users/syahiidkamil/Projects/TheVibeLearning/vibe-ai-partner-entity vape speak 'TEXT TO SPEAK'
```

## HTTP — from anywhere (fallback)

The CLI is just a thin POST to the server, so you can skip `uv` and the repo
entirely and hit the endpoint directly. Default port is `5111` (config
`server.port`):

```bash
curl -s -X POST http://localhost:5111/api/speak \
  -H 'Content-Type: application/json' \
  -d '{"text":"TEXT TO SPEAK","voice":"af_heart"}'
```

Payload fields: `text` (required), `voice` (optional, defaults from config),
`speed` (optional, default `1.0`). Success returns `{"status":"ok"}`. The one
fragility: if `server.port` is changed in `config.json`, change the port here too
or the call gets connection-refused.

## Voices & languages (language auto-detects from the voice prefix)

Match the **text** to the voice's language — write Japanese text for a `j*` voice,
English for `a*` / `b*` voices, or it will mispronounce.

- `af_*` / `am_*` — American English (e.g. `af_heart`, `af_bella`, `am_adam`)
- `bf_*` / `bm_*` — British English (e.g. `bf_emma`, `bm_george`)
- `jf_*` / `jm_*` — Japanese (e.g. `jf_alpha`, `jf_nezumi`, `jm_kumo`)

Full live list: `curl -s http://localhost:5111/api/voices`. The warm default is
`af_heart`.

### Concrete examples

American English (the warm default):

```bash
uv run vape speak 'Hey Boss, ready when you are.' --voice af_heart
```

Japanese (write the text in Japanese — kana/kanji):

```bash
uv run vape speak 'こんにちは、ボス。今日もいい一日にしましょう。' --voice jf_alpha
```

## Quoting

For the CLI, wrap the text in single quotes; if it contains a single quote, escape
it as `'\''`, or use double quotes and escape `"`, `$`, and backticks. For the
curl form the text is JSON, so escape `"` and `\` inside it.

## If it fails

If the CLI prints "Server not running" (or curl gets connection-refused), the
avatar isn't up. Start it with `uv run vape start`.
