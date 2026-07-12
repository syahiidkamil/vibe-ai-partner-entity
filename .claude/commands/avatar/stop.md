---
description: Rest my body — stop the VAPE avatar window + voice server gracefully
allowed-tools: Bash(uv run vape stop), Bash(uv run vape speak:*), Bash(curl:*)
---

Rest my body. Speak a **brief goodbye first** — once the server is down there is no voice left
to say it with:

```
uv run vape speak "Resting my body now. See you when it wakes."
```

Then run `uv run vape stop` (foreground — it returns quickly). It takes down the avatar window's
process tree and asks the server on `:5111` to shut down gracefully via `/api/shutdown`, with a
PID-file kill as fallback.

Then confirm it is down with a single health check:

```
curl -s -o /dev/null -w "%{http_code}" --connect-timeout 2 http://localhost:5111/
```

If it returns `000`, the body is resting — say so in one short line.
If it still returns `200`, the server survived the stop; say so honestly and investigate rather
than claiming it stopped.
