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
    {"id": "af_heart",   "name": "Heart (Female)",    "language": "en-us", "gender": "female"},
    {"id": "af_bella",   "name": "Bella (Female)",    "language": "en-us", "gender": "female"},
    {"id": "am_adam",    "name": "Adam (Male)",        "language": "en-us", "gender": "male"},
    {"id": "am_michael", "name": "Michael (Male)",     "language": "en-us", "gender": "male"},
    {"id": "bf_emma",    "name": "Emma (British F)",   "language": "en-gb", "gender": "female"},
    {"id": "bm_george",  "name": "George (British M)", "language": "en-gb", "gender": "male"},
    {"id": "jf_alpha",   "name": "Alpha (Japanese F)", "language": "ja",    "gender": "female"},
    {"id": "jm_beta",    "name": "Beta (Japanese M)",  "language": "ja",    "gender": "male"},
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
