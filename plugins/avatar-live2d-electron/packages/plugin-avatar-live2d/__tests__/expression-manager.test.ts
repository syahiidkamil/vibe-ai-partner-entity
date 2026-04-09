import { describe, it, expect, vi, beforeEach } from "vitest";
import { ExpressionManager } from "../src/expression-manager.js";
import type { Live2DFeelingMapping } from "../src/types.js";

// Mock capabilities.json feelings section
const mockFeelings: Record<string, Live2DFeelingMapping | null> = {
  happy: { expression: "internal-feeling/Happy.exp3.json" },
  sad: { expression: "internal-feeling/Sad.exp3.json" },
  frustrated: { expression: "internal-feeling/Frustrated.exp3.json" },
  calm: null, // Not supported by this model
  curious: { expression: "internal-feeling/Curious.exp3.json" },
};

// Mock Live2D model with expression definitions matching model3.json
function createMockModel() {
  const expressionFn = vi.fn();
  return {
    expression: expressionFn,
    internalModel: {
      motionManager: {
        expressionManager: {
          definitions: [
            { Name: "Normal" },
            { Name: "Happy" },
            { Name: "Sad" },
            { Name: "Frustrated" },
            { Name: "Curious" },
          ],
        },
      },
    },
    _expressionFn: expressionFn,
  };
}

describe("ExpressionManager", () => {
  let manager: ExpressionManager;
  let mockModel: ReturnType<typeof createMockModel>;

  beforeEach(() => {
    manager = new ExpressionManager(mockFeelings);
    mockModel = createMockModel();
    manager.bind(mockModel);
  });

  describe("getAvailable()", () => {
    it("returns only non-null feelings", () => {
      const available = manager.getAvailable();
      expect(available).toEqual(["happy", "sad", "frustrated", "curious"]);
      expect(available).not.toContain("calm");
    });
  });

  describe("apply()", () => {
    it("applies happy expression by finding index in definitions", () => {
      manager.apply("happy", 80);
      // "Happy" is at index 1 in the definitions array
      expect(mockModel._expressionFn).toHaveBeenCalledWith(1);
    });

    it("applies sad expression", () => {
      manager.apply("sad", 60);
      // "Sad" is at index 2
      expect(mockModel._expressionFn).toHaveBeenCalledWith(2);
    });

    it("resets to Normal when intensity is 0", () => {
      manager.apply("happy", 0);
      // "Normal" is at index 0
      expect(mockModel._expressionFn).toHaveBeenCalledWith(0);
    });

    it("silently ignores unsupported feelings (null in capabilities)", () => {
      manager.apply("calm", 80);
      expect(mockModel._expressionFn).not.toHaveBeenCalled();
    });

    it("silently ignores unknown feelings (not in capabilities at all)", () => {
      manager.apply("nonexistent", 80);
      expect(mockModel._expressionFn).not.toHaveBeenCalled();
    });
  });

  describe("without model bound", () => {
    it("does not throw when apply is called before bind", () => {
      const unbound = new ExpressionManager(mockFeelings);
      expect(() => unbound.apply("happy", 80)).not.toThrow();
    });
  });
});
