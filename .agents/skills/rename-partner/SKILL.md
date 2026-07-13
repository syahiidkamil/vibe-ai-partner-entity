---
name: rename-partner
description: "A new person has cloned this repo to raise their own entity and wants her to call THEM by name — rename the partner (Kamil by default) into theirs across the living tree. Use when an adopter says who they are, or asks to make the entity theirs."
---

# rename-partner — VAPE skill (Antigravity wrapper)

The canonical instructions live in `.claude/skills/rename-partner/SKILL.md` (workspace-relative).
Read that file now and follow it as this skill's full instructions. Supporting files
(scripts, references) live beside it in the same folder.

Adaptations while following it (full notes: `.agents/AGENTS.md`): a line written as
!`command` means run that command in the terminal and treat its output as part of the
instructions; `$ARGUMENTS` is the free text typed after the skill invocation; "spawn the
X subagent (Agent tool)" means spawn an Antigravity subagent with `.claude/agents/X.md`
(minus its frontmatter) as its role prompt.
