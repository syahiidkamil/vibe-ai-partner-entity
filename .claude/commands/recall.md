---
description: Search my memory corpus for the few best matches (hybrid pgvector + FTS)
allowed-tools: Bash(uv run vape memory recall:*)
---

Reach back into my memory. Run:

```
uv run vape memory recall "$ARGUMENTS"
```

This is hybrid search over my corpus — semantic (pgvector) blended with keyword (FTS) —
returning the few best rows nearest-first, never a dump. If `$ARGUMENTS` names a bubble
scope you can add `--bubble <name>`; tune the count with `--limit N`.

Read what surfaces, then answer me with it folded into the reply in my own voice — not as
a raw list of database rows. If nothing surfaces, say so plainly; an empty recall is honest,
not a failure.
