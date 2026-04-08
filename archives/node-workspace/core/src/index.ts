// Interfaces
export type {
  IPlugin,
  IPluginManifest,
  IPluginRegistry,
  IAvatarRenderer,
  ITTSEngine,
  TTSOptions,
  TTSResult,
  TTSChunk,
  VoiceInfo,
  EventMap,
  IEventBus,
} from "./interfaces/index.js";

// Events
export { EventBus } from "./events/index.js";
export type { EntityEventMap } from "./events/index.js";

// State engine
export { StateManager } from "./state/index.js";
export { FeelingEngine, FEELING_NAMES } from "./state/index.js";
export { ExpressionTrigger, EXPRESSION_THRESHOLDS } from "./state/index.js";
export type { ExpressionThreshold, ExpressionTriggerResult } from "./state/index.js";
export { ConsciousnessStub } from "./state/index.js";
export type { IConsciousnessSystem, FreeWillDeliberation } from "./state/index.js";
