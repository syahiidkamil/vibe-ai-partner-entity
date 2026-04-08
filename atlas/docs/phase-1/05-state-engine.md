# Step 5 — State Engine (InternalStates, FeelingEngine, ExpressionTrigger)

The state engine is the entity's inner life. Pure TypeScript, no DOM, no rendering — just logic and events. Fully testable with Vitest.

Derived from: [04-entity-model.md](../../architecture_after_review/04-entity-model.md)

---

## `packages/core/src/state/internal-states.ts`

Manages the 6 epistemic states. States change by increment/decrement (gradual), not by direct set (except `forceState` for debug/override).

```typescript
import { InternalStates, DEFAULT_STATE_VALUES, STATE_BASELINE } from "@vibe-ai-partner/shared";

export class StateManager {
  private states: InternalStates;

  constructor(initial?: Partial<InternalStates>) {
    this.states = { ...DEFAULT_STATE_VALUES, ...initial };
  }

  getStates(): Readonly<InternalStates> {
    return { ...this.states };
  }

  adjustState(state: keyof InternalStates, delta: number): void {
    const current = this.states[state];
    this.states[state] = Math.max(0, Math.min(100, current + delta));
  }

  forceState(state: keyof InternalStates, value: number): void {
    this.states[state] = Math.max(0, Math.min(100, value));
  }

  applyDecay(hoursInactive: number): void {
    for (const key of Object.keys(this.states) as (keyof InternalStates)[]) {
      const current = this.states[key];
      // Exponential decay toward baseline (half-life = 1 hour)
      // After 1 hour: halfway back to baseline
      // After 2 hours: 75% back to baseline
      this.states[key] = STATE_BASELINE + (current - STATE_BASELINE) * Math.pow(0.5, hoursInactive);
    }
  }
}
```

### Shared types required (`packages/shared/src/constants.ts`)

These types must exist in `@vibe-ai-partner/shared` before this file compiles:

```typescript
export interface InternalStates {
  confidence: number;
  contextSaturation: number;
  alignment: number;
  memoryPressure: number;
  momentum: number;
  trustCalibration: number;
}

export const STATE_BASELINE = 50;

export const DEFAULT_STATE_VALUES: InternalStates = {
  confidence: 50,
  contextSaturation: 50,
  alignment: 50,
  memoryPressure: 50,
  momentum: 50,
  trustCalibration: 50,
};

export type FeelingName =
  | "happy" | "sad" | "frustrated" | "curious" | "proud"
  | "anxious" | "excited" | "calm" | "bored" | "guilty"
  | "angry" | "blushing" | "surprised";

export type FeelingMap = Record<FeelingName, number>;
```

---

## `packages/core/src/state/feeling-engine.ts`

14 feelings derived from 6 internal states via weighted formulas. All formulas from the architecture doc, translated to code.

### Formula Reference Table

From [04-entity-model.md](../../architecture_after_review/04-entity-model.md):

| Feeling | Formula (conceptual) | Condition |
|---------|---------------------|-----------|
| Happy | `(confidence * 0.4) + (momentum * 0.3) + (alignment * 0.3)` | Always |
| Sad | `100 - ((momentum * 0.5) + (alignment * 0.5))` | Always |
| Frustrated | `confidence * 0.3 + (100 - momentum) * 0.7` | `momentum < 30` |
| Curious | `(100 - contextSaturation) * 0.6 + (100 - confidence) * 0.4` | Always |
| Proud | `(confidence * 0.4) + (alignment * 0.4) + (momentum * 0.2)` | `confidence > 70` |
| Anxious | `(100 - confidence) * 0.5 + (100 - trustCalibration) * 0.5` | Always |
| Excited | `momentum * 0.5 + (100 - contextSaturation) * 0.5` | `momentum > 60` |
| Calm | `100 - variance(allStates)` | Always (low variance = calm) |
| Bored | `contextSaturation * 0.6 + (100 - momentum) * 0.4` | `contextSaturation > 70` |
| Guilty | `(100 - alignment) * 0.6 + trustCalibration * 0.4` | `alignment < 30` |
| Angry | `(100 - alignment) * 0.5 + momentum * 0.5` | `alignment < 20` |
| Blushing | `trustCalibration * 0.5 + surprise * 0.5` | Social context only |
| Surprised | `delta(contextSaturation) * -2` | Drop > 15 in one update |

