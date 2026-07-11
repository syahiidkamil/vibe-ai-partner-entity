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
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from engine.apps.tts import TTSApp
from engine.apps.avatar import AvatarApp
from engine.cli._config import get_avatar_renderer, write_config
from engine.server.sentiment import analyze_sentiment
from engine.server.state_manager import StateManager


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
RENDERERS_DIR = ROOT_DIR / "vape" / "plugins" / "renderers"
SHELLS_DIR = ROOT_DIR / "vape" / "plugins" / "shells"


# ═══════════════════════════════════════════════════════════════
# Pydantic models
# ═══════════════════════════════════════════════════════════════

class SpeakRequest(BaseModel):
    text: str
    voice: str | None = None
    speed: float | None = None
    volume: int | None = None  # 0-100, this utterance only; None -> standing tts.volume

class FeelingRequest(BaseModel):
    name: str

class ActionRequest(BaseModel):
    name: str
    text: str | None = None

class StateAdjustment(BaseModel):
    state: str
    delta: float

class StateAdjustRequest(BaseModel):
    adjustments: list[StateAdjustment]

class VoiceRequest(BaseModel):
    voice: str

class VolumeRequest(BaseModel):
    volume: int

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
        config = json.loads((ROOT_DIR / "config.json").read_text(encoding="utf-8"))
        return config.get("entity", {}).get("vocalMode", "silent")
    except (FileNotFoundError, json.JSONDecodeError):
        return os.getenv("ENTITY_VOCAL_MODE", "silent")


def _get_standing_volume() -> int:
    """Standing speech volume (0-100) from config.json; read per clip so
    `vape volume N` takes effect without a server restart."""
    try:
        config = json.loads((ROOT_DIR / "config.json").read_text(encoding="utf-8"))
        return int(config.get("tts", {}).get("volume", 100))
    except (FileNotFoundError, json.JSONDecodeError, TypeError, ValueError):
        return 100

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


# Audio is delivered over HTTP (not as a local file path) so any shell —
# Electron, Tauri, or a plain browser — can play it same-origin. The TTS
# pipeline writes a temp WAV; we register it under a token, broadcast the URL,
# and serve + reap it here.
# Generous TTL so a long multi-sentence utterance (clips play sequentially) is
# never swept before the renderer reaches it in its play queue.
_AUDIO_TTL = 600.0  # seconds before an unfetched clip is swept
_audio_clips: dict[str, tuple[str, float]] = {}


def _purge_audio_clips() -> None:
    """Remove all registered temp WAVs (called on shutdown)."""
    for path, _ in _audio_clips.values():
        try:
            os.remove(path)
        except OSError:
            pass
    _audio_clips.clear()


def _sweep_audio_clips() -> None:
    now = time.time()
    for name, (path, created) in list(_audio_clips.items()):
        if now - created > _AUDIO_TTL:
            _audio_clips.pop(name, None)
            try:
                os.remove(path)
            except OSError:
                pass


async def _broadcast_audio(wav_path: str, text: str, is_last: bool, volume: int | None = None) -> None:
    _sweep_audio_clips()
    name = f"{uuid.uuid4().hex}.wav"
    _audio_clips[name] = (wav_path, time.time())
    effective = volume if volume is not None else _get_standing_volume()
    effective = max(0, min(100, effective))
    await manager.broadcast_audio({
        "type": "audio", "url": f"/audio/{name}", "text": text,
        "isLast": is_last, "volume": effective,
    })

async def _broadcast_action(name: str) -> None:
    """Resolve system expression trigger via avatar interface, then broadcast."""
    resolved = avatar.resolve_action(name) if avatar else name
    if resolved is not None:
        await manager.broadcast_status({"type": "action", "name": resolved})


async def _broadcast_caption(text: str) -> None:
    """Show bubble text with no audio behind it — over the same channel as a
    spoken clip (`type` just differs), so the renderer needs no new socket."""
    await manager.broadcast_audio({"type": "caption", "text": text})


