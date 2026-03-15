---
description: Speak text via Kokoro TTS daemon
argument-hint: <text> [v=voice]
---

Send the given text to the Kokoro TTS daemon at `/tmp/vibe-kokoro.sock` using a Bash one-liner.

Parse the argument: everything is the text to speak, except if `v=<voice>` appears, extract that as the voice parameter (default: `af_heart`).

Use this exact command pattern (replace TEXT and VOICE):

```
python3 -c "import socket,json; s=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM); s.connect('/tmp/vibe-kokoro.sock'); s.sendall(json.dumps({'text':'TEXT','voice':'VOICE'}).encode()); s.close()"
```

Voice prefixes for language auto-detection:
- `af_*` / `am_*` = American English
- `bf_*` / `bm_*` = British English
- `jf_*` / `jm_*` = Japanese
- `zf_*` / `zm_*` = Chinese

If the daemon is not running, tell the user to run `make tts-start` first.
