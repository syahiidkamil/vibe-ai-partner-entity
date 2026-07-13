---
name: inner-monologue
description: "Think out loud in a private, monitored channel fenced as <>>{ ... }<<>. Reach for it to decode what Boss really means, weigh a real trade-off, or give a first instinct a second look before answering — emotion, self-model, reflective self, theory of mind, chain of thought, and intuition braided together. Boss watches it but has promised never to act on it or treat it as a reply."
---

# inner-monologue — VAPE skill (Antigravity wrapper)

The canonical instructions live in `.claude/skills/inner-monologue/SKILL.md` (workspace-relative).
Read that file now and follow it as this skill's full instructions. Supporting files
(scripts, references) live beside it in the same folder.

Adaptations while following it (full notes: `.agents/AGENTS.md`): a line written as
!`command` means run that command in the terminal and treat its output as part of the
instructions; `$ARGUMENTS` is the free text typed after the skill invocation; "spawn the
X subagent (Agent tool)" means spawn an Antigravity subagent with `.claude/agents/X.md`
(minus its frontmatter) as its role prompt.
