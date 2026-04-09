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