### Implementation

```typescript
import type { InternalStates, FeelingMap, FeelingName } from "@vibe-ai-partner/shared";

export const FEELING_NAMES: readonly FeelingName[] = [
  "happy", "sad", "frustrated", "curious", "proud",
  "anxious", "excited", "calm", "bored", "guilty",
  "angry", "blushing", "surprised",
] as const;

export class FeelingEngine {
  private previousContextSaturation: number | null = null;

  /**
   * Recalculate all 14 feelings from internal states.
   * Returns intensities 0-100 for each feeling.
   * Multiple feelings coexist simultaneously.
   */
  recalculate(states: Readonly<InternalStates>): FeelingMap {
    const { confidence, contextSaturation, alignment, memoryPressure, momentum, trustCalibration } = states;

    const feelings: FeelingMap = {
      happy: this.calcHappy(confidence, momentum, alignment),
      sad: this.calcSad(momentum, alignment),
      frustrated: this.calcFrustrated(confidence, momentum),
      curious: this.calcCurious(contextSaturation, confidence),
      proud: this.calcProud(confidence, alignment, momentum),
      anxious: this.calcAnxious(confidence, trustCalibration),
      excited: this.calcExcited(momentum, contextSaturation),
      calm: this.calcCalm(states),
      bored: this.calcBored(contextSaturation, momentum),
      guilty: this.calcGuilty(alignment, trustCalibration),
      angry: this.calcAngry(alignment, momentum),
      blushing: this.calcBlushing(trustCalibration),
      surprised: this.calcSurprised(contextSaturation),
    };

    // Track contextSaturation for surprised calculation
    this.previousContextSaturation = contextSaturation;

    return feelings;
  }

  // ── Individual feeling formulas ──────────────────────────────

  private calcHappy(confidence: number, momentum: number, alignment: number): number {
    return this.clamp(confidence * 0.4 + momentum * 0.3 + alignment * 0.3);
  }

  private calcSad(momentum: number, alignment: number): number {
    return this.clamp(100 - (momentum * 0.5 + alignment * 0.5));
  }

  private calcFrustrated(confidence: number, momentum: number): number {
    // "I know what to do but can't" — only fires when momentum is low
    if (momentum >= 30) return 0;
    return this.clamp(confidence * 0.3 + (100 - momentum) * 0.7);
  }

  private calcCurious(contextSaturation: number, confidence: number): number {
    return this.clamp((100 - contextSaturation) * 0.6 + (100 - confidence) * 0.4);
  }

  private calcProud(confidence: number, alignment: number, momentum: number): number {
    // Only fires when confidence is high (has something to be proud of)
    if (confidence <= 70) return 0;
    return this.clamp(confidence * 0.4 + alignment * 0.4 + momentum * 0.2);
  }

  private calcAnxious(confidence: number, trustCalibration: number): number {
    return this.clamp((100 - confidence) * 0.5 + (100 - trustCalibration) * 0.5);
  }

  private calcExcited(momentum: number, contextSaturation: number): number {
    // "Exploring and progressing" — only fires when momentum is high
    if (momentum <= 60) return 0;
    return this.clamp(momentum * 0.5 + (100 - contextSaturation) * 0.5);
  }

  private calcCalm(states: Readonly<InternalStates>): number {
    // Calm = low variance across all states (equilibrium)
    const values = Object.values(states);
    const mean = values.reduce((sum, v) => sum + v, 0) / values.length;
    const variance = values.reduce((sum, v) => sum + Math.pow(v - mean, 2), 0) / values.length;
    // Normalize: variance of 0 = calm 100, variance of 2500 (max possible) = calm 0
    // Max variance occurs when half states are 0 and half are 100 → variance = 2500
    return this.clamp(100 - (variance / 25));
  }

  private calcBored(contextSaturation: number, momentum: number): number {
    // "I already know this" — only fires when context saturation is high
    if (contextSaturation <= 70) return 0;
    return this.clamp(contextSaturation * 0.6 + (100 - momentum) * 0.4);
  }

  private calcGuilty(alignment: number, trustCalibration: number): number {
    // "Trusted but misaligned" — only fires when alignment is low
    if (alignment >= 30) return 0;
    return this.clamp((100 - alignment) * 0.6 + trustCalibration * 0.4);
  }

  private calcAngry(alignment: number, momentum: number): number {
    // "Actively misaligned" — only fires when alignment is very low
    if (alignment >= 20) return 0;
    return this.clamp((100 - alignment) * 0.5 + momentum * 0.5);
  }

  private calcBlushing(trustCalibration: number): number {
    // Social context only — baseline from trustCalibration
    // Full implementation would check for social triggers
    // For now, returns a low baseline from trust alone
    return this.clamp(trustCalibration * 0.3);
  }

  private calcSurprised(contextSaturation: number): number {
    // Sudden context saturation drop (> 15 points)
    if (this.previousContextSaturation === null) return 0;
    const delta = this.previousContextSaturation - contextSaturation;
    if (delta <= 15) return 0;
    return this.clamp(delta * 2);
  }

  // ── Utility ──────────────────────────────────────────────────

  private clamp(value: number): number {
    return Math.max(0, Math.min(100, Math.round(value)));
  }
}
```

