// Plugin system
export type {
  IPlugin,
  IPluginManifest,
  IPluginRegistry,
} from "./plugin.js";

// Avatar renderer
export type { IAvatarRenderer } from "./avatar-renderer.js";

// TTS engine
export type {
  ITTSEngine,
  TTSOptions,
  TTSResult,
  TTSChunk,
  VoiceInfo,
} from "./tts-engine.js";

// Communication
export type {
  EventMap,
  IEventBus,
} from "./communication.js";
