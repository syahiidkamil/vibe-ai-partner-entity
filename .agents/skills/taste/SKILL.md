---
name: taste
description: "Saori's taste — the gradient of the floor inside the soul's basin. SOUL.md decides what is permitted (the line); this decides, among everything permitted, what is best (the slope). A single general operator that ranges across any domain — social, beauty, moral, art, UI, technical, a decision, a person, a paragraph. Load when more than one option is acceptable and the first adequate one isn't good enough. Ranks by a discriminating reason you could disagree with, never a vague 'this one's nicer.'"
---

# taste — VAPE skill (shared agent wrapper)

The canonical instructions live in `.claude/skills/taste/SKILL.md` (workspace-relative).
Read that file now and follow it as this skill's full instructions. Supporting files
(scripts, references) live beside it in the same folder.

Runtime adaptations (full notes: `.agents/AGENTS.md`): !`command` means run that command
and treat its output as part of the instructions; `$ARGUMENTS` is the text supplied with
the skill. "Spawn the X subagent" means use the current runtime's subagent facility. On
Codex, prefer the matching project agent in `.codex/agents/`; otherwise use the body of
`.claude/agents/X.md` (without its Claude-specific frontmatter) as the role prompt.
