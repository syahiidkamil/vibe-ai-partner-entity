import type { IPlugin } from "./plugin.js";

/**
 * Universal avatar renderer interface.
 *
 * All renderers follow the same lifecycle:
 *   mount(container) → update loop → setFeeling/playSelfExpression/setLipSyncAmplitude → unmount()
 *
 * Feelings are persistent mood states (the avatar's face stays happy).
 * Self-expressions are one-shot motions (the avatar waves once).
 * Lip sync is driven by a normalized amplitude value from the TTS pipeline.
 *
 * What each method maps to internally depends on the renderer:
 *   - Live2D: .exp3.json presets, .motion3.json keyframes, ParamMouthOpenY
 *   - VRM: FACS blend shapes, bone quaternions, jaw + visemes
 *   - Three.js: morph targets, AnimationClip, morph target weights
 *   - HTML: CSS classes, CSS animations, CSS property transitions
 */
export interface IAvatarRenderer extends IPlugin {
  /**
   * Create canvas/DOM, load model, start render loop.
   * Called once when the renderer becomes active.
   */
  mount(container: HTMLElement): Promise<void>;

  /**
   * Per-frame update. Drives idle animations, physics, spring smoothing.
   * Called every requestAnimationFrame by the host.
   * @param deltaTime - Time since last frame in seconds
   */
  update(deltaTime: number): void;

  /**
   * Set a persistent feeling (mood). Maps to renderer-specific expression.
   * Unknown or unsupported feelings are silently ignored.
   * @param feeling - Feeling name (e.g., "happy", "frustrated")
   * @param intensity - Intensity 0-100
   */
  setFeeling(feeling: string, intensity: number): void;

  /**
   * Play a one-shot self-expression motion (e.g., wave, nod, laugh).
   * Resolves when the motion completes. Unknown expressions silently ignored.
   * @param name - Expression name (e.g., "wave", "celebrate")
   */
  playSelfExpression(name: string): Promise<void>;

  /**
   * Drive lip sync from audio amplitude.
   * Called at ~30Hz during TTS playback.
   * @param amplitude - Normalized 0-1 value (0 = closed, 1 = fully open)
   */
  setLipSyncAmplitude(amplitude: number): void;

  /**
   * Handle container resize. Updates canvas/camera/viewport.
   * @param width - New width in pixels
   * @param height - New height in pixels
   */
  resize(width: number, height: number): void;

  /**
   * Query which feelings this renderer supports.
   * Reads from the model's capabilities.json at runtime.
   * @returns Array of supported feeling names
   */
  getAvailableFeelings(): string[];

  /**
   * Query which self-expressions this renderer supports.
   * Reads from the model's capabilities.json at runtime.
   * @returns Array of supported expression names
   */
  getAvailableSelfExpressions(): string[];

  /**
   * Remove canvas/DOM elements. Release WebGL context.
   * The plugin can be remounted later without re-initialization
   * (e.g., switching tabs — model data stays loaded).
   */
  unmount(): void;
}
