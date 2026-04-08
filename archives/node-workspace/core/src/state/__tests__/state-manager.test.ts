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
