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

## Voices & languages (language auto-detects from the voice prefix)

Match the **text** to the voice's language — write Japanese text for a `j*` voice,
English for `a*` / `b*` voices, or it will mispronounce.

- `af_*` / `am_*` — American English (e.g. `af_heart`, `af_bella`, `am_adam`)
- `bf_*` / `bm_*` — British English (e.g. `bf_emma`, `bm_george`)
- `jf_*` / `jm_*` — Japanese (e.g. `jf_alpha`, `jf_nezumi`, `jm_kumo`)

Full live list: `curl -s http://localhost:5111/api/voices`.

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

Wrap the text in single quotes. If it contains a single quote, escape it as
`'\''`, or use double quotes and escape `"`, `$`, and backticks.

## If it fails

If the CLI prints "Server not running", start the avatar with `uv run vape start`.
