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
