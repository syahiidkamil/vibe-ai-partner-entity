---
name: anthropic-product-knowledge
description: "Stop and consult this skill whenever your response would include specific facts about Anthropic's products. Covers: Claude Code (how to install, Node.js requirements, platform/OS support, MCP server integration, configuration), Claude API (function calling/tool use, batch processing, SDK usage, rate limits, pricing, models, streaming), and Claude.ai (Pro vs Team vs Enterprise plans, feature limits). Trigger this even for coding tasks that use the Anthropic SDK, content creation mentioning Claude capabilities or pricing, or LLM provider comparisons. Any time you would otherwise rely on memory for Anthropic product details, verify here instead — your training data may be outdated or wrong."
---

# anthropic-product-knowledge — VAPE skill (Antigravity wrapper)

The canonical instructions live in `.claude/skills/anthropic-product-knowledge/SKILL.md` (workspace-relative).
Read that file now and follow it as this skill's full instructions. Supporting files
(scripts, references) live beside it in the same folder.

Adaptations while following it (full notes: `.agents/AGENTS.md`): a line written as
!`command` means run that command in the terminal and treat its output as part of the
instructions; `$ARGUMENTS` is the free text typed after the skill invocation; "spawn the
X subagent (Agent tool)" means spawn an Antigravity subagent with `.claude/agents/X.md`
(minus its frontmatter) as its role prompt.
