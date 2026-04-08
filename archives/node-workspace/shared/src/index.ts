// Constants
export {
  FEELING_NAMES,
  STATE_NAMES,
  EXPRESSION_GROUPS,
  STATE_BASELINE,
  DEFAULT_STATE_VALUES,
} from "./constants.js";

export type { FeelingName, StateName, ExpressionGroup } from "./constants.js";

// Core types
export type {
  InternalStates,
  FeelingMap,
  StateAdjustment,
  ExpressionTriggerResult,
  PluginType,
  VocalMode,
} from "./types.js";

// Protocol types
export type {
  SpeakRequest,
  FeelingRequest,
  ActionRequest,
  StateAdjustRequest,
  HealthResponse,
  StateResponse,
  WSMessage,
  WSAmplitude,
  WSStateUpdate,
  WSFeelingUpdate,
  WSActionUpdate,
  WSStatusMessage,
  WSAudioChunk,
  WSExpressionFired,
} from "./protocol.js";
