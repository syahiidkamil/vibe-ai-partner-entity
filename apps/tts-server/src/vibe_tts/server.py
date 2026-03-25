"""
Vibe TTS Server — FastAPI app with REST + WebSocket endpoints.

Routes match the protocol types from @vibe-ai-partner/shared:
  - SpeakRequest, FeelingRequest, ActionRequest, StateAdjustRequest
  - HealthResponse, StateResponse
  - WSStatusMessage, WSAudioChunk
"""

from __future__ import annotations

import asyncio
import os
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

from vibe_tts.audio_player import AudioPlayer
from vibe_tts.engine_registry import EngineRegistry
from vibe_tts.pipeline import TTSPipeline
from vibe_tts.sentiment import analyze_sentiment
from vibe_tts.state_manager import StateManager


# ═══════════════════════════════════════════════════════════════
# Pydantic models — mirrors of shared/protocol.ts types
# ═══════════════════════════════════════════════════════════════

class SpeakRequest(BaseModel):
    """POST /api/speak — mirrors SpeakRequest from protocol.ts"""
    text: str
    voice: str | None = None
    speed: float | None = None

class FeelingRequest(BaseModel):
    """POST /api/feeling — mirrors FeelingRequest from protocol.ts"""
    name: str

class ActionRequest(BaseModel):
    """POST /api/action — mirrors ActionRequest from protocol.ts"""
    name: str

class StateAdjustment(BaseModel):
    """Single state delta — mirrors StateAdjustment from types.ts"""
    state: str
    delta: float

class StateAdjustRequest(BaseModel):
    """POST /api/state — mirrors StateAdjustRequest from protocol.ts"""
    adjustments: list[StateAdjustment]

class VoiceRequest(BaseModel):
    """POST /api/voice — switch active voice"""
    voice: str

class HookEvent(BaseModel):
    """POST /api/hook — receives Claude Code hook events."""
    hook_event_name: str
    session_id: str | None = None
    tool_name: str | None = None
    tool_input: dict | None = None
    tool_output: str | None = None
    tool_error: str | None = None
    user_prompt: str | None = None
    stop_response: str | None = None
    session_trigger: str | None = None
    sentiment: dict | None = None


# ═══════════════════════════════════════════════════════════════
# Vocal mode
# ═══════════════════════════════════════════════════════════════

VOCAL_MODE = os.getenv("ENTITY_VOCAL_MODE", "silent")


def _should_speak(sentiment: dict) -> bool:
    """Check if vocal mode allows speaking for this sentiment."""
    speak_text = sentiment.get("speak", "")
    if not speak_text:
        return False
    if VOCAL_MODE == "silent":
        return False
    if VOCAL_MODE == "reactive":
        return sentiment.get("intensity", 0) > 80
    if VOCAL_MODE == "conversational":
        return True
    return False


# ═══════════════════════════════════════════════════════════════
# WebSocket connection manager
# ═══════════════════════════════════════════════════════════════

class ConnectionManager:
    """Manages WebSocket connections for status and audio channels."""

    def __init__(self) -> None:
        self.status_clients: list[WebSocket] = []
        self.audio_clients: list[WebSocket] = []

    async def connect_status(self, ws: WebSocket) -> None:
        await ws.accept()
        self.status_clients.append(ws)

    async def connect_audio(self, ws: WebSocket) -> None:
        await ws.accept()
        self.audio_clients.append(ws)

    def disconnect_status(self, ws: WebSocket) -> None:
        self.status_clients.remove(ws)

    def disconnect_audio(self, ws: WebSocket) -> None:
        self.audio_clients.remove(ws)

    async def broadcast_status(self, message: dict[str, Any]) -> None:
        """Broadcast JSON to all /ws/status clients."""
        dead: list[WebSocket] = []
        for ws in self.status_clients:
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.status_clients.remove(ws)

    async def broadcast_audio(self, message: dict[str, Any]) -> None:
        """Broadcast JSON to all /ws/audio clients."""
        dead: list[WebSocket] = []
        for ws in self.audio_clients:
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.audio_clients.remove(ws)


