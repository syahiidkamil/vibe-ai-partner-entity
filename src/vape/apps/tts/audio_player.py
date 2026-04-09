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

from vape.core import AudioChunk


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
        chunks: list[AudioChunk],
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
