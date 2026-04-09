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