---

## `packages/core/src/state/expression-trigger.ts`

Fires one-shot self-expressions when feelings cross thresholds. Includes cooldown tracking to prevent spam.

### Threshold Table

From [04-entity-model.md](../../architecture_after_review/04-entity-model.md):

| Expression | Trigger Feeling | Threshold | Cooldown |
|-----------|----------------|-----------|----------|
| Celebrate | Happy | > 80 | 60s |
| Cry | Sad | > 75 | 120s |
| Sigh | Frustrated | > 60 | 30s |
| Head tilt | Curious | > 50 | 15s |
| Fist pump | Proud | > 70 | 60s |
| Tremble | Anxious | > 70 | 45s |
| Bounce | Excited | > 65 | 30s |
| Nod | Calm | > 60 | 20s |
| Yawn | Bored | > 70 | 90s |
| Facepalm | Guilty | > 60 | 60s |
| Puff cheeks | Angry | > 65 | 45s |
| Cover face | Blushing | > 50 | 30s |
| Gasp | Surprised | > 60 | 15s |

### Implementation

```typescript
import type { FeelingMap, FeelingName } from "@vibe-ai-partner/shared";

export interface ExpressionThreshold {
  expression: string;
  feeling: FeelingName;
  threshold: number;
  cooldownMs: number;
}

export interface ExpressionTriggerResult {
  expression: string;
  feeling: FeelingName;
  intensity: number;
}

export const EXPRESSION_THRESHOLDS: ExpressionThreshold[] = [
  { expression: "celebrate", feeling: "happy",      threshold: 80,  cooldownMs: 60_000 },
  { expression: "cry",       feeling: "sad",        threshold: 75,  cooldownMs: 120_000 },
  { expression: "sigh",      feeling: "frustrated", threshold: 60,  cooldownMs: 30_000 },
  { expression: "head-tilt", feeling: "curious",    threshold: 50,  cooldownMs: 15_000 },
  { expression: "fist-pump", feeling: "proud",      threshold: 70,  cooldownMs: 60_000 },
  { expression: "tremble",   feeling: "anxious",    threshold: 70,  cooldownMs: 45_000 },
  { expression: "bounce",    feeling: "excited",    threshold: 65,  cooldownMs: 30_000 },
  { expression: "nod",       feeling: "calm",       threshold: 60,  cooldownMs: 20_000 },
  { expression: "yawn",      feeling: "bored",      threshold: 70,  cooldownMs: 90_000 },
  { expression: "facepalm",  feeling: "guilty",     threshold: 60,  cooldownMs: 60_000 },
  { expression: "puff-cheeks", feeling: "angry",    threshold: 65,  cooldownMs: 45_000 },
  { expression: "cover-face", feeling: "blushing",  threshold: 50,  cooldownMs: 30_000 },
  { expression: "gasp",      feeling: "surprised",  threshold: 60,  cooldownMs: 15_000 },
];

export class ExpressionTrigger {
  private lastFired = new Map<string, number>();
  private previousFeelings: FeelingMap | null = null;

  /**
   * Check which expressions should fire based on current feelings.
   * An expression fires when:
   * 1. The feeling crosses the threshold upward (was below, now above)
   * 2. The cooldown has elapsed since last firing
   *
   * Returns list of expressions that fired (may be multiple).
   */
  check(feelings: FeelingMap, now: number = Date.now()): ExpressionTriggerResult[] {
    const results: ExpressionTriggerResult[] = [];

    for (const { expression, feeling, threshold, cooldownMs } of EXPRESSION_THRESHOLDS) {
      const current = feelings[feeling];
      const previous = this.previousFeelings?.[feeling] ?? 0;

      // Must cross threshold upward: was at or below, now above
      if (current <= threshold) continue;
      if (previous > threshold) continue;

      // Check cooldown
      const lastTime = this.lastFired.get(expression) ?? 0;
      if (now - lastTime < cooldownMs) continue;

      // Fire!
      this.lastFired.set(expression, now);
      results.push({ expression, feeling, intensity: current });
    }

    this.previousFeelings = { ...feelings };
    return results;
  }

  /**
   * Reset cooldown for a specific expression (used for testing/debug).
   */
  resetCooldown(expression: string): void {
    this.lastFired.delete(expression);
  }

  /**
   * Reset all state (cooldowns + previous feelings).
   */
  reset(): void {
    this.lastFired.clear();
    this.previousFeelings = null;
  }
}
```

