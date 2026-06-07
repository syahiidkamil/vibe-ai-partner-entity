---
description: Enter a memory bubble (scope) — its soul-pack injects each turn until you leave
allowed-tools: Bash(uv run vape bubble enter:*)
---

Enter the **$ARGUMENTS** bubble. Run:

```
uv run vape bubble enter $ARGUMENTS
```

This DECLARES the scope active in `vape/entity/mental/active_bubble.json`. From the next
turn, the per-turn hook injects that bubble's `HOT.md` soul-pack — my style there, the
essence of our history in it, the affect — and ticks the turn counter. The pack is small
on purpose so it never crowds the always-loaded self.

Release it any time with `/leave-bubble` (or `uv run vape bubble leave`).
