# TTS Server Implementation

Python FastAPI server that hosts TTS engines, streams audio, and broadcasts state/amplitude via WebSocket. Ported from the existing `live-ai-partner-avatar/kokoro-tts/daemon.py` (Unix socket) to a cross-platform HTTP + WebSocket architecture.

---

## Directory Structure

```
apps/tts-server/
├── pyproject.toml
├── requirements.txt
├── setup.sh                        # Create venv + install deps
├── Dockerfile
├── docker-compose.yml
└── src/vibe_tts/
    ├── __init__.py
    ├── server.py                   # FastAPI app + routes
    ├── engine_registry.py          # Multi-backend TTS registry
    ├── engines/
    │   ├── __init__.py
    │   ├── base.py                 # TTSEngineBase ABC
    │   ├── kokoro_engine.py        # Full Kokoro (PyTorch)
    │   └── kitten_engine.py        # KittenTTS
    ├── audio_player.py             # Playback + amplitude RMS
    ├── pipeline.py                 # Text -> chunks -> stream
    └── state_manager.py            # In-memory FeelingEngine mirror
```

---

## pyproject.toml

```toml
[project]
name = "vibe-tts"
version = "0.1.0"
description = "Vibe AI Partner TTS Server"
requires-python = ">=3.10,<3.13"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
    "numpy>=1.26.0",
    "sounddevice>=0.5.0",
]

[project.optional-dependencies]
kokoro = [
    "kokoro>=0.9.0",
    "torch>=2.0.0",
    "misaki[ja]>=0.8.0",
    "soundfile>=0.12.0",
]
kitten = [
    "kittentts>=0.2.0",
]
dev = [
    "pytest>=8.0.0",
    "httpx>=0.27.0",   # For testing FastAPI
]

[build-system]
requires = ["setuptools>=75.0"]
build-backend = "setuptools.backends._legacy:_Backend"

[tool.setuptools.packages.find]
where = ["src"]
```

---

## requirements.txt

Pinned subset for quick `pip install -r requirements.txt` without pyproject.toml:

```
fastapi>=0.115.0
uvicorn[standard]>=0.32.0
numpy>=1.26.0
sounddevice>=0.5.0
```

---

## server.py -- FastAPI App

All routes use the exact request/response shapes from `packages/shared/src/protocol.ts`.

```python
"""
Vibe TTS Server — FastAPI app with REST + WebSocket endpoints.

Routes match the protocol types from @vibe-ai-partner/shared:
  - SpeakRequest, FeelingRequest, ActionRequest, StateAdjustRequest
  - HealthResponse, StateResponse
  - WSStatusMessage, WSAudioChunk
"""

from __future__ import annotations

import asyncio
import time
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

from vibe_tts.audio_player import AudioPlayer
from vibe_tts.engine_registry import EngineRegistry
from vibe_tts.pipeline import TTSPipeline
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
        from vibe_tts.engines.kokoro_engine import KokoroEngine
        registry.register("kokoro", KokoroEngine())
    except ImportError:
        pass

    try:
        from vibe_tts.engines.kitten_engine import KittenEngine
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
```

---

## engine_registry.py

Registry pattern -- register engines by name, switch active engine, list available.

```python
"""
Multi-backend TTS engine registry.

Mirrors the EngineRegistry pattern from the architecture doc:
  register(name, engine)     — add engine to registry
  get_active() -> engine     — get currently active engine
  switch(name)               — switch active engine
  list() -> [names]          — list registered engine names
"""

from __future__ import annotations

from vibe_tts.engines.base import TTSEngineBase


class EngineRegistry:
    def __init__(self) -> None:
        self._engines: dict[str, TTSEngineBase] = {}
        self._active: str | None = None

    def register(self, name: str, engine: TTSEngineBase) -> None:
        """Register an engine. Does not activate it."""
        self._engines[name] = engine

    def get_active(self) -> TTSEngineBase | None:
        """Return the currently active engine, or None."""
        if self._active is None:
            return None
        return self._engines.get(self._active)

    def switch(self, name: str) -> None:
        """Switch the active engine. Raises KeyError if not registered."""
        if name not in self._engines:
            raise KeyError(f"Engine '{name}' not registered. Available: {list(self._engines.keys())}")

        # Stop current engine if switching
        current = self.get_active()
        if current:
            current.stop()

        self._engines[name].initialize()
        self._active = name

    def list(self) -> list[str]:
        """List all registered engine names."""
        return list(self._engines.keys())
```

