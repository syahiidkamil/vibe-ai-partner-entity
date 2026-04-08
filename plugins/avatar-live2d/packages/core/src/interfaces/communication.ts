import type { InternalStates, FeelingMap } from "@vibe-ai-partner/shared";

/**
 * Complete event map for the internal event bus.
 *
 * Three categories:
 * 1. State/feeling changes (from FeelingEngine)
 * 2. Avatar/TTS commands (from WebSocket client or direct calls)
 * 3. Plugin lifecycle and configuration
 */
export interface EventMap {
  // ─── State changes ───────────────────────────────────────
  "state:changed": { state: InternalStates };
  "feeling:changed": { feelings: FeelingMap };
  "feeling:threshold": { feeling: string; level: number };

  // ─── Avatar commands ─────────────────────────────────────
  "avatar:feeling": { name: string; intensity: number };
  "avatar:self-expression": { name: string };

  // ─── TTS events ──────────────────────────────────────────
  "tts:amplitude": { value: number };
  "tts:speaking-start": { text: string };
  "tts:speaking-stop": Record<string, never>;

  // ─── External commands (CLI → server → WebSocket → app) ──
  "command:feeling": { name: string };
  "command:action": { name: string };
  "command:speak": { text: string; voice?: string };

  // ─── Plugin lifecycle ────────────────────────────────────
  "plugin:activated": { id: string; type: string };
  "plugin:deactivated": { id: string; type: string };

  // ─── Configuration ───────────────────────────────────────
  "config:changed": { key: string; value: unknown };
}

/**
 * Typed event bus for internal inter-component communication.
 *
 * All communication between components within the desktop app
 * goes through this bus. Components never import each other directly.
 *
 * Usage:
 *   eventBus.on("feeling:changed", ({ feelings }) => { ... });
 *   eventBus.emit("avatar:feeling", { name: "happy", intensity: 82 });
 */
export interface IEventBus {
  /**
   * Subscribe to an event. Returns an unsubscribe function.
   * @param event - Event name from EventMap
   * @param handler - Callback receiving the typed payload
   * @returns Unsubscribe function — call to remove this listener
   */
  on<K extends keyof EventMap>(
    event: K,
    handler: (payload: EventMap[K]) => void,
  ): () => void;

  /**
   * Subscribe to an event for a single firing. Auto-unsubscribes after first call.
   * @param event - Event name from EventMap
   * @param handler - Callback receiving the typed payload
   */
  once<K extends keyof EventMap>(
    event: K,
    handler: (payload: EventMap[K]) => void,
  ): void;

  /**
   * Emit an event to all subscribers.
   * @param event - Event name from EventMap
   * @param payload - Typed payload matching the event
   */
  emit<K extends keyof EventMap>(
    event: K,
    payload: EventMap[K],
  ): void;

  /**
   * Remove all listeners for a specific event, or all listeners entirely.
   * @param event - Optional. If provided, clears only that event's listeners.
   */
  off<K extends keyof EventMap>(event?: K): void;
}
