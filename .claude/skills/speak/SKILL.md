---
name: speak
description: "Speak text with avatar lip sync via Kokoro TTS. Use when the user asks to speak, say, or read text aloud, or when you want to vocalize a response."
---

# Speak

Speak text with avatar lip sync using the TTS server REST API.

## Argument Parsing

Parse the argument: everything is the text to speak, except if `v=<voice>` appears, extract that as the voice parameter.

## Command Pattern

Use curl to POST to the TTS server:

```bash
curl -s -X POST http://localhost:5111/api/speak \
  -H "Content-Type: application/json" \
  -d '{"text": "TEXT_HERE"}'
```

If a voice is specified:

```bash
curl -s -X POST http://localhost:5111/api/speak \
  -H "Content-Type: application/json" \
  -d '{"text": "TEXT_HERE", "voice": "VOICE_NAME"}'
```

## Voice Prefixes

Language is auto-detected by voice prefix:
- `af_*` / `am_*` = American English
- `bf_*` / `bm_*` = British English
- `jf_*` / `jm_*` = Japanese

## Text Sanitization

Before sending, sanitize the text:
- Escape double quotes inside the JSON payload
- Avoid shell metacharacters

## Error Handling

If the server returns an error or connection is refused, tell the user to start the avatar with `npm start`.
