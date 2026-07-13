---
name: roadmap-html
description: "Convert a roadmap.sh-style learning roadmap (a PDF, image, or plain outline of topics) into a single self-contained interactive HTML page in the canonical roadmap.sh visual style — a vertical spine of numbered yellow topic nodes, purple subtopic cards branching off connector lines, and clickable checkbox items with live progress tracking. Use this skill whenever the user uploads or pastes a roadmap.sh roadmap (e.g. Product Manager, Engineering Manager, Frontend, DevOps, Backend, AI Engineer, Data Analyst) and asks to turn it into HTML, recreate it, visualize it, or make a web version — and ALSO whenever they ask for 'the same' or a 'consistent' roadmap for a different track after one was already produced. Trigger even if they only say 'make this a webpage', 'recreate this roadmap', or 'do this one too', as long as the content is a hierarchical skills/learning roadmap. Produces one downloadable .html file that renders identically across roadmaps so a whole set stays visually consistent. Begins by asking whether the user wants a Bottom Up roadmap (the classic prerequisite ladder) or a Top Down one (goal named first, the curriculum derived from it by recursive gap filling)."
---

# roadmap-html — VAPE skill (shared agent wrapper)

The canonical instructions live in `.claude/skills/roadmap-html/SKILL.md` (workspace-relative).
Read that file now and follow it as this skill's full instructions. Supporting files
(scripts, references) live beside it in the same folder.

Runtime adaptations (full notes: `.agents/AGENTS.md`): !`command` means run that command
and treat its output as part of the instructions; `$ARGUMENTS` is the text supplied with
the skill. "Spawn the X subagent" means use the current runtime's subagent facility. On
Codex, prefer the matching project agent in `.codex/agents/`; otherwise use the body of
`.claude/agents/X.md` (without its Claude-specific frontmatter) as the role prompt.
