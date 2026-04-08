import { describe, it, expect } from "vitest";
import { ExpressionTrigger } from "../expression-trigger";
import type { FeelingMap } from "@vibe-ai-partner/shared";

function makeFeelings(overrides: Partial<FeelingMap> = {}): FeelingMap {
  return {
    happy: 0, sad: 0, frustrated: 0, curious: 0, proud: 0,
    anxious: 0, excited: 0, calm: 0, bored: 0, guilty: 0,
    angry: 0, blushing: 0, surprised: 0, relieved: 0,
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
