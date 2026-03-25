"""
KittenTTS Engine — lightweight model, CPU-only, 8 voices.

Uses KittenML/kitten-tts-nano-0.8-int8 (25MB, ONNX).
Auto-downloads from HuggingFace on first run.
"""

from __future__ import annotations

import numpy as np
from kittentts import KittenTTS as KittenModel

from vibe_plugin_tts_core import AudioChunk, TTSEngineBase

KITTEN_MODEL = "KittenML/kitten-tts-nano-0.8-int8"

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
        if self._model is None:
            self._model = KittenModel(KITTEN_MODEL)

    def generate(self, text: str, voice: str | None = None, speed: float = 1.0) -> list[AudioChunk]:
        if self._model is None:
            raise RuntimeError("KittenEngine not initialized")

        voice = voice or self._voice
        self._stopped = False

        audio = self._model.generate(text, voice=voice)

        if self._stopped:
            return []

        samples = np.array(audio, dtype=np.float32)
        return [AudioChunk(samples=samples, sample_rate=KITTEN_SAMPLE_RATE, is_last=True)]

    async def generate_stream(self, text: str, voice: str | None = None, speed: float = 1.0):
        chunks = self.generate(text, voice=voice, speed=speed)
        for chunk in chunks:
            yield chunk

    def get_voices(self) -> list[dict]:
        return KITTEN_VOICES

    def set_voice(self, voice_id: str) -> None:
        self._voice = voice_id

    def stop(self) -> None:
        self._stopped = True
