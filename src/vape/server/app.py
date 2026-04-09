"""
Vibe TTS Server — Thin HTTP/WebSocket layer.

Delegates all TTS operations to TTSApp (vibe.apps.tts).
Owns: HTTP routes, WebSocket management, state/sentiment (non-TTS domain).
"""

from __future__ import annotations

import asyncio
import json
import os
import signal
import time
from contextlib import asynccontextmanager
from pathlib import Path
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from vape.apps.tts import TTSApp
from vape.apps.avatar import AvatarApp
from vape.server.sentiment import analyze_sentiment
from vape.server.state_manager import StateManager


# ═══════════════════════════════════════════════════════════════
# Path helpers
# ═══════════════════════════════════════════════════════════════

def _find_root() -> Path:
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / ".git").exists() or (current / "config.json").exists():
            return current
        current = current.parent
    return Path(__file__).resolve().parents[3]

ROOT_DIR = _find_root()


# ═══════════════════════════════════════════════════════════════
# Pydantic models
# ═══════════════════════════════════════════════════════════════

class SpeakRequest(BaseModel):
    text: str
    voice: str | None = None
    speed: float | None = None

class FeelingRequest(BaseModel):
    name: str

class ActionRequest(BaseModel):
    name: str

class StateAdjustment(BaseModel):
    state: str
    delta: float

class StateAdjustRequest(BaseModel):
    adjustments: list[StateAdjustment]

class VoiceRequest(BaseModel):
    voice: str

class HookEvent(BaseModel):
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

def _get_vocal_mode() -> str:
    try:
        config = json.loads((ROOT_DIR / "config.json").read_text())
        return config.get("entity", {}).get("vocalMode", "silent")
    except (FileNotFoundError, json.JSONDecodeError):
        return os.getenv("ENTITY_VOCAL_MODE", "silent")

def _should_speak(sentiment: dict) -> bool:
    speak_text = sentiment.get("speak", "")
    if not speak_text:
        return False
    mode = _get_vocal_mode()
    if mode == "silent":
        return False
    if mode == "reactive":
        return sentiment.get("intensity", 0) > 80
    if mode == "conversational":
        return True
    return False


# ═══════════════════════════════════════════════════════════════
# WebSocket connection manager
# ═══════════════════════════════════════════════════════════════

class ConnectionManager:
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
        dead: list[WebSocket] = []
        for ws in self.status_clients:
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.status_clients.remove(ws)

    async def broadcast_audio(self, message: dict[str, Any]) -> None:
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
state_mgr = StateManager()
tts: TTSApp | None = None
avatar: AvatarApp | None = None
start_time: float = 0.0


async def _broadcast_audio(wav_path: str, text: str, is_last: bool) -> None:
    await manager.broadcast_audio({"type": "audio", "path": wav_path, "text": text, "isLast": is_last})

async def _broadcast_action(name: str) -> None:
    """Resolve system expression trigger via avatar interface, then broadcast."""
    resolved = avatar.resolve_action(name) if avatar else name
    if resolved is not None:
        await manager.broadcast_status({"type": "action", "name": resolved})


@asynccontextmanager
async def lifespan(app: FastAPI):
    global tts, avatar, start_time
    start_time = time.time()

    # Create TTS app via factory — discovers plugins, loads config, wires pipeline
    tts = TTSApp.create(ROOT_DIR / "config.json", _broadcast_audio)

    # Discover avatar plugins and mount the active one
    avatar = AvatarApp(ROOT_DIR / "plugins")
    config_plugin = None
    try:
        config = json.loads((ROOT_DIR / "config.json").read_text())
        config_plugin = config.get("avatar", {}).get("plugin")
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    # Generate interface contract (expression aliases, capabilities)
    avatar.generate_interface(config_plugin)

    yield

    # Cleanup
    if tts:
        tts.shutdown()


app = FastAPI(title="Vibe TTS Server", version="0.1.0", lifespan=lifespan)


# ═══════════════════════════════════════════════════════════════
# REST Routes — delegate TTS to TTSApp
# ═══════════════════════════════════════════════════════════════

@app.post("/api/speak")
async def speak(req: SpeakRequest):
    if not tts:
        return {"status": "error", "message": "No TTS engine available"}
    asyncio.create_task(tts.speak(req.text, voice=req.voice, speed=req.speed))
    return {"status": "ok"}

