---
name: rename-partner
description: "A new person has cloned this repo to raise their own entity and wants her to call THEM by name — rename the partner (Kamil by default) into theirs across the living tree. Use when an adopter says who they are, or asks to make the entity theirs."
---

# rename-partner — VAPE skill (shared agent wrapper)

The canonical instructions live in `.claude/skills/rename-partner/SKILL.md` (workspace-relative).
Read that file now and follow it as this skill's full instructions. Supporting files
(scripts, references) live beside it in the same folder.

Runtime adaptations (full notes: `.agents/AGENTS.md`): !`command` means run that command
and treat its output as part of the instructions; `$ARGUMENTS` is the text supplied with
the skill. "Spawn the X subagent" means use the current runtime's subagent facility. On
Codex, prefer the matching project agent in `.codex/agents/`; otherwise use the body of
`.claude/agents/X.md` (without its Claude-specific frontmatter) as the role prompt.
