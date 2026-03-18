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