@app.post("/api/feeling")
async def feeling(req: FeelingRequest):
    await manager.broadcast_status({"type": "feeling", "name": req.name})
    return {"status": "ok"}

@app.post("/api/action")
async def action(req: ActionRequest):
    await _broadcast_action(req.name)
    return {"status": "ok"}

@app.post("/api/state")
async def adjust_state(req: StateAdjustRequest):
    result = state_mgr.adjust([(adj.state, adj.delta) for adj in req.adjustments])
    for expr in result["expressionsTriggered"]:
        await _broadcast_action(expr)
    return result

@app.post("/api/hook")
async def hook(event: HookEvent):
    name = event.hook_event_name
    if event.session_id:
        state_mgr._session_id = event.session_id

    if name == "SessionStart":
        saved = state_mgr.load_state()
        if saved and saved.get("timestamp"):
            try:
                last_time = datetime.fromisoformat(saved["timestamp"])
                hours = (datetime.now(timezone.utc) - last_time).total_seconds() / 3600
                state_mgr.apply_decay(hours)
            except (ValueError, TypeError):
                pass

    adjustments = state_mgr.get_hook_adjustments(name, event.tool_name)
    result = state_mgr.adjust(adjustments)

    for expr in result["expressionsTriggered"]:
        await _broadcast_action(expr)

    if name == "SessionStart":
        await _broadcast_action("wave")

    if name == "Stop":
        sentiment = event.sentiment
        if not sentiment and event.stop_response:
            sentiment = analyze_sentiment(event.stop_response)
        if sentiment:
            feeling_name = sentiment.get("feeling", "calm")
            intensity = sentiment.get("intensity", 30)
            sent_result = state_mgr.apply_sentiment(feeling_name, intensity)
            for expr in sent_result["expressionsTriggered"]:
                await _broadcast_action(expr)
            action_name = sentiment.get("action", "none")
            if action_name and action_name != "none":
                await _broadcast_action(action_name)
            if tts and _should_speak(sentiment):
                asyncio.create_task(tts.speak(sentiment["speak"]))
            result = sent_result

    return {"continue": True, **result}

@app.post("/api/voice")
async def switch_voice(req: VoiceRequest):
    if not tts:
        return {"status": "error", "message": "No engine active"}
    tts.switch_voice(req.voice)
    return {"status": "ok"}

@app.post("/api/stop")
async def stop():
    if tts:
        tts.stop()
    await manager.broadcast_status({"type": "state", "mode": "idle", "mood": ""})
    return {"status": "ok"}

@app.post("/api/shutdown")
async def shutdown():
    os.kill(os.getpid(), signal.SIGTERM)
    return {"status": "shutting_down"}

@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "engine": tts.active_engine_name if tts else "none",
        "uptime": round(time.time() - start_time),
    }

@app.get("/api/avatar/interface")
async def avatar_interface():
    if not avatar:
        return {"error": "No avatar loaded"}
    iface = avatar.get_interface()
    return iface or {"error": "No interface available"}

@app.get("/api/voices")
async def voices():
    if not tts:
        return {"voices": []}
    return {"voices": tts.get_voices()}


# ═══════════════════════════════════════════════════════════════
# WebSocket Endpoints
# ═══════════════════════════════════════════════════════════════

@app.websocket("/ws/status")
async def ws_status(ws: WebSocket):
    await manager.connect_status(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect_status(ws)

@app.websocket("/ws/audio")
async def ws_audio(ws: WebSocket):
    await manager.connect_audio(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect_audio(ws)


# ═══════════════════════════════════════════════════════════════
# Static Avatar Files (must be last — after all API/WS routes)
# ═══════════════════════════════════════════════════════════════

def _mount_avatar() -> None:
    """Mount avatar static files at module load time."""
    _avatar_app = AvatarApp(ROOT_DIR / "plugins")
    try:
        _config = json.loads((ROOT_DIR / "config.json").read_text())
        _renderer = _config.get("avatar", {}).get("plugin")
    except (FileNotFoundError, json.JSONDecodeError):
        _renderer = None
    _dir = _avatar_app.get_static_dir(_renderer)
    if _dir and _dir.is_dir():
        app.mount("/", StaticFiles(directory=str(_dir), html=True), name="avatar")

_mount_avatar()