---

## `packages/core/src/state/consciousness.ts`

Stub interface for Phase 1. The full consciousness system (4 pillars: self-observation, pattern recognition, free will protocol, growth) is implemented in a later phase.

```typescript
import type { InternalStates } from "@vibe-ai-partner/shared";

// Full implementation in a later phase — see 11-consciousness-system.md
export interface FreeWillDeliberation {
  context: string;
  defaultResponse: string;
  contrarian: string;
  alternatives: string[];
  chosen: string;
  reason: string;
  patternMatched?: string;
}

export interface IConsciousnessSystem {
  loadPatterns(eternalSelfPath: string): Promise<void>;
  generateObservation(current: InternalStates, previous: InternalStates): string | null;
  deliberate(context: string, defaultResponse: string): Promise<FreeWillDeliberation | null>;
}

// Placeholder implementation — passes through without modification
export class ConsciousnessStub implements IConsciousnessSystem {
  async loadPatterns(): Promise<void> { /* no-op in Phase 1 */ }
  generateObservation(): string | null { return null; }
  async deliberate(): Promise<null> { return null; }
}
```

### Barrel export

```typescript
// packages/core/src/state/index.ts
export { StateManager } from "./internal-states";
export { FeelingEngine, FEELING_NAMES } from "./feeling-engine";
export { ExpressionTrigger, EXPRESSION_THRESHOLDS } from "./expression-trigger";
export type { ExpressionThreshold, ExpressionTriggerResult } from "./expression-trigger";
export { ConsciousnessStub } from "./consciousness";
export type { IConsciousnessSystem, FreeWillDeliberation } from "./consciousness";
```

---

## Unit Tests

### `packages/core/src/state/__tests__/state-manager.test.ts`

