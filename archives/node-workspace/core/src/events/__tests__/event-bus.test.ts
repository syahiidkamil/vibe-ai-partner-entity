import { describe, it, expect, vi } from "vitest";
import { EventBus } from "../event-bus";

// Simple test event map
interface TestEventMap {
  "test:simple": { value: number };
  "test:complex": { name: string; items: string[] };
  "test:empty": {};
}

describe("EventBus", () => {
  it("should emit and receive events", () => {
    const bus = new EventBus<TestEventMap>();
    const handler = vi.fn();

    bus.on("test:simple", handler);
    bus.emit("test:simple", { value: 42 });

    expect(handler).toHaveBeenCalledWith({ value: 42 });
    expect(handler).toHaveBeenCalledTimes(1);
  });

  it("should support multiple listeners", () => {
    const bus = new EventBus<TestEventMap>();
    const handler1 = vi.fn();
    const handler2 = vi.fn();

    bus.on("test:simple", handler1);
    bus.on("test:simple", handler2);
    bus.emit("test:simple", { value: 10 });

    expect(handler1).toHaveBeenCalledWith({ value: 10 });
    expect(handler2).toHaveBeenCalledWith({ value: 10 });
  });

  it("should remove specific listener with off()", () => {
    const bus = new EventBus<TestEventMap>();
    const handler1 = vi.fn();
    const handler2 = vi.fn();

    bus.on("test:simple", handler1);
    bus.on("test:simple", handler2);
    bus.off("test:simple", handler1);
    bus.emit("test:simple", { value: 5 });

    expect(handler1).not.toHaveBeenCalled();
    expect(handler2).toHaveBeenCalledWith({ value: 5 });
  });

  it("should fire once() handler only once", () => {
    const bus = new EventBus<TestEventMap>();
    const handler = vi.fn();

    bus.once("test:simple", handler);
    bus.emit("test:simple", { value: 1 });
    bus.emit("test:simple", { value: 2 });

    expect(handler).toHaveBeenCalledTimes(1);
    expect(handler).toHaveBeenCalledWith({ value: 1 });
  });

  it("should remove all listeners for an event", () => {
    const bus = new EventBus<TestEventMap>();
    const handler1 = vi.fn();
    const handler2 = vi.fn();

    bus.on("test:simple", handler1);
    bus.on("test:simple", handler2);
    bus.removeAllListeners("test:simple");
    bus.emit("test:simple", { value: 99 });

    expect(handler1).not.toHaveBeenCalled();
    expect(handler2).not.toHaveBeenCalled();
  });

  it("should remove all listeners globally", () => {
    const bus = new EventBus<TestEventMap>();
    const simpleHandler = vi.fn();
    const complexHandler = vi.fn();

    bus.on("test:simple", simpleHandler);
    bus.on("test:complex", complexHandler);
    bus.removeAllListeners();
    bus.emit("test:simple", { value: 1 });
    bus.emit("test:complex", { name: "x", items: [] });

    expect(simpleHandler).not.toHaveBeenCalled();
    expect(complexHandler).not.toHaveBeenCalled();
  });

  it("should not throw when emitting with no listeners", () => {
    const bus = new EventBus<TestEventMap>();

    expect(() => {
      bus.emit("test:simple", { value: 1 });
    }).not.toThrow();
  });
});