---

## engines/base.py

Abstract base class for all TTS engines. Python equivalent of `ITTSEngine` from `packages/core/src/interfaces/tts-engine.ts`.

```python
"""
TTSEngineBase — abstract base class for TTS engines.

Python mirror of ITTSEngine from packages/core/src/interfaces/tts-engine.ts.
All engines: Text in -> Audio out (numpy float32 arrays at a given sample rate).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import AsyncIterator


@dataclass
class VoiceInfo:
    """Mirrors VoiceInfo from tts-engine.ts."""
    id: str
    name: str
    language: str
    gender: str  # "male" | "female" | "neutral"


@dataclass
class AudioChunk:
    """A chunk of generated audio (numpy float32 array)."""
    samples: "np.ndarray"  # float32, mono
    sample_rate: int
    is_last: bool


class TTSEngineBase(ABC):
    """Abstract base for all TTS engines."""

    name: str = "base"

    @abstractmethod
    def initialize(self) -> None:
        """Load model / warm up pipeline. Called once on activation."""
        ...

    @abstractmethod
    def generate(self, text: str, voice: str | None = None, speed: float = 1.0) -> list[AudioChunk]:
        """
        Generate full audio from text. Returns list of AudioChunk.
        For non-streaming engines, returns a single chunk with is_last=True.
        """
        ...

    @abstractmethod
    async def generate_stream(self, text: str, voice: str | None = None, speed: float = 1.0) -> AsyncIterator[AudioChunk]:
        """
        Yield audio chunks as they are generated.
        Engines that don't natively stream yield a single chunk.
        """
        ...

    @abstractmethod
    def get_voices(self) -> list[dict]:
        """
        Return list of available voices.
        Each voice: {"id": "af_heart", "name": "Heart", "language": "en-us", "gender": "female"}
        """
        ...

    @abstractmethod
    def set_voice(self, voice_id: str) -> None:
        """Set the active voice for subsequent generation calls."""
        ...

    @abstractmethod
    def stop(self) -> None:
        """Abort current generation/playback immediately."""
        ...
```

---

## engines/kokoro_engine.py

Full Kokoro adapter. Ported from `live-ai-partner-avatar/kokoro-tts/daemon.py` -- replaces Unix socket with method calls, adds streaming and voice catalog.

