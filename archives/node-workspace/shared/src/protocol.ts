import type { FeelingName, StateName } from "./constants.js";
import type { InternalStates, FeelingMap, StateAdjustment } from "./types.js";

// ═══════════════════════════════════════════════════════════════
// REST Request/Response Types (Layer 1: HTTP)
// ═══════════════════════════════════════════════════════════════

// POST /api/speak
export interface SpeakRequest {
  text: string;
  voice?: string;
  speed?: number;
}

// POST /api/feeling
export interface FeelingRequest {
  name: FeelingName;
}

// POST /api/action
export interface ActionRequest {
  name: string;
}

// POST /api/state
export interface StateAdjustRequest {
  adjustments: StateAdjustment[];
}

// GET /api/health
export interface HealthResponse {
  status: "ok" | "error";
  engine: string;
  uptime: number;
}

// GET /api/state, POST /api/state response
export interface StateResponse {
  states: InternalStates;
  feelings: FeelingMap;
  expressionsTriggered: string[];
}

// ═══════════════════════════════════════════════════════════════
// WebSocket Message Types (Layer 2: Real-time)
// ═══════════════════════════════════════════════════════════════

// ─── Status channel (/ws/status) ─────────────────────────────

export interface WSStateUpdate {
  type: "state";
  mode: string;
  mood: string;
}

export interface WSAmplitude {
  type: "amplitude";
  value: number;
  timestamp: number;
}

export interface WSFeelingUpdate {
  type: "feeling";
  name: FeelingName;
}

export interface WSActionUpdate {
  type: "action";
  name: string;
}

// Union of all status channel messages
export type WSStatusMessage =
  | WSStateUpdate
  | WSAmplitude
  | WSFeelingUpdate
  | WSActionUpdate;

// ─── Audio channel (/ws/audio) ───────────────────────────────

export interface WSAudioChunk {
  type: "audio_chunk";
  data: string; // base64-encoded PCM
  sampleRate: number;
  isLast: boolean;
}

// ─── Expression fired (event bus → WebSocket) ────────────────

export interface WSExpressionFired {
  type: "expression_fired";
  expression: string;
  feeling: FeelingName;
  intensity: number;
}

// ─── Union of all WebSocket messages ─────────────────────────

export type WSMessage =
  | WSStatusMessage
  | WSAudioChunk
  | WSExpressionFired;
