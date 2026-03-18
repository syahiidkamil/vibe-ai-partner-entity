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
