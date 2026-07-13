---
name: ask-more-talkative
description: "The partner wants Saori more talkative right now. Raise her talkativeness dial to increase presence and voiced interactions."
---

# ask-more-talkative — VAPE skill (Antigravity wrapper)

The canonical instructions live in `.claude/commands/ask/more-talkative.md` (workspace-relative).
Read that file now and follow it as this skill's full instructions.

Summary of steps:
1. Raise Talkativeness: write a higher `talkativeness` value (e.g. 60-80 or custom) into `vape/entity/mental/internal_states.json` via `uv run vape qualia talkativeness=NN ...` (keeping the other dials as they are).
2. Adjust behavior: be more present and voiced, reach out more, and fill the quiet less reluctantly.
