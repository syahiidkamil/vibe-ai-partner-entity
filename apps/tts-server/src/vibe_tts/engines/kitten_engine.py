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
