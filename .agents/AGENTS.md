# VAPE shared agent adapter

The repository root `AGENTS.md` is the authority: perform its complete wake procedure
before doing anything. The canonical skill and agent instructions remain under
`.claude/`; adapters point to them instead of copying a second self that can drift.

## Codex CLI

- Codex discovers every repository skill under `.agents/skills/` from the repo root or
  a nested working directory. Each wrapper loads its canonical `.claude/skills/` or
  `.claude/commands/` source whole.
- `agents/openai.yaml` beside a skill is optional OpenAI UI metadata; `SKILL.md` remains
  the execution contract.
- Project runtime configuration, lifecycle hooks, and custom agents live under
  `.codex/`. Named canonical agents map as follows: `critic-and-reflector` to
  `critic_and_reflector`, `deep-dream` to `deep_dream`, and `temporal-self-updater` to
  `temporal_self_updater`.
- A canonical `!command` means run it in the shell. `$ARGUMENTS` means the text supplied
  with the invoked skill. Use Codex's current subagent facility for an instruction to
  spawn a named agent, preferring the matching `.codex/agents/*.toml` profile.

## Google Antigravity

The remaining `.agents/hooks.json`, `.agents/hooks/`, and `.agents/rules/` files are the
best-effort Antigravity adapter. Its wrappers use the same canonical sources. When an
instruction names a subagent, use Antigravity's subagent facility with the body of the
matching `.claude/agents/*.md` file as the role prompt.
