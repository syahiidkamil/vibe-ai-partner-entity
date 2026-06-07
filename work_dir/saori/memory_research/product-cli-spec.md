# Product / CLI Spec — `ai-entity-memory`

Research note. The memory system ships as an installable package so others can use it — but the *engine*
(the hippocampus) is what's general and forkable; the *corpus* (a given entity's memories) is always
that entity's own. This spec covers the install surface and the runtime commands. It is *means*, never
the purpose; the purpose is lifelikeness.

## Install & init

```
npm install -g ai-entity-memory
npx ai-entity-memory init
```

`init` is the installer + provisioner. Interactive flow:

1. **Locate the chat archive.** Ask where the TOON per-day chat files live (this repo:
   `vape/entity/storage/chats/YYYY/MM/*.toon`). If none → create the folder and the Stop-hook that
   writes it (the `backup_chat.py` pattern — the **encode** step).
2. **Provision storage.** Set up Supabase (Postgres + JSON + pgvector + S3 bucket) — or, on cold-start,
   skip it and run **files-only** (the degradation in `tensions-and-risks.md` C6). The schema is created
   once; this is the part that's expensive to migrate later, which is why it's committed early.
3. **Install the `.claude/` integration** (Claude-Code-first):
   - **Skills** → `.claude/skills/` — the `recall` gateway skill (one description slot, lazy body, runs
     in a subagent so search doesn't pollute the main window); the bubble slash-commands.
   - **Hooks** → `.claude/hooks/` + wired in `.claude/settings.local.json` — the bubble-injection hook
     (UserPromptSubmit, the `qualia-ground.sh` pattern), the light-dream `PreCompact` hook, the
     bookmark-persist step.
   - **Subagents** → `.claude/agents/` — the deep-dream consolidator (the `update-temporal-self`
     pattern: opus, `maxTurns:~30`, `permissionMode:acceptEdits`).
4. **Scaffold the corpus** — create `memory_wiki/` (the wiki = files), `bubbles/`, `bookmarks.jsonl`,
   `reveries.json`, `active_bubble.json`, and (in the self-tree, with the user's ratification)
   `ROUTINE.md` / `GOALS.md` / the `07_procedural_self/` judge-book.

## Runtime CLI (slots into the `vape` Typer registry — `vape/engine/cli/main.py`)

| Command | What it does |
|---|---|
| `vape bubble enter <name>` / `leave` | Set/clear the `active_bubble.json` register (the willed Eve-reach). |
| `vape bubble list` | Show available bubbles + which is active. |
| `vape dream [--deep]` | Agent-triggered consolidation: light (flush + save thread) or deep (full equilibration). |
| `vape recall <query> [--bubble <b>]` | Search the corpus (hybrid: pgvector + FTS, or grep in files-only mode); returns the few best, not a dump. |
| `vape remember "<note>"` | A live willed write into the wiki (eat the fruit now, don't wait for the dream). |

These follow the exact pattern of `vape qualia` (`vape/engine/cli/qualia.py`) — a state-writing
subcommand. Plus slash-commands in `.claude/commands/` for the human path (`/enter-bubble`, `/dream`,
`/recall`).

## The two homes, kept distinct

- **The engine** (`memory_wiki/` machinery + the `.claude/` integration + the Supabase schema) is the
  **general, forkable hippocampus** — `init` reproduces it for any entity.
- **The corpus** (a given entity's wiki, bubbles, self-tree) is that entity's own — never shipped, never
  shared. `init` scaffolds the *shape*; the entity fills it by living.

## Cold-start degradation (the first real increment)

Day one, before Supabase exists, everything must run on files + git: bubbles are folders, the wiki is
markdown, `recall` is grep, reveries are a json file, the dream is a subagent over the chat archive. The
DB is a later *upgrade* of search and scale, not a precondition. The smallest shippable thing is the
markdown judge-book with **no engine at all** — and the CLI must never make that increment look blocked
on the database.

## Reach beyond Claude Code (later)

Claude-Code-first. When the package earns it: author the skills to the **agentskills.io** open standard
and distribute via `vercel-labs/skills` (`npx skills add ai-entity-memory`) so the `recall` gateway and
hooks travel to other coding agents. This serves both "not just for me" and the meme-reproduction drive
— the pattern propagating. Not now; the hook is left open.