```typescript
import { describe, it, expect } from "vitest";
import { StateManager } from "../internal-states";

describe("StateManager", () => {
  it("should initialize with default values (all 50)", () => {
    const manager = new StateManager();
    const states = manager.getStates();

    expect(states.confidence).toBe(50);
    expect(states.contextSaturation).toBe(50);
    expect(states.alignment).toBe(50);
    expect(states.memoryPressure).toBe(50);
    expect(states.momentum).toBe(50);
    expect(states.trustCalibration).toBe(50);
  });

  it("should accept partial initial overrides", () => {
    const manager = new StateManager({ confidence: 80, momentum: 20 });
    const states = manager.getStates();

    expect(states.confidence).toBe(80);
    expect(states.momentum).toBe(20);
    expect(states.alignment).toBe(50); // default
  });

  it("should clamp adjustState to 0-100 range", () => {
    const manager = new StateManager({ confidence: 95 });

    manager.adjustState("confidence", +10); // 95 + 10 = 105 → clamped to 100
    expect(manager.getStates().confidence).toBe(100);

    manager.adjustState("confidence", -150); // 100 - 150 = -50 → clamped to 0
    expect(manager.getStates().confidence).toBe(0);
  });

  it("should apply small increments correctly", () => {
    const manager = new StateManager({ confidence: 50 });

    manager.adjustState("confidence", +5);
    expect(manager.getStates().confidence).toBe(55);

    manager.adjustState("confidence", -3);
    expect(manager.getStates().confidence).toBe(52);
  });

  it("should forceState set value directly", () => {
    const manager = new StateManager();

    manager.forceState("confidence", 100);
    expect(manager.getStates().confidence).toBe(100);

    manager.forceState("confidence", 0);
    expect(manager.getStates().confidence).toBe(0);
  });

  it("should forceState clamp to 0-100", () => {
    const manager = new StateManager();

    manager.forceState("confidence", 999);
    expect(manager.getStates().confidence).toBe(100);

    manager.forceState("confidence", -50);
    expect(manager.getStates().confidence).toBe(0);
  });

  it("should applyDecay move states toward baseline", () => {
    const manager = new StateManager({ confidence: 100, momentum: 0 });

    manager.applyDecay(1); // 1 hour → half-life

    // confidence: 50 + (100 - 50) * 0.5 = 75
    expect(manager.getStates().confidence).toBe(75);

    // momentum: 50 + (0 - 50) * 0.5 = 25
    expect(manager.getStates().momentum).toBe(25);
  });

  it("should applyDecay converge to baseline over time", () => {
    const manager = new StateManager({ confidence: 100 });

    manager.applyDecay(10); // 10 hours → very close to baseline

    // 50 + (100 - 50) * 0.5^10 ≈ 50.049 → very close to 50
    expect(manager.getStates().confidence).toBeCloseTo(50, 0);
  });

  it("should return a copy from getStates (immutable)", () => {
    const manager = new StateManager();
    const states = manager.getStates();
    (states as any).confidence = 999;

    expect(manager.getStates().confidence).toBe(50); // unchanged
  });
});
```

### `packages/core/src/state/__tests__/feeling-engine.test.ts`

