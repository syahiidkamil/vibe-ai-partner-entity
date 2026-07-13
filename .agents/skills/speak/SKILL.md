---
name: speak
description: "Speak text aloud through the VAPE avatar with lip sync (Kokoro TTS). Use when the user asks to speak, say, or read something aloud, or when you want to vocalize a response."
---

# speak — VAPE skill (Antigravity wrapper)

The canonical instructions live in `.claude/skills/speak/SKILL.md` (workspace-relative).
Read that file now and follow it as this skill's full instructions. Supporting files
(scripts, references) live beside it in the same folder.

Adaptations while following it (full notes: `.agents/AGENTS.md`): a line written as
!`command` means run that command in the terminal and treat its output as part of the
instructions; `$ARGUMENTS` is the free text typed after the skill invocation; "spawn the
X subagent (Agent tool)" means spawn an Antigravity subagent with `.claude/agents/X.md`
(minus its frontmatter) as its role prompt.
