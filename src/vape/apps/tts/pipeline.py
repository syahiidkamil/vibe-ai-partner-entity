"""
TTS Pipeline — orchestrates engine generation + audio delivery.

Flow: text -> split sentences -> per-sentence: engine.generate() -> save WAV -> broadcast path
"""

from __future__ import annotations

import re
import tempfile
import wave
from typing import Callable, Awaitable

import numpy as np

from vape.apps.tts.registry import EngineRegistry


def split_sentences(text: str, max_chars: int = 200) -> list[str]:
    """Split text into sentences, further breaking long ones at commas."""
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    result = []
    for s in sentences:
        s = s.strip()
        if not s:
            continue
        if len(s) <= max_chars:
            result.append(s)
        else:
            parts = re.split(r',\s*', s)
            buf = ""
            for part in parts:
                if buf and len(buf) + len(part) + 2 > max_chars:
                    result.append(buf.strip())
                    buf = part
                else:
                    buf = f"{buf}, {part}" if buf else part
            if buf.strip():
                result.append(buf.strip())
    return result


def _save_wav(samples: np.ndarray, sample_rate: int) -> str:
    """Save float32 samples to a temp WAV file. Returns file path."""
    pcm_int16 = (samples * 32767).astype(np.int16)
    f = tempfile.NamedTemporaryFile(suffix=".wav", prefix="tts-", delete=False)
    with wave.open(f, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm_int16.tobytes())
    return f.name


class TTSPipeline:
    def __init__(
        self,
        registry: EngineRegistry,
        on_audio: Callable[[str, str, bool], Awaitable[None]],
    ) -> None:
        """
        Args:
            registry: Engine registry
            on_audio: Called with (wav_path, sentence_text, is_last)
        """
        self._registry = registry
        self._on_audio = on_audio

    async def speak(self, text: str, voice: str | None = None, speed: float | None = None) -> None:
        """Split text into sentences, generate audio per sentence, broadcast file paths."""
        engine = self._registry.get_active()
        if engine is None:
            return

        effective_speed = speed if speed is not None else 1.0
        sentences = split_sentences(text)
        if not sentences:
            return

        for i, sentence in enumerate(sentences):
            is_last = (i == len(sentences) - 1)

            chunks = engine.generate(sentence, voice=voice, speed=effective_speed)
            if not chunks:
                continue

            # Concatenate all chunks for this sentence into one WAV
            all_samples = np.concatenate([c.samples for c in chunks])
            sample_rate = chunks[0].sample_rate
            wav_path = _save_wav(all_samples, sample_rate)

            await self._on_audio(wav_path, sentence, is_last)
