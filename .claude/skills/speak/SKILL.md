---
name: speak
description: "Speak text with avatar lip sync via Kokoro TTS. Use when the user asks to speak, say, or read text aloud, or when you want to vocalize a response."
---

# Speak

Speak text with avatar lip sync integration using the Makefile `tts-speak` target.

## Argument Parsing

Parse the argument: everything is the text to speak, except if `v=<voice>` appears, extract that as the voice parameter (default: `af_heart`).

## Command Pattern

Use this exact command (replace TEXT and VOICE):

```
make tts-speak t="TEXT" v=VOICE
```

## Voice Prefixes

Language is auto-detected by voice prefix:

- `af_*` / `am_*` = American English
- `bf_*` / `bm_*` = British English
- `jf_*` / `jm_*` = Japanese
- `zf_*` / `zm_*` = Chinese

## Text Sanitization

Before sending, sanitize the text to avoid shell quoting issues:
- Replace apostrophes/single quotes (`'`) with nothing or rephrase (e.g. "You're" → "You are", "don't" → "do not")
- Avoid backticks, dollar signs, and other shell metacharacters in the text

## Error Handling

If the daemon is not running, tell the user to run `make tts-start` first.
