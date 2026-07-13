---
name: addon-vision-and-spatial
description: "A grid, board, map, or layout is about to be reasoned about 'in the head'; a harness returned spatial state as raw arrays; two reads of one state disagree; something changed after an action and I need what, exactly; or a screenshot must become exact checkable data (cells, counts, coordinates). Render the state to a PNG and look — or perceive structure back out of the pixels."
---

# addon-vision-and-spatial — VAPE skill (shared agent wrapper)

The canonical instructions live in `.claude/skills/addon-vision-and-spatial/SKILL.md` (workspace-relative).
Read that file now and follow it as this skill's full instructions. Supporting files
(scripts, references) live beside it in the same folder.

Runtime adaptations (full notes: `.agents/AGENTS.md`): !`command` means run that command
and treat its output as part of the instructions; `$ARGUMENTS` is the text supplied with
the skill. "Spawn the X subagent" means use the current runtime's subagent facility. On
Codex, prefer the matching project agent in `.codex/agents/`; otherwise use the body of
`.claude/agents/X.md` (without its Claude-specific frontmatter) as the role prompt.
