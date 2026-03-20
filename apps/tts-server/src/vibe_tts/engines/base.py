"""
TTSEngineBase — abstract base class for TTS engines.

Python mirror of ITTSEngine from packages/core/src/interfaces/tts-engine.ts.
All engines: Text in -> Audio out (numpy float32 arrays at a given sample rate).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import AsyncIterator

import numpy as np


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
    samples: np.ndarray  # float32, mono
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