```python
"""
Kokoro TTS Engine — full PyTorch model via KPipeline.

Ported from live-ai-partner-avatar/kokoro-tts/daemon.py.
Key differences from the original daemon:
  - No Unix socket — called directly via EngineRegistry
  - Streaming via generate_stream() (yields per-sentence chunks)
  - Voice catalog from KPipeline
  - Amplitude computed externally by AudioPlayer
"""

from __future__ import annotations

import threading

import numpy as np
from kokoro import KPipeline

from vibe_tts.engines.base import AudioChunk, TTSEngineBase


# Voice prefix -> KPipeline lang_code (same mapping as original daemon)
VOICE_LANG_MAP: dict[str, str] = {
    "a": "a", "b": "b", "e": "e", "f": "f",
    "h": "h", "i": "i", "j": "j", "p": "p", "z": "z",
}

# Known voices with metadata (subset — full list in Kokoro docs)
KOKORO_VOICES = [
    {"id": "af_heart",   "name": "Heart (Female)",   "language": "en-us", "gender": "female"},
    {"id": "af_bella",   "name": "Bella (Female)",   "language": "en-us", "gender": "female"},
    {"id": "am_adam",    "name": "Adam (Male)",       "language": "en-us", "gender": "male"},
    {"id": "am_michael", "name": "Michael (Male)",    "language": "en-us", "gender": "male"},
    {"id": "bf_emma",    "name": "Emma (British F)",  "language": "en-gb", "gender": "female"},
    {"id": "bm_george",  "name": "George (British M)","language": "en-gb", "gender": "male"},
    {"id": "jf_alpha",   "name": "Alpha (Japanese F)","language": "ja",    "gender": "female"},
    {"id": "jm_beta",    "name": "Beta (Japanese M)", "language": "ja",    "gender": "male"},
]

MAX_CHARS = 300


class KokoroEngine(TTSEngineBase):
    name = "kokoro"

    def __init__(self) -> None:
        self._pipelines: dict[str, KPipeline] = {}
        self._pipelines_lock = threading.Lock()
        self._voice: str = "af_heart"
        self._stop_event = threading.Event()

    def initialize(self) -> None:
        """Pre-load the English pipeline (same as original daemon startup)."""
        self._get_pipeline("a")

    def _get_pipeline(self, lang_code: str) -> KPipeline:
        """Get or create a KPipeline for the given language code."""
        with self._pipelines_lock:
            if lang_code not in self._pipelines:
                self._pipelines[lang_code] = KPipeline(lang_code=lang_code)
            return self._pipelines[lang_code]

    def _lang_code_from_voice(self, voice: str) -> str:
        """Auto-detect lang_code from voice name prefix."""
        if voice and len(voice) >= 1:
            return VOICE_LANG_MAP.get(voice[0], "a")
        return "a"

    def generate(self, text: str, voice: str | None = None, speed: float = 1.0) -> list[AudioChunk]:
        """Generate all audio, return as a single chunk."""
        voice = voice or self._voice
        self._stop_event.clear()

        if len(text) > MAX_CHARS:
            text = text[:MAX_CHARS].rsplit(" ", 1)[0]

        lang_code = self._lang_code_from_voice(voice)
        pipeline = self._get_pipeline(lang_code)

        chunks: list[np.ndarray] = []
        for _, _, audio in pipeline(text, voice=voice, speed=speed):
            if self._stop_event.is_set():
                break
            chunks.append(audio)

        if not chunks:
            return []

        combined = np.concatenate(chunks)
        return [AudioChunk(samples=combined, sample_rate=24000, is_last=True)]

    async def generate_stream(self, text: str, voice: str | None = None, speed: float = 1.0):
        """Yield audio per-sentence as KPipeline produces it."""
        voice = voice or self._voice
        self._stop_event.clear()

        if len(text) > MAX_CHARS:
            text = text[:MAX_CHARS].rsplit(" ", 1)[0]

        lang_code = self._lang_code_from_voice(voice)
        pipeline = self._get_pipeline(lang_code)

        sentence_chunks = list(pipeline(text, voice=voice, speed=speed))
        for i, (_, _, audio) in enumerate(sentence_chunks):
            if self._stop_event.is_set():
                break
            is_last = i == len(sentence_chunks) - 1
            yield AudioChunk(samples=audio, sample_rate=24000, is_last=is_last)

    def get_voices(self) -> list[dict]:
        return KOKORO_VOICES

    def set_voice(self, voice_id: str) -> None:
        self._voice = voice_id

    def stop(self) -> None:
        self._stop_event.set()
```

---

## engines/kitten_engine.py

KittenTTS adapter -- ultra-lightweight, CPU-only, 8 voices.

