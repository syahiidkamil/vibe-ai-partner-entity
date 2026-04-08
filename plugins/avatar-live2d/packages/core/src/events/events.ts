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
