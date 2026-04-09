"""
TTS Pipeline — orchestrates engine generation + audio playback + broadcasting.

Flow: text -> split sentences -> per-sentence: engine.generate() -> broadcast audio chunk
"""

from __future__ import annotations

import base64
import re
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
            # Split long sentences at commas
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


class TTSPipeline:
    def __init__(
        self,
        registry: EngineRegistry,
        on_audio_chunk: Callable[[str, int, bool, str | None], Awaitable[None]],
    ) -> None:
        self._registry = registry
        self._on_audio_chunk = on_audio_chunk

    async def speak(self, text: str, voice: str | None = None, speed: float | None = None) -> None:
        """Split text into sentences, generate and broadcast audio per sentence."""
        engine = self._registry.get_active()
        if engine is None:
            return

        effective_speed = speed if speed is not None else 1.0
        sentences = split_sentences(text)
        if not sentences:
            return

        for i, sentence in enumerate(sentences):
            is_last_sentence = (i == len(sentences) - 1)

            chunks = engine.generate(sentence, voice=voice, speed=effective_speed)
            if not chunks:
                continue

            for j, chunk in enumerate(chunks):
                is_last_chunk = is_last_sentence and (j == len(chunks) - 1)
                # Attach sentence text to the first chunk of each sentence
                text_label = sentence if j == 0 else None
                pcm_int16 = (chunk.samples * 32767).astype(np.int16)
                data_b64 = base64.b64encode(pcm_int16.tobytes()).decode("ascii")
                await self._on_audio_chunk(data_b64, chunk.sample_rate, is_last_chunk, text_label)