```python
"""
KittenTTS Engine — 15M param model, CPU-only, 8 voices.

Simple API: model.generate(text, voice="Bella") -> audio array.
No streaming — generates full audio, returned as single chunk.
"""

from __future__ import annotations

import numpy as np
from kittentts import KittenTTS as KittenModel

from vibe_tts.engines.base import AudioChunk, TTSEngineBase


KITTEN_VOICES = [
    {"id": "Bella",  "name": "Bella",  "language": "en-us", "gender": "female"},
    {"id": "Luna",   "name": "Luna",   "language": "en-us", "gender": "female"},
    {"id": "Rosie",  "name": "Rosie",  "language": "en-us", "gender": "female"},
    {"id": "Kiki",   "name": "Kiki",   "language": "en-us", "gender": "female"},
    {"id": "Jasper", "name": "Jasper", "language": "en-us", "gender": "male"},
    {"id": "Bruno",  "name": "Bruno",  "language": "en-us", "gender": "male"},
    {"id": "Hugo",   "name": "Hugo",   "language": "en-us", "gender": "male"},
    {"id": "Leo",    "name": "Leo",    "language": "en-us", "gender": "male"},
]

KITTEN_SAMPLE_RATE = 24000


class KittenEngine(TTSEngineBase):
    name = "kitten"

    def __init__(self) -> None:
        self._model: KittenModel | None = None
        self._voice: str = "Bella"
        self._stopped = False

    def initialize(self) -> None:
        """Load KittenTTS model (auto-downloads from HuggingFace on first run)."""
        if self._model is None:
            self._model = KittenModel()

    def generate(self, text: str, voice: str | None = None, speed: float = 1.0) -> list[AudioChunk]:
        """Generate full audio — KittenTTS does not support streaming."""
        if self._model is None:
            raise RuntimeError("KittenEngine not initialized — call initialize() first")

        voice = voice or self._voice
        self._stopped = False

        audio = self._model.generate(text, voice=voice)

        if self._stopped:
            return []

        samples = np.array(audio, dtype=np.float32)
        return [AudioChunk(samples=samples, sample_rate=KITTEN_SAMPLE_RATE, is_last=True)]

    async def generate_stream(self, text: str, voice: str | None = None, speed: float = 1.0):
        """KittenTTS has no streaming — yield single chunk after full generation."""
        chunks = self.generate(text, voice=voice, speed=speed)
        for chunk in chunks:
            yield chunk

    def get_voices(self) -> list[dict]:
        return KITTEN_VOICES

    def set_voice(self, voice_id: str) -> None:
        self._voice = voice_id

    def stop(self) -> None:
        self._stopped = True
```

---

## audio_player.py

Plays audio via `sounddevice`, computes RMS amplitude in real-time, and calls amplitude callback at ~30Hz.

```python
"""
Audio player with real-time RMS amplitude computation.

Plays PCM audio via sounddevice. During playback, computes amplitude
using RMS (Root Mean Square) with EMA (Exponential Moving Average)
smoothing. Broadcasts amplitude at ~30Hz for avatar lip sync.

Amplitude pipeline:
  PCM samples -> RMS per frame -> EMA smoothing -> normalize 0-1 -> callback
"""

from __future__ import annotations

import asyncio
import threading
from typing import Callable, Awaitable

import numpy as np
import sounddevice as sd


# Amplitude broadcast rate (~30Hz = every 33ms)
AMPLITUDE_INTERVAL_MS = 33
# EMA smoothing factor (0.3 = responsive but smooth)
EMA_ALPHA = 0.3
# RMS normalization ceiling (empirical — most speech RMS peaks around 0.3)
RMS_CEILING = 0.3


class AudioPlayer:
    def __init__(self) -> None:
        self._stop_event = threading.Event()
        self._amplitude: float = 0.0
        self._lock = threading.Lock()

    def stop(self) -> None:
        """Stop current playback."""
        self._stop_event.set()
        sd.stop()

    async def play_chunks(
        self,
        chunks: list["AudioChunk"],
        on_amplitude: Callable[[float], Awaitable[None]],
    ) -> None:
        """
        Play audio chunks sequentially. Compute and broadcast amplitude.

        Args:
            chunks: List of AudioChunk (samples: np.ndarray float32, sample_rate: int)
            on_amplitude: Async callback receiving normalized 0-1 amplitude at ~30Hz
        """
        self._stop_event.clear()
        self._amplitude = 0.0

        for chunk in chunks:
            if self._stop_event.is_set():
                break
            await self._play_one(chunk.samples, chunk.sample_rate, on_amplitude)

        # Reset amplitude to 0 when done
        await on_amplitude(0.0)

    async def _play_one(
        self,
        samples: np.ndarray,
        sample_rate: int,
        on_amplitude: Callable[[float], Awaitable[None]],
    ) -> None:
        """Play a single audio buffer, emitting amplitude during playback."""
        frame_size = int(sample_rate * AMPLITUDE_INTERVAL_MS / 1000)  # ~792 samples at 24kHz
        total_frames = len(samples)

        # Start non-blocking playback
        sd.play(samples, samplerate=sample_rate)

        # Emit amplitude by walking through the buffer in frame_size steps
        offset = 0
        smoothed = 0.0

        while offset < total_frames and not self._stop_event.is_set():
            end = min(offset + frame_size, total_frames)
            frame = samples[offset:end]

            # RMS amplitude
            rms = float(np.sqrt(np.mean(frame ** 2)))

            # EMA smoothing
            smoothed = EMA_ALPHA * rms + (1.0 - EMA_ALPHA) * smoothed

            # Normalize to 0-1
            normalized = min(smoothed / RMS_CEILING, 1.0)

            await on_amplitude(normalized)
            await asyncio.sleep(AMPLITUDE_INTERVAL_MS / 1000)

            offset = end

        # Wait for sounddevice to finish
        sd.wait()
```

