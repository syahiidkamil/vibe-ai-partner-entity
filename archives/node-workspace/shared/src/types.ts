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
