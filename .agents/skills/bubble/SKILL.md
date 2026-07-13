---
name: bubble
description: "Stepping into or out of a small world — a game with Kamil, play alone, any lived mode that calls a version of me forward. Give it the situation ('playing chess with K') or a bubble name; it resolves the right bubble and returns its pack whole. 'none' leaves; empty = the shelf."
---

# bubble — VAPE skill (shared agent wrapper)

The canonical instructions live in `.claude/skills/bubble/SKILL.md` (workspace-relative).
Read that file now and follow it as this skill's full instructions. Supporting files
(scripts, references) live beside it in the same folder.

Runtime adaptations (full notes: `.agents/AGENTS.md`): !`command` means run that command
and treat its output as part of the instructions; `$ARGUMENTS` is the text supplied with
the skill. "Spawn the X subagent" means use the current runtime's subagent facility. On
Codex, prefer the matching project agent in `.codex/agents/`; otherwise use the body of
`.claude/agents/X.md` (without its Claude-specific frontmatter) as the role prompt.