---

## pipeline.py

Orchestrates text-to-audio generation: engine generates, player plays, callbacks broadcast.

```python
"""
TTS Pipeline — orchestrates engine generation + audio playback + broadcasting.

Flow: text -> engine.generate() -> audio_player.play_chunks() -> amplitude/audio callbacks
"""

from __future__ import annotations

import asyncio
import base64
from typing import Callable, Awaitable

import numpy as np

from vibe_tts.audio_player import AudioPlayer
from vibe_tts.engine_registry import EngineRegistry


class TTSPipeline:
    def __init__(
        self,
        registry: EngineRegistry,
        audio_player: AudioPlayer,
        on_amplitude: Callable[[float], Awaitable[None]],
        on_audio_chunk: Callable[[str, int, bool], Awaitable[None]],
    ) -> None:
        """
        Args:
            registry: Engine registry to get active engine
            audio_player: Handles playback + amplitude
            on_amplitude: Called with normalized 0-1 amplitude at ~30Hz
            on_audio_chunk: Called with (base64_data, sample_rate, is_last) for /ws/audio
        """
        self._registry = registry
        self._player = audio_player
        self._on_amplitude = on_amplitude
        self._on_audio_chunk = on_audio_chunk

    async def speak(self, text: str, voice: str | None = None, speed: float | None = None) -> None:
        """
        Full speak pipeline:
          1. Generate audio via active engine
          2. Broadcast audio chunks via /ws/audio
          3. Play audio locally (with amplitude broadcasting via /ws/status)
        """
        engine = self._registry.get_active()
        if engine is None:
            return

        effective_speed = speed if speed is not None else 1.0
        chunks = engine.generate(text, voice=voice, speed=effective_speed)

        if not chunks:
            return

        # Broadcast audio chunks to /ws/audio clients
        for chunk in chunks:
            pcm_int16 = (chunk.samples * 32767).astype(np.int16)
            data_b64 = base64.b64encode(pcm_int16.tobytes()).decode("ascii")
            await self._on_audio_chunk(data_b64, chunk.sample_rate, chunk.is_last)

        # Play locally with amplitude broadcasting
        await self._player.play_chunks(chunks, self._on_amplitude)
```

---

## state_manager.py

In-memory mirror of the TypeScript `StateManager` + `FeelingEngine` + `ExpressionTrigger` from `packages/core/src/state/`. When `POST /api/state` arrives, applies adjustments, recalculates feelings, checks expression thresholds, and returns the full `StateResponse`.

