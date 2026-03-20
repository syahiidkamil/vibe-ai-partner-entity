import type { Live2DSelfExpressionMapping } from "./types.js";

/**
 * Maps self-expression names to Live2D motion files (.motion3.json) and plays them.
 *
 * Ported from submodule index.html:
 *   const SELF_EXPRESSION_MAP = {
 *     nod: 0, headshake: 1, headtilt: 2, laugh: 3, giggle: 4,
 *     gasp: 5, think: 6, celebrate: 7, sweat: 8, wave: 9, bow: 10, starryeyes: 11,
 *   };
 *   function playSelfExpression(name) {
 *     const idx = SELF_EXPRESSION_MAP[name];
 *     model.motion('SelfExpression', idx, 3);
 *   }
 *
 * Changes from submodule:
 *   - Reads mappings from capabilities.json instead of hardcoded index map
 *   - Resolves motion index dynamically from motion file path
 *   - Returns a Promise that resolves when the motion completes
 *   - Supports motion queuing (one motion at a time, queue the rest)
 */
export class MotionPlayer {
  private selfExpressions: Record<string, Live2DSelfExpressionMapping>;
  private model: any = null;
  private queue: Array<{ name: string; resolve: () => void }> = [];
  private playing = false;

  constructor(selfExpressions: Record<string, Live2DSelfExpressionMapping>) {
    this.selfExpressions = selfExpressions;
  }

  /** Bind to a loaded Live2D model. Must be called after model loads. */
  bind(model: any): void {
    this.model = model;
  }

  /**
   * Play a self-expression motion. Returns a Promise that resolves on completion.
   *
   * If a motion is already playing, the new motion is queued and will play
   * after the current one finishes.
   *
   * @param name - Self-expression name (e.g., "wave", "nod", "celebrate")
   */
  async play(name: string): Promise<void> {
    if (!this.model) return;

    const mapping = this.selfExpressions[name];
    if (!mapping) return; // Unknown expression — silently ignore

    return new Promise<void>((resolve) => {
      this.queue.push({ name, resolve });
      if (!this.playing) {
        this.processQueue();
      }
    });
  }

  /** Get list of available self-expression names. */
  getAvailable(): string[] {
    return Object.keys(this.selfExpressions);
  }

  /**
   * Process the motion queue. Plays one motion at a time.
   *
   * Motion playback uses pixi-live2d-display's motion() method with:
   *   - Group: "SelfExpression" (matches the motion group in model3.json)
   *   - Index: looked up from the model's motion definitions
   *   - Priority: 3 (force — overrides idle and other lower-priority motions)
   *
   * Ported from submodule:
   *   model.motion('SelfExpression', idx, 3)
   *
   * Change: instead of hardcoded indices (nod: 0, headshake: 1, ...),
   * we find the index by matching the motion file path from capabilities.json
   * against the SelfExpression motion definitions in model3.json.
   */
  private async processQueue(): Promise<void> {
    if (this.queue.length === 0) {
      this.playing = false;
      return;
    }

    this.playing = true;
    const { name, resolve } = this.queue.shift()!;

    const mapping = this.selfExpressions[name];
    const idx = this.findMotionIndex(mapping.motion);

    if (idx >= 0) {
      try {
        // Priority 3 = force (overrides idle motions)
        await this.model.motion("SelfExpression", idx, 3);
      } catch (err) {
        // Motion playback failed — log but don't break the queue
        console.error(`Motion "${name}" failed:`, err);
      }
    }

    resolve();
    this.processQueue();
  }

  /**
   * Find the index of a motion file within the SelfExpression motion group.
   *
   * The model3.json Motions.SelfExpression array contains objects like:
   *   { "File": "self-expression/Nodding.motion3.json" }
   *
   * We match against the filename portion of the capabilities.json motion path.
   */
  private findMotionIndex(motionFile: string): number {
    const motionManager = this.model.internalModel?.motionManager;
    if (!motionManager) return -1;

    // Access the motion definitions from the model's settings
    // In Cubism 4, this is stored in model.internalModel.settings.motions
    const motionGroups = this.model.internalModel?.settings?.motions;
    if (!motionGroups?.SelfExpression) return -1;

    const definitions: Array<{ File: string }> = motionGroups.SelfExpression;

    return definitions.findIndex((def) => {
      // Match by filename: "self-expression/Nodding.motion3.json" ends with "Nodding.motion3.json"
      return def.File.endsWith(motionFile);
    });
  }
}