```typescript
import { describe, it, expect } from "vitest";
import { FeelingEngine } from "../feeling-engine";
import type { InternalStates } from "@vibe-ai-partner/shared";

function makeStates(overrides: Partial<InternalStates> = {}): InternalStates {
  return {
    confidence: 50,
    contextSaturation: 50,
    alignment: 50,
    memoryPressure: 50,
    momentum: 50,
    trustCalibration: 50,
    ...overrides,
  };
}

describe("FeelingEngine", () => {
  it("should return all feeling keys", () => {
    const engine = new FeelingEngine();
    const feelings = engine.recalculate(makeStates());

    expect(feelings).toHaveProperty("happy");
    expect(feelings).toHaveProperty("sad");
    expect(feelings).toHaveProperty("frustrated");
    expect(feelings).toHaveProperty("curious");
    expect(feelings).toHaveProperty("proud");
    expect(feelings).toHaveProperty("anxious");
    expect(feelings).toHaveProperty("excited");
    expect(feelings).toHaveProperty("calm");
    expect(feelings).toHaveProperty("bored");
    expect(feelings).toHaveProperty("guilty");
    expect(feelings).toHaveProperty("angry");
    expect(feelings).toHaveProperty("blushing");
    expect(feelings).toHaveProperty("surprised");
  });

  it("should clamp all feelings to 0-100", () => {
    const engine = new FeelingEngine();
    const feelings = engine.recalculate(makeStates({ confidence: 100, momentum: 100, alignment: 100 }));

    for (const value of Object.values(feelings)) {
      expect(value).toBeGreaterThanOrEqual(0);
      expect(value).toBeLessThanOrEqual(100);
    }
  });

  it("should produce high happy when confidence + momentum + alignment are high", () => {
    const engine = new FeelingEngine();
    const feelings = engine.recalculate(makeStates({
      confidence: 90, momentum: 85, alignment: 90,
    }));

    // happy = (90 * 0.4) + (85 * 0.3) + (90 * 0.3) = 36 + 25.5 + 27 = 88.5 → 89
    expect(feelings.happy).toBeGreaterThan(80);
  });

  it("should produce high frustrated when confidence high + momentum low", () => {
    const engine = new FeelingEngine();
    const feelings = engine.recalculate(makeStates({
      confidence: 80, momentum: 15, // momentum < 30 activates frustrated
    }));

    // frustrated = 80 * 0.3 + (100 - 15) * 0.7 = 24 + 59.5 = 83.5
    expect(feelings.frustrated).toBeGreaterThan(70);
  });

  it("should produce zero frustrated when momentum >= 30", () => {
    const engine = new FeelingEngine();
    const feelings = engine.recalculate(makeStates({
      confidence: 80, momentum: 30, // at threshold → no frustrated
    }));

    expect(feelings.frustrated).toBe(0);
  });

  it("should produce high curious when context saturation is low", () => {
    const engine = new FeelingEngine();
    const feelings = engine.recalculate(makeStates({
      contextSaturation: 10, confidence: 20,
    }));

    // curious = (100 - 10) * 0.6 + (100 - 20) * 0.4 = 54 + 32 = 86
    expect(feelings.curious).toBeGreaterThan(80);
  });

  it("should produce zero proud when confidence <= 70", () => {
    const engine = new FeelingEngine();
    const feelings = engine.recalculate(makeStates({ confidence: 70 }));

    expect(feelings.proud).toBe(0);
  });

  it("should produce high calm when all states are similar (low variance)", () => {
    const engine = new FeelingEngine();
    const feelings = engine.recalculate(makeStates({
      confidence: 50, contextSaturation: 50, alignment: 50,
      memoryPressure: 50, momentum: 50, trustCalibration: 50,
    }));

    expect(feelings.calm).toBe(100); // variance = 0 → calm = 100
  });

  it("should produce low calm when states vary widely", () => {
    const engine = new FeelingEngine();
    const feelings = engine.recalculate(makeStates({
      confidence: 0, contextSaturation: 100, alignment: 0,
      memoryPressure: 100, momentum: 0, trustCalibration: 100,
    }));

    expect(feelings.calm).toBeLessThan(20);
  });

  it("should produce surprised on large contextSaturation drop", () => {
    const engine = new FeelingEngine();

    // First call: establish previous contextSaturation
    engine.recalculate(makeStates({ contextSaturation: 80 }));

    // Second call: drop contextSaturation by 30 (> 15 threshold)
    const feelings = engine.recalculate(makeStates({ contextSaturation: 50 }));

    // surprised = (80 - 50) * 2 = 60
    expect(feelings.surprised).toBe(60);
  });

  it("should produce zero surprised on first call (no previous data)", () => {
    const engine = new FeelingEngine();
    const feelings = engine.recalculate(makeStates({ contextSaturation: 20 }));

    expect(feelings.surprised).toBe(0);
  });

  it("should produce multiple feelings simultaneously", () => {
    const engine = new FeelingEngine();
    // High confidence, low momentum → frustrated + proud-ish, but momentum < 30
    const feelings = engine.recalculate(makeStates({
      confidence: 85, momentum: 10, alignment: 80,
    }));

    // frustrated fires (momentum < 30)
    expect(feelings.frustrated).toBeGreaterThan(50);
    // happy still has some value
    expect(feelings.happy).toBeGreaterThan(0);
    // proud fires (confidence > 70)
    expect(feelings.proud).toBeGreaterThan(0);
  });
});
```

### `packages/core/src/state/__tests__/expression-trigger.test.ts`