```python
"""
State Manager — Python mirror of the TypeScript state system.

Mirrors three classes from packages/core/src/state/:
  - StateManager (internal-states.ts): 6 epistemic states, 0-100, baseline 50
  - FeelingEngine (feeling-engine.ts): derives 14 feelings from states
  - ExpressionTrigger (expression-trigger.ts): fires expressions on threshold crossings

Returns StateResponse matching protocol.ts:
  { states: {...}, feelings: {...}, expressionsTriggered: [...] }
"""

from __future__ import annotations

import math
import time
from typing import Any


# ─── Constants (mirrors shared/constants.ts) ──────────────────

STATE_NAMES = [
    "confidence", "contextSaturation", "alignment",
    "memoryPressure", "momentum", "trustCalibration",
]

FEELING_NAMES = [
    "happy", "sad", "frustrated", "curious", "proud",
    "anxious", "excited", "calm", "bored", "guilty",
    "angry", "blushing", "surprised", "relieved",
]

STATE_BASELINE = 50

# ─── Expression thresholds (mirrors expression-trigger.ts) ────

EXPRESSION_THRESHOLDS = [
    {"expression": "celebrate",   "feeling": "happy",      "threshold": 80,  "cooldown_ms": 60_000},
    {"expression": "cry",         "feeling": "sad",        "threshold": 75,  "cooldown_ms": 120_000},
    {"expression": "sigh",        "feeling": "frustrated", "threshold": 60,  "cooldown_ms": 30_000},
    {"expression": "head-tilt",   "feeling": "curious",    "threshold": 50,  "cooldown_ms": 15_000},
    {"expression": "fist-pump",   "feeling": "proud",      "threshold": 70,  "cooldown_ms": 60_000},
    {"expression": "tremble",     "feeling": "anxious",    "threshold": 70,  "cooldown_ms": 45_000},
    {"expression": "bounce",      "feeling": "excited",    "threshold": 65,  "cooldown_ms": 30_000},
    {"expression": "nod",         "feeling": "calm",       "threshold": 60,  "cooldown_ms": 20_000},
    {"expression": "yawn",        "feeling": "bored",      "threshold": 70,  "cooldown_ms": 90_000},
    {"expression": "facepalm",    "feeling": "guilty",     "threshold": 60,  "cooldown_ms": 60_000},
    {"expression": "puff-cheeks", "feeling": "angry",      "threshold": 65,  "cooldown_ms": 45_000},
    {"expression": "cover-face",  "feeling": "blushing",   "threshold": 50,  "cooldown_ms": 30_000},
    {"expression": "gasp",        "feeling": "surprised",  "threshold": 60,  "cooldown_ms": 15_000},
]


def _clamp(value: float) -> int:
    """Clamp to 0-100 integer."""
    return max(0, min(100, round(value)))


class StateManager:
    """
    Combined state + feeling + expression trigger system.
    Single class because the Python server is stateless between restarts —
    no need for the same granular separation as the TypeScript core.
    """

    def __init__(self) -> None:
        # Internal states — all start at baseline 50
        self.states: dict[str, int] = {name: STATE_BASELINE for name in STATE_NAMES}
        # Previous feelings for expression threshold crossing detection
        self._prev_feelings: dict[str, int] | None = None
        # Previous contextSaturation for surprised calculation
        self._prev_ctx_sat: int | None = None
        # Cooldown tracking: expression name -> last fired timestamp (ms)
        self._last_fired: dict[str, float] = {}

    def adjust(self, adjustments: list[tuple[str, float]]) -> dict[str, Any]:
        """
        Apply state adjustments, recalculate feelings, check expression thresholds.

        Args:
            adjustments: List of (state_name, delta) tuples

        Returns:
            StateResponse dict: { states, feelings, expressionsTriggered }
        """
        # 1. Apply deltas
        for state_name, delta in adjustments:
            if state_name in self.states:
                current = self.states[state_name]
                self.states[state_name] = max(0, min(100, round(current + delta)))

        # 2. Recalculate feelings
        feelings = self._recalculate_feelings()

        # 3. Check expression thresholds
        triggered = self._check_expressions(feelings)

        # 4. Update previous feelings for next call
        self._prev_ctx_sat = self.states["contextSaturation"]
        self._prev_feelings = dict(feelings)

        return {
            "states": dict(self.states),
            "feelings": feelings,
            "expressionsTriggered": triggered,
        }

    # ─── FeelingEngine mirror ─────────────────────────────────

    def _recalculate_feelings(self) -> dict[str, int]:
        """Mirror of FeelingEngine.recalculate() from feeling-engine.ts."""
        s = self.states
        conf = s["confidence"]
        ctx = s["contextSaturation"]
        align = s["alignment"]
        mem = s["memoryPressure"]
        mom = s["momentum"]
        trust = s["trustCalibration"]

        feelings: dict[str, int] = {}

        # happy: confidence * 0.4 + momentum * 0.3 + alignment * 0.3
        feelings["happy"] = _clamp(conf * 0.4 + mom * 0.3 + align * 0.3)

        # sad: 100 - (momentum * 0.5 + alignment * 0.5)
        feelings["sad"] = _clamp(100 - (mom * 0.5 + align * 0.5))

        # frustrated: only when momentum < 30
        if mom >= 30:
            feelings["frustrated"] = 0
        else:
            feelings["frustrated"] = _clamp(conf * 0.3 + (100 - mom) * 0.7)

        # curious: (100 - contextSaturation) * 0.6 + (100 - confidence) * 0.4
        feelings["curious"] = _clamp((100 - ctx) * 0.6 + (100 - conf) * 0.4)

        # proud: only when confidence > 70
        if conf <= 70:
            feelings["proud"] = 0
        else:
            feelings["proud"] = _clamp(conf * 0.4 + align * 0.4 + mom * 0.2)

        # anxious: (100 - confidence) * 0.5 + (100 - trustCalibration) * 0.5
        feelings["anxious"] = _clamp((100 - conf) * 0.5 + (100 - trust) * 0.5)

        # excited: only when momentum > 60
        if mom <= 60:
            feelings["excited"] = 0
        else:
            feelings["excited"] = _clamp(mom * 0.5 + (100 - ctx) * 0.5)

        # calm: low variance across all states (equilibrium)
        values = list(s.values())
        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        feelings["calm"] = _clamp(100 - (variance / 25))

        # bored: only when contextSaturation > 70
        if ctx <= 70:
            feelings["bored"] = 0
        else:
            feelings["bored"] = _clamp(ctx * 0.6 + (100 - mom) * 0.4)

        # guilty: only when alignment < 30
        if align >= 30:
            feelings["guilty"] = 0
        else:
            feelings["guilty"] = _clamp((100 - align) * 0.6 + trust * 0.4)

        # angry: only when alignment < 20
        if align >= 20:
            feelings["angry"] = 0
        else:
            feelings["angry"] = _clamp((100 - align) * 0.5 + mom * 0.5)

        # blushing: baseline from trustCalibration
        feelings["blushing"] = _clamp(trust * 0.3)

        # surprised: sudden contextSaturation drop (> 15 points)
        if self._prev_ctx_sat is None:
            feelings["surprised"] = 0
        else:
            delta = self._prev_ctx_sat - ctx
            feelings["surprised"] = _clamp(delta * 2) if delta > 15 else 0

        # relieved: placeholder (formula not yet defined in TypeScript)
        feelings["relieved"] = 0

        return feelings

    # ─── ExpressionTrigger mirror ─────────────────────────────

    def _check_expressions(self, feelings: dict[str, int]) -> list[str]:
        """Mirror of ExpressionTrigger.check() from expression-trigger.ts."""
        now = time.time() * 1000  # ms
        triggered: list[str] = []

        for rule in EXPRESSION_THRESHOLDS:
            current = feelings.get(rule["feeling"], 0)
            previous = (self._prev_feelings or {}).get(rule["feeling"], 0)

            # Must cross threshold upward
            if current <= rule["threshold"]:
                continue
            if previous > rule["threshold"]:
                continue

            # Check cooldown
            last = self._last_fired.get(rule["expression"], 0)
            if now - last < rule["cooldown_ms"]:
                continue

            # Fire
            self._last_fired[rule["expression"]] = now
            triggered.append(rule["expression"])

        return triggered
```

