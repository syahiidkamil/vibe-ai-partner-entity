# Phase 1 — Shared Package (`packages/shared`)

## What This Delivers

The shared package contains **zero dependencies** — pure TypeScript types, constants, and protocol definitions that every other package imports. Nothing here runs. It just defines the vocabulary the entire system speaks.

```
packages/shared/
├── package.json
├── tsconfig.json
└── src/
    ├── constants.ts    # Canonical names, defaults, baselines
    ├── types.ts        # Core type definitions
    ├── protocol.ts     # REST + WebSocket message types
    └── index.ts        # Barrel export
```

---

## `packages/shared/package.json`

```json
{
  "name": "@vibe-ai-partner/shared",
  "version": "0.1.0",
  "type": "module",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "scripts": {
    "build": "tsc",
    "test": "echo 'No tests — types only'"
  },
  "files": ["dist"]
}
```

No dependencies. No devDependencies (TypeScript comes from the root workspace).

---

## `packages/shared/tsconfig.json`

```json
{
  "extends": "../../tsconfig.base.json",
  "compilerOptions": {
    "outDir": "dist",
    "rootDir": "src"
  },
  "include": ["src"]
}
```

Inherits strict settings from root `tsconfig.base.json`.

---

## `src/constants.ts` — All Canonical Names

```typescript
// ─── Feelings ────────────────────────────────────────────────
// 14 universal feelings derived from internal states via the FeelingEngine.
// Each feeling is 0-100. Multiple feelings coexist simultaneously.
// Models declare which subset they support via capabilities.json.

export const FEELING_NAMES = [
  "happy",
  "sad",
  "frustrated",
  "curious",
  "proud",
  "anxious",
  "excited",
  "calm",
  "bored",
  "guilty",
  "angry",
  "blushing",
  "surprised",
  "relieved",
] as const;

export type FeelingName = (typeof FEELING_NAMES)[number];

// ─── Internal States ─────────────────────────────────────────
// 6 epistemic variables that describe what the AI knows about its situation.
// These are NOT emotions — feelings are derived from these states.

export const STATE_NAMES = [
  "confidence",
  "contextSaturation",
  "alignment",
  "memoryPressure",
  "momentum",
  "trustCalibration",
] as const;

export type StateName = (typeof STATE_NAMES)[number];

// ─── Expression Groups ───────────────────────────────────────
// Self-expressions are one-shot motions organized by category.

export const EXPRESSION_GROUPS = [
  "emotional",
  "social",
  "reaction",
  "combo",
] as const;

export type ExpressionGroup = (typeof EXPRESSION_GROUPS)[number];

// ─── State Defaults ──────────────────────────────────────────
// All states start at 50 (baseline equilibrium).
// States decay toward this value over time when not actively adjusted.

export const STATE_BASELINE = 50;

export const DEFAULT_STATE_VALUES: Record<StateName, number> = {
  confidence: STATE_BASELINE,
  contextSaturation: STATE_BASELINE,
  alignment: STATE_BASELINE,
  memoryPressure: STATE_BASELINE,
  momentum: STATE_BASELINE,
  trustCalibration: STATE_BASELINE,
};
```

---

## `src/types.ts` — Core Type Definitions

```typescript
import type { FeelingName, StateName } from "./constants.js";

// ─── Internal States ─────────────────────────────────────────
// Record of the 6 epistemic states, each 0-100.

export type InternalStates = Record<StateName, number>;

// ─── Feeling Map ─────────────────────────────────────────────
// Record of 14 feelings, each 0-100.
// All feelings are present simultaneously — multiple feelings coexist.

export type FeelingMap = Record<FeelingName, number>;

// ─── State Adjustment ────────────────────────────────────────
// Used by hooks and commands to increment/decrement states.
// Delta is additive: confidence at 70 + delta +5 = 75.

export interface StateAdjustment {
  state: StateName;
  delta: number;
}

// ─── Expression Trigger Result ───────────────────────────────
// Returned when a feeling crosses a threshold and fires an expression.

export interface ExpressionTriggerResult {
  expression: string;
  feeling: FeelingName;
  intensity: number;
}

// ─── Plugin Type ─────────────────────────────────────────────
// The three categories of swappable plugins.

export type PluginType = "avatar-renderer" | "tts-engine" | "memory-backend";

// ─── Vocal Mode ──────────────────────────────────────────────
// Controls how the entity uses TTS.
// silent: no speech. reactive: speaks when spoken to. conversational: speaks proactively.

export type VocalMode = "silent" | "reactive" | "conversational";
```

---

## `src/protocol.ts` — REST + WebSocket Message Types