# ═══════════════════════════════════════════════════════════════
# Application setup
# ═══════════════════════════════════════════════════════════════

manager = ConnectionManager()
registry = EngineRegistry()
state_mgr = StateManager()
audio_player = AudioPlayer()
pipeline: TTSPipeline | None = None
start_time: float = 0.0


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: register engines, load default. Shutdown: cleanup."""
    global pipeline, start_time
    start_time = time.time()

    # Register available engines (try-import, skip if deps missing)
    try:
        from vibe_plugin_tts_kokoro import KokoroEngine
        registry.register("kokoro", KokoroEngine())
    except ImportError:
        pass

    try:
        from vibe_plugin_tts_kokoro_onnx import KokoroOnnxEngine
        registry.register("kokoro-onnx", KokoroOnnxEngine())
    except ImportError:
        pass

    try:
        from vibe_plugin_tts_kitten import KittenEngine
        registry.register("kitten", KittenEngine())
    except ImportError:
        pass

    # Activate first available engine
    available = registry.list()
    if available:
        registry.switch(available[0])

    # Wire up pipeline with broadcast callbacks
    pipeline = TTSPipeline(
        registry=registry,
        audio_player=audio_player,
        on_amplitude=_broadcast_amplitude,
        on_audio_chunk=_broadcast_audio_chunk,
    )

    yield

    # Cleanup
    active = registry.get_active()
    if active:
        active.stop()


app = FastAPI(title="Vibe TTS Server", version="0.1.0", lifespan=lifespan)


# ═══════════════════════════════════════════════════════════════
# Broadcast helpers (called from pipeline during generation)
# ═══════════════════════════════════════════════════════════════

async def _broadcast_amplitude(value: float) -> None:
    """Send amplitude update to /ws/status clients."""
    await manager.broadcast_status({
        "type": "amplitude",
        "value": value,
        "timestamp": time.time(),
    })

async def _broadcast_audio_chunk(data_b64: str, sample_rate: int, is_last: bool) -> None:
    """Send audio chunk to /ws/audio clients."""
    await manager.broadcast_audio({
        "type": "audio_chunk",
        "data": data_b64,
        "sampleRate": sample_rate,
        "isLast": is_last,
    })


# ═══════════════════════════════════════════════════════════════
# REST Routes
# ═══════════════════════════════════════════════════════════════

@app.post("/api/speak")
async def speak(req: SpeakRequest):
    """Generate TTS audio, stream via WebSocket. Non-blocking."""
    if not pipeline:
        return {"status": "error", "message": "No TTS engine available"}

    # Broadcast speaking state
    await manager.broadcast_status({"type": "state", "mode": "speaking", "mood": ""})

    # Run generation in background so the HTTP response returns immediately
    asyncio.create_task(
        pipeline.speak(req.text, voice=req.voice, speed=req.speed)
    )

    return {"status": "ok"}


@app.post("/api/feeling")
async def feeling(req: FeelingRequest):
    """Set a feeling — broadcast to /ws/status."""
    await manager.broadcast_status({"type": "feeling", "name": req.name})
    return {"status": "ok"}


@app.post("/api/action")
async def action(req: ActionRequest):
    """Trigger an action — broadcast to /ws/status."""
    await manager.broadcast_status({"type": "action", "name": req.name})
    return {"status": "ok"}


@app.post("/api/state")
async def adjust_state(req: StateAdjustRequest):
    """
    Apply state adjustments, recalculate feelings, check expression thresholds.
    Returns full StateResponse (mirrors protocol.ts StateResponse).
    """
    result = state_mgr.adjust(
        [(adj.state, adj.delta) for adj in req.adjustments]
    )

    # Broadcast any triggered expressions
    for expr in result["expressionsTriggered"]:
        await manager.broadcast_status({"type": "action", "name": expr})

    return result


@app.post("/api/hook")
async def hook(event: HookEvent):
    """
    Receive Claude Code hook events. Translate to state adjustments,
    broadcast expressions, handle sentiment on Stop events.
    """
    name = event.hook_event_name

    # Track session ID
    if event.session_id:
        state_mgr._session_id = event.session_id

    # SessionStart: load previous state with decay
    if name == "SessionStart":
        saved = state_mgr.load_state()
        if saved and saved.get("timestamp"):
            try:
                last_time = datetime.fromisoformat(saved["timestamp"])
                now = datetime.now(timezone.utc)
                hours = (now - last_time).total_seconds() / 3600
                state_mgr.apply_decay(hours)
            except (ValueError, TypeError):
                pass

    # Get hook adjustments and apply
    adjustments = state_mgr.get_hook_adjustments(name, event.tool_name)
    result = state_mgr.adjust(adjustments)

    # Broadcast triggered expressions
    for expr in result["expressionsTriggered"]:
        await manager.broadcast_status({"type": "action", "name": expr})

    # SessionStart: broadcast wave
    if name == "SessionStart":
        await manager.broadcast_status({"type": "action", "name": "wave"})

    # Stop: handle sentiment analysis
    if name == "Stop":
        sentiment = event.sentiment
        if not sentiment and event.stop_response:
            sentiment = analyze_sentiment(event.stop_response)

        if sentiment:
            feeling = sentiment.get("feeling", "calm")
            intensity = sentiment.get("intensity", 30)
            sent_result = state_mgr.apply_sentiment(feeling, intensity)

            # Broadcast sentiment-triggered expressions
            for expr in sent_result["expressionsTriggered"]:
                await manager.broadcast_status({"type": "action", "name": expr})

            # Broadcast suggested action
            action_name = sentiment.get("action", "none")
            if action_name and action_name != "none":
                await manager.broadcast_status({"type": "action", "name": action_name})

            # Vocal mode check for speak
            if pipeline and _should_speak(sentiment):
                asyncio.create_task(pipeline.speak(sentiment["speak"]))

            result = sent_result

    return {"continue": True, **result}


@app.post("/api/voice")
async def switch_voice(req: VoiceRequest):
    """Switch the active voice on the current engine."""
    active = registry.get_active()
    if not active:
        return {"status": "error", "message": "No engine active"}
    active.set_voice(req.voice)
    return {"status": "ok"}


@app.post("/api/stop")
async def stop():
    """Abort current TTS generation/playback."""
    active = registry.get_active()
    if active:
        active.stop()
    audio_player.stop()
    await manager.broadcast_status({"type": "state", "mode": "idle", "mood": ""})
    return {"status": "ok"}


@app.get("/api/health")
async def health():
    """Health check — mirrors HealthResponse from protocol.ts."""
    active = registry.get_active()
    return {
        "status": "ok",
        "engine": active.name if active else "none",
        "uptime": round(time.time() - start_time),
    }


@app.get("/api/voices")
async def voices():
    """List voices for the active engine."""
    active = registry.get_active()
    if not active:
        return {"voices": []}
    voice_list = active.get_voices()
    return {"voices": voice_list}


# ═══════════════════════════════════════════════════════════════
# WebSocket Endpoints
# ═══════════════════════════════════════════════════════════════

@app.websocket("/ws/status")
async def ws_status(ws: WebSocket):
    """
    Status channel — broadcasts state, amplitude, feeling, action updates.
    Message types: WSStateUpdate, WSAmplitude, WSFeelingUpdate, WSActionUpdate
    """
    await manager.connect_status(ws)
    try:
        while True:
            # Keep connection alive. Client can send pings.
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect_status(ws)


@app.websocket("/ws/audio")
async def ws_audio(ws: WebSocket):
    """
    Audio channel — streams PCM audio chunks as base64 JSON.
    Message type: WSAudioChunk { type, data, sampleRate, isLast }
    """
    await manager.connect_audio(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect_audio(ws)