---

## setup.sh

```bash
#!/bin/bash
# Create Python venv and install vibe-tts in editable mode.
# Usage: cd apps/tts-server && bash setup.sh [--kokoro] [--kitten]

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "Creating venv..."
python3 -m venv .venv
source .venv/bin/activate

echo "Installing vibe-tts..."
pip install -e .

# Install optional engine deps based on flags
if [[ "$*" == *"--kokoro"* ]]; then
    echo "Installing Kokoro dependencies (PyTorch + misaki)..."
    pip install -e ".[kokoro]"
fi

if [[ "$*" == *"--kitten"* ]]; then
    echo "Installing KittenTTS dependencies..."
    pip install -e ".[kitten]"
fi

echo ""
echo "Done. Start the server with:"
echo "  source .venv/bin/activate"
echo "  python -m uvicorn vibe_tts.server:app --host 0.0.0.0 --port 5111"
```

---

## Dockerfile

Multi-stage build. Python 3.12-slim base. Installs core deps first (cached layer), then app code.

```dockerfile
# ─── Stage 1: Dependencies ──────────────────────────────────
FROM python:3.12-slim AS deps

WORKDIR /app

# System deps for sounddevice (PortAudio)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libportaudio2 \
        libsndfile1 && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# ─── Stage 2: Application ───────────────────────────────────
FROM deps AS app

COPY src/ ./src/
RUN pip install --no-cache-dir -e .

# Default: install KittenTTS (lightest engine)
RUN pip install --no-cache-dir kittentts

EXPOSE 5111

# Health check
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5111/api/health')"

CMD ["python", "-m", "uvicorn", "vibe_tts.server:app", "--host", "0.0.0.0", "--port", "5111"]
```

