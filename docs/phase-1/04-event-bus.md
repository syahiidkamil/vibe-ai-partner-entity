# Step 4 — EventBus Implementation

## `packages/core/src/events/event-bus.ts`

A typed EventEmitter that enforces type safety for event names and payloads. No external dependencies — pure TypeScript.

```typescript
// Typed event emitter
type EventHandler<T> = (data: T) => void;

export class EventBus<TEventMap extends Record<string, unknown>> {
  private listeners = new Map<keyof TEventMap, Set<EventHandler<any>>>();

  on<K extends keyof TEventMap>(event: K, handler: EventHandler<TEventMap[K]>): void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event)!.add(handler);
  }

  off<K extends keyof TEventMap>(event: K, handler: EventHandler<TEventMap[K]>): void {
    this.listeners.get(event)?.delete(handler);
  }

  once<K extends keyof TEventMap>(event: K, handler: EventHandler<TEventMap[K]>): void {
    const wrapped = (data: TEventMap[K]) => {
      handler(data);
      this.off(event, wrapped);
    };
    this.on(event, wrapped);
  }

  emit<K extends keyof TEventMap>(event: K, data: TEventMap[K]): void {
    this.listeners.get(event)?.forEach(handler => handler(data));
  }

  removeAllListeners(event?: keyof TEventMap): void {
    if (event) {
      this.listeners.delete(event);
    } else {
      this.listeners.clear();
    }
  }
}
```

**Why not Node's EventEmitter?** Node's EventEmitter uses string keys with `any` payloads. This implementation gives compile-time errors when you emit the wrong data shape for an event name. The generic `TEventMap` enforces the contract.

---

## `packages/core/src/events/events.ts` — Complete EntityEventMap

This is the single source of truth for all events in the system. Every event name, every payload shape.

Derived from:
- [05-communication.md](../../architecture_after_review/05-communication.md) — State, feeling, avatar, TTS, command, plugin, config events
- [11-consciousness-system.md](../../architecture_after_review/11-consciousness-system.md) — Consciousness observation, pattern, choice, growth events

```typescript
import type { InternalStates, FeelingMap } from "@vibe-ai-partner/shared";

export interface EntityEventMap {
  // ── State changes ──────────────────────────────────────────────
  "state:changed": { states: InternalStates; previous: InternalStates };
  "state:adjusted": { state: string; delta: number; newValue: number };

  // ── Feeling changes ────────────────────────────────────────────
  "feeling:changed": { feelings: FeelingMap; previous: FeelingMap };
  "feeling:threshold": { feeling: string; intensity: number; direction: "up" | "down" };

  // ── Avatar events ──────────────────────────────────────────────
  "avatar:feeling": { name: string; intensity: number };
  "avatar:self-expression": { name: string };
  "avatar:mounted": { renderer: string };
  "avatar:unmounted": {};

  // ── TTS events ─────────────────────────────────────────────────
  "tts:amplitude": { value: number };
  "tts:speaking-start": { text: string };
  "tts:speaking-stop": {};

  // ── Command events (from CLI/server via WebSocket) ─────────────
  "command:feeling": { name: string };
  "command:action": { name: string };
  "command:speak": { text: string; voice?: string };

  // ── Plugin lifecycle ───────────────────────────────────────────
  "plugin:activated": { id: string; type: string };
  "plugin:deactivated": { id: string; type: string };

  // ── Configuration ──────────────────────────────────────────────
  "config:changed": { key: string; value: unknown };

  // ── Consciousness events ───────────────────────────────────────
  "consciousness:observation": { observation: string; states: InternalStates };
  "consciousness:pattern": { pattern: string; context: string };
  "consciousness:choice": { context: string; chosen: string; reason: string };
  "consciousness:growth": { newTruth: string; source: string };
}
```

### Usage

```typescript
import { EventBus } from "./event-bus";
import type { EntityEventMap } from "./events";

// Create a singleton event bus for the entity
const bus = new EventBus<EntityEventMap>();

// Type-safe — TS enforces the payload shape
bus.on("feeling:changed", ({ feelings, previous }) => {
  // feelings: FeelingMap, previous: FeelingMap — typed automatically
});

// Compile error: wrong payload shape
// bus.emit("feeling:changed", { wrong: true });  // TS error

// Compile error: unknown event name
// bus.on("nonexistent:event", () => {});  // TS error
```

### Barrel export

```typescript
// packages/core/src/events/index.ts
export { EventBus } from "./event-bus";
export type { EntityEventMap } from "./events";
```

---

## Unit Tests

### `packages/core/src/events/__tests__/event-bus.test.ts`

```typescript
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
```

---

## Verification

```bash
npx vitest run packages/core/src/events/__tests__/event-bus.test.ts
# All 7 tests should pass
```
