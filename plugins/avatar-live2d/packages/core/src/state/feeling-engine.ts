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
      relieved: 0, // Placeholder — formula not yet defined
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