# Default caption for actions that carry their own line but no voice — TTS
# reading "hahaha" comes out as stilted speech, not a laugh, so this is
# caption-only, no audio. A caller can override the text per-call (ActionRequest.text).
_ACTION_CAPTION_LINES: dict[str, str] = {
    "laugh": "Hahaha!",
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    global tts, avatar, start_time
    start_time = time.time()

    # Create TTS app via factory — discovers plugins, loads config, wires pipeline
    tts = TTSApp.create(ROOT_DIR / "config.json", _broadcast_audio)

    # Discover avatar renderers + shells and resolve the active renderer
    avatar = AvatarApp(RENDERERS_DIR, SHELLS_DIR)
    config_renderer = get_avatar_renderer()
    if avatar.get_active(config_renderer) is None:
        print(
            f"[avatar] configured renderer '{config_renderer}' is not available — "
            f"interface/static serving disabled until it is built",
            flush=True,
        )

    # Generate interface contract (expression aliases, capabilities)
    avatar.generate_interface(config_renderer)

    yield

    # Cleanup
    if tts:
        tts.shutdown()
    _purge_audio_clips()


app = FastAPI(title="Vibe TTS Server", version="0.1.0", lifespan=lifespan)


# ═══════════════════════════════════════════════════════════════
# REST Routes — delegate TTS to TTSApp
# ═══════════════════════════════════════════════════════════════

@app.post("/api/speak")
async def speak(req: SpeakRequest):
    if not tts:
        return {"status": "error", "message": "No TTS engine available"}
    asyncio.create_task(tts.speak(req.text, voice=req.voice, speed=req.speed, volume=req.volume))
    return {"status": "ok"}

@app.post("/api/feeling")
async def feeling(req: FeelingRequest):
    await manager.broadcast_status({"type": "feeling", "name": req.name})
    return {"status": "ok"}

@app.post("/api/action")
async def action(req: ActionRequest):
    await _broadcast_action(req.name)
    caption = req.text or _ACTION_CAPTION_LINES.get(req.name)
    if caption:
        await _broadcast_caption(caption)
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

@app.get("/api/volume")
async def get_volume():
    return {"volume": _get_standing_volume()}

@app.post("/api/volume")
async def set_volume(req: VolumeRequest):
    level = max(0, min(100, req.volume))
    write_config({"tts": {"volume": level}})
    return {"status": "ok", "volume": level}

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
    # In-process raise, not os.kill: on Windows os.kill(pid, SIGTERM) is a hard
    # TerminateProcess (the shutdown lifespan never runs, temp WAVs leak), while
    # raise_signal triggers uvicorn's signal.signal handler → graceful exit.
    # On POSIX the two are equivalent for our own pid.
    signal.raise_signal(signal.SIGTERM)
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

@app.get("/audio/{name}")
async def audio_clip(name: str):
    """Serve a TTS clip by token (broadcast over /ws/audio as a URL)."""
    entry = _audio_clips.get(name)
    if not entry or not os.path.exists(entry[0]):
        return Response(status_code=404)
    # Refresh TTL on access so an actively-playing clip isn't swept mid-queue.
    _audio_clips[name] = (entry[0], time.time())
    return FileResponse(entry[0], media_type="audio/wav")


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

class NoCacheStaticFiles(StaticFiles):
    """Serve avatar assets with ``Cache-Control: no-store``.

    The model/expressions/textures are local files served over loopback and loaded
    once per launch, so HTTP caching saves ~nothing — but a stale WebKit copy
    silently renders the pre-edit model/expression until the cache is hand-cleared
    (the bug that makes an edited .exp3.json look like it "didn't take"). no-store
    removes that trap entirely.
    """

    def file_response(self, *args: Any, **kwargs: Any) -> Response:
        resp = super().file_response(*args, **kwargs)
        resp.headers["Cache-Control"] = "no-store"
        return resp


def _mount_avatar() -> None:
    """Serve the active renderer at / so any shell can load it over HTTP."""
    _avatar_app = AvatarApp(RENDERERS_DIR)
    _renderer = get_avatar_renderer()
    _dir = _avatar_app.get_static_dir(_renderer)
    if _dir and _dir.is_dir():
        app.mount("/", NoCacheStaticFiles(directory=str(_dir), html=True), name="avatar")
    else:
        print(
            f"[avatar] renderer '{_renderer}' not found under {RENDERERS_DIR} — "
            f"the avatar window will have nothing to load",
            flush=True,
        )

_mount_avatar()
