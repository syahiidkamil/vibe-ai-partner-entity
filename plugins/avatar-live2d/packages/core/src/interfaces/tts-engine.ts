import type { IPlugin } from "./plugin.js";

/**
 * Options for TTS generation.
 */
export interface TTSOptions {
  /** Voice ID (e.g., "af_heart", "Bella"). Engine-specific. */
  voice?: string;

  /** Playback speed multiplier. 1.0 = normal. */
  speed?: number;

  /** Output audio format. */
  format?: "wav" | "mp3" | "opus";
}

/**
 * Result of full (non-streaming) TTS generation.
 */
export interface TTSResult {
  /** Raw audio data */
  audio: ArrayBuffer;

  /** Sample rate in Hz (e.g., 24000) */
  sampleRate: number;

  /** Duration in seconds */
  duration: number;
}

/**
 * A single chunk from streaming TTS generation.
 */
export interface TTSChunk {
  /** Partial audio data */
  audio: ArrayBuffer;

  /** Sample rate in Hz */
  sampleRate: number;

  /** True for the final chunk — no more data coming */
  isFinal: boolean;
}

/**
 * Metadata about an available voice.
 */
export interface VoiceInfo {
  /** Engine-specific voice ID (e.g., "af_heart", "Bella") */
  id: string;

  /** Human-readable name (e.g., "Heart (Female)") */
  name: string;

  /** Language code (e.g., "en-us", "ja") */
  language: string;

  /** Voice gender */
  gender: "male" | "female" | "neutral";
}

/**
 * Universal TTS engine interface.
 *
 * All engines follow the same pattern: Text in → Audio out.
 * Streaming is optional — engines that don't natively stream
 * can return a single-chunk AsyncIterable.
 *
 * Engine implementations:
 *   - Kokoro: Python daemon, PyTorch, GPU recommended, 27 voices, native streaming
 *   - Kokoro ONNX: ONNX Runtime, CPU-friendly, 20+ voices, full-then-play
 *   - KittenTTS: 15M param model, CPU-only, 8 voices, full-then-play
 */
export interface ITTSEngine extends IPlugin {
  /**
   * Generate complete audio from text.
   * Resolves when all audio is ready.
   * @param text - Text to synthesize
   * @param options - Voice, speed, format overrides
   */
  generate(text: string, options?: TTSOptions): Promise<TTSResult>;

  /**
   * Generate audio as a stream of chunks.
   * For engines that don't natively stream, yields a single chunk with isFinal=true.
   * @param text - Text to synthesize
   * @param options - Voice, speed, format overrides
   */
  generateStream(
    text: string,
    options?: TTSOptions,
  ): AsyncIterable<TTSChunk>;

  /**
   * Abort current generation/playback immediately.
   */
  stop(): void;

  /**
   * List all voices available in this engine.
   */
  getAvailableVoices(): Promise<VoiceInfo[]>;

  /**
   * Set the active voice for subsequent generation calls.
   * @param voiceId - Voice ID from getAvailableVoices()
   */
  setVoice(voiceId: string): void;
}
