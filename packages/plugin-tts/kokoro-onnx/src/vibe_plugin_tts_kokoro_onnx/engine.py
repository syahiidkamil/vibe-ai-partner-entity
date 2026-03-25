"""
Kokoro ONNX Engine — lightweight ONNX runtime, CPU-friendly, ~300MB model.

Auto-downloads model files from GitHub releases on first init.
"""

from __future__ import annotations

import os
import urllib.request
from pathlib import Path

import numpy as np

from vibe_plugin_tts_core import AudioChunk, TTSEngineBase

MODEL_REPO = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0"
MODEL_FILE = "kokoro-v1.0.onnx"
VOICES_FILE = "voices-v1.0.bin"

KOKORO_ONNX_VOICES = [
    {"id": "af_heart",   "name": "Heart (Female)",    "language": "en-us", "gender": "female"},
    {"id": "af_bella",   "name": "Bella (Female)",    "language": "en-us", "gender": "female"},
    {"id": "am_adam",    "name": "Adam (Male)",        "language": "en-us", "gender": "male"},
    {"id": "am_michael", "name": "Michael (Male)",     "language": "en-us", "gender": "male"},
    {"id": "bf_emma",    "name": "Emma (British F)",   "language": "en-gb", "gender": "female"},
    {"id": "bm_george",  "name": "George (British M)", "language": "en-gb", "gender": "male"},
]

MAX_CHARS = 500


def _cache_dir() -> Path:
    d = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "kokoro-onnx"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _download_if_missing(filename: str) -> str:
    path = _cache_dir() / filename
    if path.exists():
        return str(path)
    url = f"{MODEL_REPO}/{filename}"
    print(f"  Downloading {filename}...")
    urllib.request.urlretrieve(url, path)
    print(f"  Downloaded {filename} ({path.stat().st_size / 1024 / 1024:.1f}MB)")
    return str(path)


class KokoroOnnxEngine(TTSEngineBase):
    name = "kokoro-onnx"

    def __init__(self) -> None:
        self._kokoro = None
        self._voice: str = "af_heart"
        self._stopped = False

    def initialize(self) -> None:
        from kokoro_onnx import Kokoro

        model_path = _download_if_missing(MODEL_FILE)
        voices_path = _download_if_missing(VOICES_FILE)
        self._kokoro = Kokoro(model_path, voices_path)

    def generate(self, text: str, voice: str | None = None, speed: float = 1.0) -> list[AudioChunk]:
        if self._kokoro is None:
            raise RuntimeError("KokoroOnnxEngine not initialized")

        voice = voice or self._voice
        self._stopped = False

        if len(text) > MAX_CHARS:
            text = text[:MAX_CHARS].rsplit(" ", 1)[0]

        audio, sr = self._kokoro.create(text, voice=voice, speed=speed)

        if self._stopped:
            return []

        samples = np.array(audio, dtype=np.float32)
        return [AudioChunk(samples=samples, sample_rate=sr, is_last=True)]

    async def generate_stream(self, text: str, voice: str | None = None, speed: float = 1.0):
        if self._kokoro is None:
            raise RuntimeError("KokoroOnnxEngine not initialized")

        voice = voice or self._voice
        self._stopped = False

        if len(text) > MAX_CHARS:
            text = text[:MAX_CHARS].rsplit(" ", 1)[0]

        async for audio, sr in self._kokoro.create_stream(text, voice=voice, speed=speed):
            if self._stopped:
                break
            samples = np.array(audio, dtype=np.float32)
            yield AudioChunk(samples=samples, sample_rate=sr, is_last=False)

    def get_voices(self) -> list[dict]:
        return KOKORO_ONNX_VOICES

    def set_voice(self, voice_id: str) -> None:
        self._voice = voice_id

    def stop(self) -> None:
        self._stopped = True
