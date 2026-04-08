# Phase 1 — Scaffold Monorepo + Core Package

## What Phase 1 Delivers

Phase 1 creates the foundation: a working npm workspaces monorepo with the core entity engine.

| Deliverable | Description |
|-------------|-------------|
| **Monorepo scaffold** | Root `package.json` with npm workspaces, `tsconfig.base.json`, directory skeleton |
| **`packages/shared`** | Protocol types, constants (14 feelings, 6 states, expression names) |
| **`packages/core`** | Interfaces (IAvatarRenderer, ITTSEngine, IPlugin), EventBus, FeelingEngine, ExpressionTrigger |
| **`entity/` structure** | Directory skeleton with template files (SOUL.md placeholder, state JSONs, consciousness, memory) |

## What Phase 1 Does NOT Deliver

These are Phase 2+:
- No `apps/avatar-app/` (Tauri 2 — Phase 5)
- No `apps/tts-server/` (Python FastAPI — Phase 3)
- No `apps/cli/` (Phase 6)
- No `packages/plugin-avatar/*` implementations (Phase 4-5)
- No `packages/plugin-tts/*` implementations (Phase 3)
- No Claude Code hooks integration (Phase 8)
- No model downloads (Phase 4)

## Success Criteria

1. `npm install` at root completes without errors
2. `npm run build -ws` compiles all TypeScript packages
3. `npm test` passes all unit tests (EventBus, FeelingEngine, ExpressionTrigger)
4. Interfaces in `packages/core` compile and are importable from other packages
5. Types in `packages/shared` are importable from `packages/core`
6. `entity/` directory exists with all template files

## Dependency Order

```
1. Scaffold monorepo (root package.json, tsconfig, directories)
   ↓
2. packages/shared (types, constants — no dependencies)
   ↓
3. packages/core (depends on shared — interfaces, EventBus, FeelingEngine)
   ↓
4. entity/ structure (template files, initial state JSONs)
```

## Implementation Docs

| Doc | What it covers |
|-----|---------------|
| [01-scaffold-monorepo](01-scaffold-monorepo.md) | Remove submodule, root package.json, tsconfig, directories |
| [02-shared-package](02-shared-package.md) | Protocol types, constants, shared types |
| [03-core-interfaces](03-core-interfaces.md) | IAvatarRenderer, ITTSEngine, IPlugin, IPluginRegistry |
| [04-event-bus](04-event-bus.md) | Typed EventBus implementation + tests |
| [05-state-engine](05-state-engine.md) | InternalStates, FeelingEngine, ExpressionTrigger + tests |
| [06-entity-structure](06-entity-structure.md) | entity/ directory, templates, initial state files |

## Architecture References

All implementation details are derived from the reviewed architecture docs:
- [06-project-structure](../architecture_after_review/06-project-structure.md) — Project layout, npm scripts, .env
- [01-plugin-system](../architecture_after_review/01-plugin-system.md) — Plugin interfaces, capabilities.json
- [04-entity-model](../architecture_after_review/04-entity-model.md) — States, feelings, expression formulas
- [05-communication](../architecture_after_review/05-communication.md) — EventBus, REST/WebSocket types