```typescript
import type { FeelingName, StateName } from "./constants.js";
import type { InternalStates, FeelingMap, StateAdjustment } from "./types.js";

// ═══════════════════════════════════════════════════════════════
// REST Request/Response Types (Layer 1: HTTP)
// ═══════════════════════════════════════════════════════════════

// POST /api/speak
export interface SpeakRequest {
  text: string;
  voice?: string;
  speed?: number;
}

// POST /api/feeling
export interface FeelingRequest {
  name: FeelingName;
}

// POST /api/action
export interface ActionRequest {
  name: string;
}

// POST /api/state
export interface StateAdjustRequest {
  adjustments: StateAdjustment[];
}

// GET /api/health
export interface HealthResponse {
  status: "ok" | "error";
  engine: string;
  uptime: number;
}

// GET /api/state, POST /api/state response
export interface StateResponse {
  states: InternalStates;
  feelings: FeelingMap;
  expressionsTriggered: string[];
}

// ═══════════════════════════════════════════════════════════════
// WebSocket Message Types (Layer 2: Real-time)
// ═══════════════════════════════════════════════════════════════

// ─── Status channel (/ws/status) ─────────────────────────────

export interface WSStateUpdate {
  type: "state";
  mode: string;
  mood: string;
}

export interface WSAmplitude {
  type: "amplitude";
  value: number;
  timestamp: number;
}

export interface WSFeelingUpdate {
  type: "feeling";
  name: FeelingName;
}

export interface WSActionUpdate {
  type: "action";
  name: string;
}

// Union of all status channel messages
export type WSStatusMessage =
  | WSStateUpdate
  | WSAmplitude
  | WSFeelingUpdate
  | WSActionUpdate;

// ─── Audio channel (/ws/audio) ───────────────────────────────

export interface WSAudioChunk {
  type: "audio_chunk";
  data: string; // base64-encoded PCM
  sampleRate: number;
  isLast: boolean;
}

// ─── Expression fired (event bus → WebSocket) ────────────────

export interface WSExpressionFired {
  type: "expression_fired";
  expression: string;
  feeling: FeelingName;
  intensity: number;
}

// ─── Union of all WebSocket messages ─────────────────────────

export type WSMessage =
  | WSStatusMessage
  | WSAudioChunk
  | WSExpressionFired;
```

---

## `src/index.ts` — Barrel Export

```typescript
// Constants
export {
  FEELING_NAMES,
  STATE_NAMES,
  EXPRESSION_GROUPS,
  STATE_BASELINE,
  DEFAULT_STATE_VALUES,
} from "./constants.js";

export type { FeelingName, StateName, ExpressionGroup } from "./constants.js";

// Core types
export type {
  InternalStates,
  FeelingMap,
  StateAdjustment,
  ExpressionTriggerResult,
  PluginType,
  VocalMode,
} from "./types.js";

// Protocol types
export type {
  SpeakRequest,
  FeelingRequest,
  ActionRequest,
  StateAdjustRequest,
  HealthResponse,
  StateResponse,
  WSMessage,
  WSAmplitude,
  WSStateUpdate,
  WSFeelingUpdate,
  WSActionUpdate,
  WSStatusMessage,
  WSAudioChunk,
  WSExpressionFired,
} from "./protocol.js";
```

---

## Verification

After creating all files, verify:

```bash
# From project root
cd packages/shared

# 1. TypeScript compiles with no errors
npx tsc --noEmit
# Expected: no output (clean compile)

# 2. Build produces dist/
npm run build
ls dist/
# Expected: constants.js, constants.d.ts, types.js, types.d.ts,
#           protocol.js, protocol.d.ts, index.js, index.d.ts

# 3. Constants are correct counts
node -e "
  const { FEELING_NAMES, STATE_NAMES, EXPRESSION_GROUPS } = require('./dist/index.js');
  console.assert(FEELING_NAMES.length === 14, 'Expected 14 feelings, got ' + FEELING_NAMES.length);
  console.assert(STATE_NAMES.length === 6, 'Expected 6 states, got ' + STATE_NAMES.length);
  console.assert(EXPRESSION_GROUPS.length === 4, 'Expected 4 groups, got ' + EXPRESSION_GROUPS.length);
  console.log('All counts correct');
"

# 4. DEFAULT_STATE_VALUES has all 6 states at 50
node -e "
  const { DEFAULT_STATE_VALUES, STATE_BASELINE } = require('./dist/index.js');
  const values = Object.values(DEFAULT_STATE_VALUES);
  console.assert(values.length === 6, 'Expected 6 default values');
  console.assert(values.every(v => v === STATE_BASELINE), 'All defaults should be ' + STATE_BASELINE);
  console.log('Defaults correct');
"
```

### Checklist

- [ ] `package.json` has no dependencies (types-only package)
- [ ] `tsconfig.json` extends root `tsconfig.base.json`
- [ ] `FEELING_NAMES` has exactly 14 entries
- [ ] `STATE_NAMES` has exactly 6 entries
- [ ] `EXPRESSION_GROUPS` has 4 entries: emotional, social, reaction, combo
- [ ] `DEFAULT_STATE_VALUES` maps all 6 states to `STATE_BASELINE` (50)
- [ ] `InternalStates` is `Record<StateName, number>`
- [ ] `FeelingMap` is `Record<FeelingName, number>`
- [ ] REST types match the endpoints in [05-communication](../architecture_after_review/05-communication.md)
- [ ] WebSocket types match the message shapes in [05-communication](../architecture_after_review/05-communication.md)
- [ ] Barrel export re-exports everything
- [ ] `npx tsc --noEmit` passes with zero errors