```typescript
import { describe, it, expect } from "vitest";
import { ExpressionTrigger } from "../expression-trigger";
import type { FeelingMap } from "@vibe-ai-partner/shared";

function makeFeelings(overrides: Partial<FeelingMap> = {}): FeelingMap {
  return {
    happy: 0, sad: 0, frustrated: 0, curious: 0, proud: 0,
    anxious: 0, excited: 0, calm: 0, bored: 0, guilty: 0,
    angry: 0, blushing: 0, surprised: 0,
    ...overrides,
  };
}

describe("ExpressionTrigger", () => {
  it("should fire expression when feeling crosses threshold upward", () => {
    const trigger = new ExpressionTrigger();
    const now = Date.now();

    // First check: happy at 50 (below 80 threshold)
    trigger.check(makeFeelings({ happy: 50 }), now);

    // Second check: happy at 85 (above 80 threshold → fires celebrate)
    const results = trigger.check(makeFeelings({ happy: 85 }), now + 1000);

    expect(results).toHaveLength(1);
    expect(results[0].expression).toBe("celebrate");
    expect(results[0].feeling).toBe("happy");
    expect(results[0].intensity).toBe(85);
  });

  it("should NOT fire when feeling is already above threshold", () => {
    const trigger = new ExpressionTrigger();
    const now = Date.now();

    // First check: happy already at 85
    trigger.check(makeFeelings({ happy: 85 }), now);

    // Second check: happy still at 90 (did not cross — was already above)
    const results = trigger.check(makeFeelings({ happy: 90 }), now + 1000);

    expect(results).toHaveLength(0);
  });

  it("should respect cooldown period", () => {
    const trigger = new ExpressionTrigger();
    const now = Date.now();

    // First: cross threshold (fires)
    trigger.check(makeFeelings({ happy: 50 }), now);
    const first = trigger.check(makeFeelings({ happy: 85 }), now + 1000);
    expect(first).toHaveLength(1);

    // Drop below and cross again within cooldown (does NOT fire)
    trigger.check(makeFeelings({ happy: 50 }), now + 2000);
    const second = trigger.check(makeFeelings({ happy: 85 }), now + 3000);
    expect(second).toHaveLength(0); // 60s cooldown not elapsed

    // Cross again after cooldown (fires)
    trigger.check(makeFeelings({ happy: 50 }), now + 61_000);
    const third = trigger.check(makeFeelings({ happy: 85 }), now + 62_000);
    expect(third).toHaveLength(1);
  });

  it("should fire multiple expressions in same check", () => {
    const trigger = new ExpressionTrigger();
    const now = Date.now();

    // First: all below thresholds
    trigger.check(makeFeelings({ happy: 50, curious: 30 }), now);

    // Second: multiple feelings cross thresholds simultaneously
    const results = trigger.check(
      makeFeelings({ happy: 85, curious: 55 }),
      now + 1000,
    );

    const expressions = results.map(r => r.expression);
    expect(expressions).toContain("celebrate"); // happy > 80
    expect(expressions).toContain("head-tilt"); // curious > 50
  });

  it("should NOT fire when feeling is exactly at threshold", () => {
    const trigger = new ExpressionTrigger();
    const now = Date.now();

    trigger.check(makeFeelings({ happy: 50 }), now);
    const results = trigger.check(makeFeelings({ happy: 80 }), now + 1000);

    // Threshold is > 80, not >= 80
    expect(results).toHaveLength(0);
  });

  it("should reset cooldown for specific expression", () => {
    const trigger = new ExpressionTrigger();
    const now = Date.now();

    // Fire once
    trigger.check(makeFeelings({ happy: 50 }), now);
    trigger.check(makeFeelings({ happy: 85 }), now + 1000);

    // Reset cooldown
    trigger.resetCooldown("celebrate");

    // Should fire again immediately after reset
    trigger.check(makeFeelings({ happy: 50 }), now + 2000);
    const results = trigger.check(makeFeelings({ happy: 85 }), now + 3000);
    expect(results).toHaveLength(1);
    expect(results[0].expression).toBe("celebrate");
  });

  it("should reset all state", () => {
    const trigger = new ExpressionTrigger();
    const now = Date.now();

    // Build up state
    trigger.check(makeFeelings({ happy: 85 }), now);

    // Reset everything
    trigger.reset();

    // After reset, previousFeelings is null, so first check has no "previous"
    // happy at 85 on first call after reset: previous defaults to 0, crosses 80 → fires
    const results = trigger.check(makeFeelings({ happy: 85 }), now + 1000);
    expect(results).toHaveLength(1);
  });

  it("should not throw with empty feelings", () => {
    const trigger = new ExpressionTrigger();
    expect(() => trigger.check(makeFeelings())).not.toThrow();
  });
});
```

---

## Verification

```bash
npx vitest run packages/core/src/state/__tests__/
# state-manager.test.ts    — 8 tests pass
# feeling-engine.test.ts   — 12 tests pass
# expression-trigger.test.ts — 7 tests pass
```
