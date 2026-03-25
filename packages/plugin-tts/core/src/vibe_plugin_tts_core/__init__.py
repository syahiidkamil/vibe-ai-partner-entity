"""Shared base types for Vibe TTS engine plugins."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import AsyncIterator

import numpy as np


@dataclass
class VoiceInfo:
    """Metadata about an available voice."""
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
        """Generate full audio from text."""
        ...

    @abstractmethod
    async def generate_stream(self, text: str, voice: str | None = None, speed: float = 1.0) -> AsyncIterator[AudioChunk]:
        """Yield audio chunks as they are generated."""
        ...

    @abstractmethod
    def get_voices(self) -> list[dict]:
        """Return list of available voices."""
        ...

    @abstractmethod
    def set_voice(self, voice_id: str) -> None:
        """Set the active voice."""
        ...

    @abstractmethod
    def stop(self) -> None:
        """Abort current generation immediately."""
        ...
