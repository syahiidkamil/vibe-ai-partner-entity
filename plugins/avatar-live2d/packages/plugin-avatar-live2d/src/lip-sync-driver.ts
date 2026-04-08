import type { Live2DLipSyncConfig } from "./types.js";

/**
 * Drives the Live2D model's mouth parameter from a normalized amplitude value.
 *
 * Ported from submodule index.html:
 *   function updateLipSync() {
 *     analyser.getByteTimeDomainData(dataArray);
 *     // ... RMS calculation ...
 *     const target = Math.min(Math.sqrt(gated * 8) * 1.2, 1);
 *     smoothedMouth += (target - smoothedMouth) * (target > smoothedMouth ? 0.8 : 0.3);
 *     model.internalModel.coreModel.setParameterValueById('PARAM_MOUTH_OPEN_Y', smoothedMouth);
 *   }
 *
 * Changes from submodule:
 *   - Does NOT do RMS calculation (that happens in the TTS/audio pipeline)
 *   - Receives pre-computed normalized amplitude (0-1) from setLipSyncAmplitude()
 *   - Smoothing is applied here to avoid jittery mouth movement
 *   - Parameter name comes from capabilities.json, not hardcoded
 *   - Range mapping from capabilities.json (e.g., [0, 1])
 */
export class LipSyncDriver {
  private config: Live2DLipSyncConfig;
  private model: any = null;
  private smoothedValue = 0;

  /** Smoothing factor for rising amplitude (0-1, higher = more responsive) */
  private readonly ATTACK_FACTOR = 0.8;
  /** Smoothing factor for falling amplitude (0-1, lower = slower decay) */
  private readonly RELEASE_FACTOR = 0.3;

  constructor(config: Live2DLipSyncConfig) {
    this.config = config;
  }

  /** Bind to a loaded Live2D model. Must be called after model loads. */
  bind(model: any): void {
    this.model = model;
  }

  /**
   * Set the lip sync amplitude. Called at ~30Hz during TTS playback.
   *
   * Applies asymmetric smoothing:
   *   - Fast attack (0.8): mouth opens quickly when amplitude rises
   *   - Slow release (0.3): mouth closes gradually when amplitude drops
   *
   * This prevents the "machine gun" effect of rapid open/close cycles
   * while keeping the mouth responsive to speech onset.
   *
   * @param amplitude - Normalized 0-1 value (0 = silent/closed, 1 = loud/fully open)
   */
  setAmplitude(amplitude: number): void {
    if (!this.model) return;

    // Clamp input to 0-1
    const clamped = Math.max(0, Math.min(1, amplitude));

    // Asymmetric smoothing (ported from submodule updateLipSync)
    if (clamped > this.smoothedValue) {
      this.smoothedValue += (clamped - this.smoothedValue) * this.ATTACK_FACTOR;
    } else {
      this.smoothedValue +=
        (clamped - this.smoothedValue) * this.RELEASE_FACTOR;
    }

    // Map to configured range
    const [min, max] = this.config.range;
    const mapped = min + this.smoothedValue * (max - min);

    // Apply to Cubism parameter
    // The parameter name in capabilities.json uses the human-readable format
    // (e.g., "ParamMouthOpenY"), but the Cubism SDK uses the internal ID format
    // (e.g., "PARAM_MOUTH_OPEN_Y"). We try both.
    try {
      this.model.internalModel.coreModel.setParameterValueById(
        this.config.parameter,
        mapped,
      );
    } catch {
      // Try the SCREAMING_SNAKE_CASE variant
      const snakeCase = this.config.parameter
        .replace(/([A-Z])/g, "_$1")
        .toUpperCase()
        .replace(/^_/, "");
      try {
        this.model.internalModel.coreModel.setParameterValueById(
          snakeCase,
          mapped,
        );
      } catch {
        // Parameter not found — silently ignore
      }
    }
  }

  /** Reset mouth to closed position. Call when speech ends. */
  reset(): void {
    this.smoothedValue = 0;
    if (this.model) {
      const [min] = this.config.range;
      try {
        this.model.internalModel.coreModel.setParameterValueById(
          this.config.parameter,
          min,
        );
      } catch {
        // Ignore
      }
    }
  }
}
