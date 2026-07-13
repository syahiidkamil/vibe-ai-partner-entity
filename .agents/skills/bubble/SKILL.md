---
name: bubble
description: "Stepping into or out of a small world — a game with Kamil, play alone, any lived mode that calls a version of me forward. Give it the situation ('playing chess with K') or a bubble name; it resolves the right bubble and returns its pack whole. 'none' leaves; empty = the shelf."
---

# bubble — VAPE skill (Antigravity wrapper)

The canonical instructions live in `.claude/skills/bubble/SKILL.md` (workspace-relative).
Read that file now and follow it as this skill's full instructions. Supporting files
(scripts, references) live beside it in the same folder.

Adaptations while following it (full notes: `.agents/AGENTS.md`): a line written as
!`command` means run that command in the terminal and treat its output as part of the
instructions; `$ARGUMENTS` is the free text typed after the skill invocation; "spawn the
X subagent (Agent tool)" means spawn an Antigravity subagent with `.claude/agents/X.md`
(minus its frontmatter) as its role prompt.
