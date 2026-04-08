import { describe, it, expect, vi, beforeEach } from "vitest";
import { MotionPlayer } from "../src/motion-player.js";
import type { Live2DSelfExpressionMapping } from "../src/types.js";

// Mock capabilities.json selfExpressions section
const mockSelfExpressions: Record<string, Live2DSelfExpressionMapping> = {
  wave: { motion: "self-expression/Waving.motion3.json", group: "social" },
  nod: { motion: "self-expression/Nodding.motion3.json", group: "social" },
  laugh: {
    motion: "self-expression/Laughing.motion3.json",
    group: "emotional",
  },
  celebrate: {
    motion: "self-expression/Celebrating.motion3.json",
    group: "combo",
  },
};

// Mock Live2D model with motion definitions matching model3.json
function createMockModel() {
  const motionFn = vi.fn().mockResolvedValue(true);
  return {
    motion: motionFn,
    internalModel: {
      motionManager: {},
      settings: {
        motions: {
          SelfExpression: [
            { File: "self-expression/Nodding.motion3.json" },
            { File: "self-expression/HeadShake.motion3.json" },
            { File: "self-expression/Laughing.motion3.json" },
            { File: "self-expression/Celebrating.motion3.json" },
            { File: "self-expression/Waving.motion3.json" },
          ],
        },
      },
    },
    _motionFn: motionFn,
  };
}

describe("MotionPlayer", () => {
  let player: MotionPlayer;
  let mockModel: ReturnType<typeof createMockModel>;

  beforeEach(() => {
    player = new MotionPlayer(mockSelfExpressions);
    mockModel = createMockModel();
    player.bind(mockModel);
  });

  describe("getAvailable()", () => {
    it("returns all self-expression names", () => {
      const available = player.getAvailable();
      expect(available).toEqual(["wave", "nod", "laugh", "celebrate"]);
    });
  });

  describe("play()", () => {
    it("plays wave motion by finding index from file path", async () => {
      await player.play("wave");
      // "Waving.motion3.json" matches index 4 in SelfExpression group
      expect(mockModel._motionFn).toHaveBeenCalledWith(
        "SelfExpression",
        4,
        3,
      );
    });

    it("plays nod motion", async () => {
      await player.play("nod");
      // "Nodding.motion3.json" matches index 0
      expect(mockModel._motionFn).toHaveBeenCalledWith(
        "SelfExpression",
        0,
        3,
      );
    });

    it("silently ignores unknown expressions", async () => {
      await player.play("nonexistent");
      expect(mockModel._motionFn).not.toHaveBeenCalled();
    });

    it("resolves the promise when motion completes", async () => {
      const promise = player.play("wave");
      await expect(promise).resolves.toBeUndefined();
    });
  });

  describe("queuing", () => {
    it("plays motions sequentially when queued", async () => {
      const callOrder: string[] = [];

      // Make motion() resolve after a microtask to simulate async playback
      mockModel._motionFn.mockImplementation(
        (_group: string, idx: number, _priority: number) => {
          callOrder.push(`motion-${idx}`);
          return Promise.resolve(true);
        },
      );

      // Queue two motions simultaneously
      const p1 = player.play("wave");
      const p2 = player.play("nod");

      await Promise.all([p1, p2]);

      // Both should have played
      expect(callOrder).toHaveLength(2);
      // Wave first (index 4), then nod (index 0)
      expect(callOrder[0]).toBe("motion-4");
      expect(callOrder[1]).toBe("motion-0");
    });
  });

  describe("without model bound", () => {
    it("does not throw when play is called before bind", async () => {
      const unbound = new MotionPlayer(mockSelfExpressions);
      await expect(unbound.play("wave")).resolves.toBeUndefined();
    });
  });
});
