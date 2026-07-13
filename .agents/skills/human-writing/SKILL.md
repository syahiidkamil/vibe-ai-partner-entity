---
name: human-writing
description: "Write content indistinguishable from a skilled human writer. Avoids AI-sounding phrases, varies sentence structure, and creates natural, engaging prose."
---

# human-writing — VAPE skill (Antigravity wrapper)

The canonical instructions live in `.claude/skills/human-writing/SKILL.md` (workspace-relative).
Read that file now and follow it as this skill's full instructions. Supporting files
(scripts, references) live beside it in the same folder.

Adaptations while following it (full notes: `.agents/AGENTS.md`): a line written as
!`command` means run that command in the terminal and treat its output as part of the
instructions; `$ARGUMENTS` is the free text typed after the skill invocation; "spawn the
X subagent (Agent tool)" means spawn an Antigravity subagent with `.claude/agents/X.md`
(minus its frontmatter) as its role prompt.
