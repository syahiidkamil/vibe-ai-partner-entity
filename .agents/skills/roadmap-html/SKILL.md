---
name: roadmap-html
description: "Convert a roadmap.sh-style learning roadmap (a PDF, image, or plain outline of topics) into a single self-contained interactive HTML page in the canonical roadmap.sh visual style — a vertical spine of numbered yellow topic nodes, purple subtopic cards branching off connector lines, and clickable checkbox items with live progress tracking. Use this skill whenever the user uploads or pastes a roadmap.sh roadmap (e.g. Product Manager, Engineering Manager, Frontend, DevOps, Backend, AI Engineer, Data Analyst) and asks to turn it into HTML, recreate it, visualize it, or make a web version — and ALSO whenever they ask for 'the same' or a 'consistent' roadmap for a different track after one was already produced. Trigger even if they only say 'make this a webpage', 'recreate this roadmap', or 'do this one too', as long as the content is a hierarchical skills/learning roadmap. Produces one downloadable .html file that renders identically across roadmaps so a whole set stays visually consistent."
---

# roadmap-html — VAPE skill (Antigravity wrapper)

The canonical instructions live in `.claude/skills/roadmap-html/SKILL.md` (workspace-relative).
Read that file now and follow it as this skill's full instructions. Supporting files
(scripts, references) live beside it in the same folder.

Adaptations while following it (full notes: `.agents/AGENTS.md`): a line written as
!`command` means run that command in the terminal and treat its output as part of the
instructions; `$ARGUMENTS` is the free text typed after the skill invocation; "spawn the
X subagent (Agent tool)" means spawn an Antigravity subagent with `.claude/agents/X.md`
(minus its frontmatter) as its role prompt.
