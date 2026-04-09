import type { ExpressionGroup } from "@vibe-ai-partner/shared";

// ─── capabilities.json schema (Live2D variant) ────────────────

export interface Live2DCapabilities {
  renderer: "live2d";
  model: string;
  version?: string;

  feelings: Record<string, Live2DFeelingMapping | null>;
  selfExpressions: Record<string, Live2DSelfExpressionMapping>;
  lipSync: Live2DLipSyncConfig;
}

export interface Live2DFeelingMapping {
  /** Relative path to .exp3.json file within the model directory */
  expression: string;
}

export interface Live2DSelfExpressionMapping {
  /** Relative path to .motion3.json file within the model directory */
  motion: string;
  /** Expression group for categorization */
  group: ExpressionGroup;
}

export interface Live2DLipSyncConfig {
  method: "rms";
  /** Cubism parameter name (e.g., "ParamMouthOpenY" or "PARAM_MOUTH_OPEN_Y") */
  parameter: string;
  /** Min/max range for the parameter */
  range: [number, number];
}

// ─── Runtime types ─────────────────────────────────────────────

export interface Live2DRendererConfig {
  /** Absolute path to the model directory containing model3.json + capabilities.json */
  modelPath: string;
  /** Override canvas width (default: container width) */
  width?: number;
  /** Override canvas height (default: container height) */
  height?: number;
}