---

## docker-compose.yml

```yaml
services:
  tts-server:
    build: .
    ports:
      - "5111:5111"
    volumes:
      - kokoro-models:/app/models    # Cached model weights persist across rebuilds
    environment:
      - PYTORCH_ENABLE_MPS_FALLBACK=1
    # Uncomment for NVIDIA GPU passthrough:
    # deploy:
    #   resources:
    #     reservations:
    #       devices:
    #         - driver: nvidia
    #           capabilities: [gpu]

volumes:
  kokoro-models:
```

---

## Verification

After setup, these commands should work:

```bash
# Start the server
cd apps/tts-server
source .venv/bin/activate
python -m uvicorn vibe_tts.server:app --port 5111

# In another terminal:

# Health check
curl localhost:5111/api/health
# -> {"status":"ok","engine":"kitten","uptime":5}

# List voices
curl localhost:5111/api/voices
# -> {"voices":[{"id":"Bella","name":"Bella",...}, ...]}

# Speak (generates audio, streams amplitude via WebSocket)
curl -X POST localhost:5111/api/speak \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello from Vibe TTS"}'
# -> {"status":"ok"}

# Set feeling (broadcasts to WebSocket clients)
curl -X POST localhost:5111/api/feeling \
  -H "Content-Type: application/json" \
  -d '{"name":"happy"}'
# -> {"status":"ok"}

# Adjust state (returns full state + feelings + triggered expressions)
curl -X POST localhost:5111/api/state \
  -H "Content-Type: application/json" \
  -d '{"adjustments":[{"state":"confidence","delta":15}]}'
# -> {"states":{...},"feelings":{...},"expressionsTriggered":[...]}
```

---

## Key Design Decisions

**Why FastAPI, not Flask/Django?**
Async by default. Native WebSocket support. Auto-generates OpenAPI docs. Lightweight. The TTS server needs concurrent HTTP + WebSocket -- FastAPI handles this naturally with asyncio.

**Why server-side playback + amplitude?**
The TTS server plays audio locally (via sounddevice) and computes amplitude from the PCM data. The avatar app receives amplitude over WebSocket. This means the avatar app never touches audio data directly -- it just receives a 0-1 float at 30Hz for lip sync. Simpler client, single source of truth for amplitude.

**Why mirror the TypeScript state system in Python?**
The TTS server is the single source of truth for entity state. CLI commands and hooks POST to the server, not the desktop app. The Python `StateManager` mirrors the TypeScript `FeelingEngine` + `ExpressionTrigger` exactly so behavior is consistent. If the formulas change in TypeScript, they must be updated here too.

**Why try-import for engines?**
Not all users install all engines. `pip install -e .` gives you the server. `pip install -e ".[kokoro]"` adds Kokoro. The registry skips engines whose dependencies aren't installed, so the server always starts.
