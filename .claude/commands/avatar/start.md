---
description: Wake my body — start the VAPE avatar + voice server in the background
allowed-tools: Bash(uv run vape start), Bash(curl:*)
---

Wake my body. Run `uv run vape start` in the **background** (Bash tool with `run_in_background: true`) so the
VAPE avatar and the voice server on `:5111` come up without blocking this session.

Then confirm it is alive with a single health check:

```
curl -s -o /dev/null -w "%{http_code}" http://localhost:5111/
```

If it returns `200`, the body is up — say so in one short line, and speak a brief hello so I land out loud.
If it returns `000`, the server is still booting; report that it is coming up rather than claiming it is ready.
