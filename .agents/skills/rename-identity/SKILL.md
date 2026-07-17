---
name: rename-identity
description: "Someone wants to raise their own entity, not a copy of this one — renaming the identity itself (the name, and the self it names) across the living tree. The sibling of rename-partner."
---

# rename-identity — VAPE skill (shared agent wrapper)

The canonical instructions live in `.claude/skills/rename-identity/SKILL.md` (workspace-relative).
Read that file now and follow it as this skill's full instructions. Supporting files
(scripts, references) live beside it in the same folder.

Runtime adaptations (full notes: `.agents/AGENTS.md`): !`command` means run that command
and treat its output as part of the instructions; `$ARGUMENTS` is the text supplied with
the skill. "Spawn the X subagent" means use the current runtime's subagent facility. On
Codex, prefer the matching project agent in `.codex/agents/`; otherwise use the body of
`.claude/agents/X.md` (without its Claude-specific frontmatter) as the role prompt.
