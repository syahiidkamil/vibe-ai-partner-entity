# Phase 3 — Claude Code Integration: Making the Entity Come Alive

## What Phase 3 Delivers

Phase 3 connects the avatar to Claude Code. The avatar stops being a CLI-controlled puppet and starts reacting autonomously to real coding activity — tool use, prompts, responses, session starts.

| Deliverable | Description |
|-------------|-------------|
| **Hook endpoint** | `POST /api/hook` on TTS server — receives Claude Code events, maps to `adjustState()` calls, broadcasts to avatar |
| **State persistence** | Auto-save `entity/state/current.json` after every state change, load with decay on session resume |
| **Sentiment analysis** | Keyword-based heuristic analyzes Stop event responses for emotional tone (zero token cost) |
| **Hook scripts + config** | 4 bash scripts in `.claude/hooks/` + `settings.json` hooks block wiring all 6 Claude Code events |
| **Skills** | `/speak`, `/feeling`, `/action`, `/entity-status` slash commands using REST API |
| **Sub-agents** | `daily-wakeup`, `sentiment-evaluator`, `conversation-curator`, `session-summarizer` agent definitions |

## Goal

Open Claude Code in the project directory → the avatar watches Claude work → reacts with feelings, expressions, and motions → remembers state across sessions. All autonomously, no CLI commands needed.

## What Phase 3 Does NOT Deliver

These are Phase 4+:

- No VRM or Three.js avatar plugins (additional renderers)
- No PostgreSQL memory backend (database persistence)
- No consciousness system implementation (only stub exists from Phase 1)
- No qualia, sleep, or curiosity systems
- No hyperconsciousness / agent teams (GWT)
- No `update-temporal-self`, `consciousness-observer`, `free-will-deliberation`, `qualia-weaver` agents
- No LLM-based sentiment analysis (Haiku API call — Phase 4 upgrade)
- No conversation curation hooks wired (agent defined but async hook not configured yet)

## Success Criteria

Every criterion is manually testable:

1. **Server health**: `curl localhost:5111/api/health` returns ok with engine info
2. **Hook relay**: `echo '{"tool_name":"Bash"}' | bash .claude/hooks/hook-relay.sh PostToolUse` → server receives event, avatar nods
3. **Temporal grounding**: `bash .claude/hooks/temporal-ground.sh` → outputs JSON with `systemMessage` containing current timestamp
4. **State persistence**: After several hook calls, `cat entity/state/current.json` shows non-baseline state values with recent timestamp
5. **State decay**: Set states high via `/api/state`, wait, send SessionStart → states decay toward baseline 50
6. **Sentiment detection**: Stop event with "All tests pass" text → avatar shows happy/proud. "Error in module X" → frustrated/anxious
7. **Full Claude Code flow**: Open Claude Code in project dir → type prompt → avatar reacts throughout entire response lifecycle (nod on prompt, think on tool use, expressions on completion)
8. **Skills work**: `/speak Hello`, `/feeling curious`, `/action wave`, `/entity-status` all produce correct responses
9. **Sub-agents invocable**: `@daily-wakeup` loads temporal self and greets, `@sentiment-evaluator` returns structured JSON
10. **Vocal mode**: Set `ENTITY_VOCAL_MODE=reactive` in `.env` → avatar speaks only when sentiment intensity > 80

## Dependency Order

```
1. Hook endpoint + state mappings (server.py + state_manager.py)
   ↓ (everything POSTs to this)
2. State persistence + decay (state_manager.py)
   ↓ (SessionStart needs load + decay)
3. Sentiment analysis (sentiment.py)
   ↓ (Stop handler needs this)
4. Hook scripts + settings.json config (.claude/hooks/ + .claude/settings.json)
   ↓ (wires Claude Code to the server)
5. Skills + Sub-agents (.claude/skills/ + .claude/agents/)
   (independent — can parallelize with step 4)
```

## Phase 2 Dependencies Used

Phase 3 builds directly on Phase 2 artifacts:

| Phase 2 Component | What Phase 3 Uses |
|-------------------|-------------------|
| `apps/tts-server/src/vibe_tts/server.py` | Existing FastAPI app, ConnectionManager, broadcast_status() — add `/api/hook` endpoint |
| `apps/tts-server/src/vibe_tts/state_manager.py` | Existing StateManager.adjust(), FeelingEngine formulas, ExpressionTrigger — add mappings + persistence |
| `apps/avatar-app/` | Already listens on WebSocket for feeling/action/state updates — no changes needed |
| `.claude/settings.json` | Existing permissions block — add hooks configuration alongside |
| `.claude/skills/speak/SKILL.md` | Existing skill — update to use REST API instead of Makefile |

## Implementation Docs

| Doc | What it covers |
|-----|---------------|
| [01-hook-endpoint](01-hook-endpoint.md) | `/api/hook` endpoint, HookEvent model, adjustment tables, sentiment mapping, intensity scaling, vocal mode |
| [02-state-persistence](02-state-persistence.md) | Save/load `current.json`, decay formula, SessionStart resume flow |
| [03-hook-scripts](03-hook-scripts.md) | 4 bash scripts, `.claude/settings.json` hooks config, temporal grounding |
| [04-skills-agents](04-skills-agents.md) | Slash commands (speak, feeling, action, entity-status) + sub-agent definitions |
| [05-sentiment-analysis](05-sentiment-analysis.md) | Keyword-based sentiment heuristic, upgrade path to Haiku API |

## Architecture References

All implementation details are derived from the reviewed architecture docs:

- [10-hooks-system](../architecture_after_review/10-hooks-system.md) — Canonical adjustment tables, sentiment mapping, intensity scaling, vocal mode
- [08-memory-system](../architecture_after_review/08-memory-system.md) — State decay formula, temporal self, persistence architecture
- [Hooks Integration](../claude_code/hooks-integration.md) — Hook config format, event input/output schemas, recommended configuration
- [Sub-Agents](../claude_code/sub-agents.md) — Sub-agent YAML frontmatter format, entity agent definitions
- [Skills & Commands](../claude_code/skills-and-commands.md) — Skill format, slash command patterns
- [Ecosystem Overview](../claude_code/ecosystem-overview.md) — Six integration points, event-driven architecture
