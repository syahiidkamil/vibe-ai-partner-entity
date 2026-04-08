import type { Live2DFeelingMapping } from "./types.js";

/**
 * Maps feeling names to Live2D expression files (.exp3.json) and applies them.
 *
 * Ported from submodule index.html:
 *   const EXPRESSION_MAP = { normal: 'Normal', happy: 'Happy', ... };
 *   function setExpression(name) {
 *     const em = model.internalModel.motionManager.expressionManager;
 *     const idx = em?.definitions?.findIndex(d => d.Name === exprName);
 *     if (idx >= 0) model.expression(idx);
 *   }
 *
 * Changes from submodule:
 *   - Reads mappings from capabilities.json instead of hardcoded EXPRESSION_MAP
 *   - Supports intensity parameter (0-100) for future weighted blending
 *   - Graceful degradation: unknown feelings silently ignored
 */
export class ExpressionManager {
  private feelings: Record<string, Live2DFeelingMapping | null>;
  private model: any = null;

  constructor(feelings: Record<string, Live2DFeelingMapping | null>) {
    this.feelings = feelings;
  }

  /** Bind to a loaded Live2D model. Must be called after model loads. */
  bind(model: any): void {
    this.model = model;
  }

  /**
   * Apply a feeling as an expression on the Live2D model.
   *
   * @param feeling - Feeling name (e.g., "happy", "sad")
   * @param intensity - 0-100 (currently used as boolean: >0 applies, 0 resets to normal)
   *
   * Implementation notes:
   *   - pixi-live2d-display's expression system works by index, not by name
   *   - We find the index by matching the expression Name from model3.json definitions
   *   - intensity is available for future use (Cubism expressions don't natively support
   *     weighted blending, but we can simulate it by interpolating parameter values)
   */
  apply(feeling: string, intensity: number): void {
    if (!this.model) return;

    // If intensity is 0, reset to normal
    if (intensity <= 0) {
      this.applyByName("Normal");
      return;
    }

    const mapping = this.feelings[feeling];
    if (!mapping) return; // Unsupported feeling — silently ignore

    // Extract expression name from file path:
    // "internal-feeling/Happy.exp3.json" → "Happy"
    const fileName = mapping.expression.split("/").pop() ?? mapping.expression;
    const exprName = fileName.replace(".exp3.json", "");
    this.applyByName(exprName);
  }

  /** Get list of feelings this model supports (non-null mappings). */
  getAvailable(): string[] {
    return Object.entries(this.feelings)
      .filter(([_, mapping]) => mapping !== null)
      .map(([name]) => name);
  }

  /**
   * Apply an expression by its Name field in the model3.json Expressions array.
   *
   * Ported directly from submodule setExpression():
   *   const em = model.internalModel.motionManager.expressionManager;
   *   const idx = em?.definitions?.findIndex(d => d.Name === exprName);
   *   if (idx >= 0) model.expression(idx);
   */
  private applyByName(name: string): void {
    const em = this.model.internalModel?.motionManager?.expressionManager;
    if (!em?.definitions) return;

    const idx = em.definitions.findIndex(
      (d: { Name: string }) => d.Name === name,
    );
    if (idx >= 0) {
      this.model.expression(idx);
    }
  }
}
