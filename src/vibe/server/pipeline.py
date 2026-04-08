"""
TTS Pipeline — orchestrates engine generation + audio playback + broadcasting.

Flow: text -> engine.generate() -> audio_player.play_chunks() -> amplitude/audio callbacks
"""

from __future__ import annotations

import base64
from typing import Callable, Awaitable

import numpy as np

from vibe.server.audio_player import AudioPlayer
from vibe.server.engine_registry import EngineRegistry


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
