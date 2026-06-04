"""
TTS Pipeline — orchestrates engine generation + audio delivery.

Flow: text -> split sentences -> per-sentence: engine.generate() -> save WAV -> broadcast path
"""

from __future__ import annotations

import asyncio
import re
import tempfile
import wave
from typing import Callable, Awaitable

import numpy as np

from engine.apps.tts.registry import EngineRegistry


def split_sentences(text: str, max_chars: int = 300) -> list[str]:
    """Split text into bubble-sized pieces, BEFORE the TTS engine, so each piece
    becomes its own audio clip + caption and the voice always matches the text on
    screen (no renderer-side re-paging that drifts out of sync).

    Short sentences are kept whole — one sentence, one bubble. Only a sentence
    longer than ``max_chars`` is broken, first at clause boundaries (commas,
    semicolons, colons — punctuation preserved), then by words as a last resort
    for a long comma-less run. ``max_chars`` ≈ what fits the 3-line bubble at the
    default avatar size; lower it if captions still wrap past the clamp.
    """
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    result: list[str] = []
    for s in sentences:
        s = s.strip()
        if not s:
            continue
        if len(s) <= max_chars:
            result.append(s)
        else:
            # Split AFTER clause punctuation so the comma/semicolon stays attached.
            result.extend(_pack(re.split(r'(?<=[,;:])\s+', s), max_chars))
    return result


def _pack(parts: list[str], max_chars: int) -> list[str]:
    """Greedily pack parts into <= max_chars pieces; a single part longer than
    max_chars (a comma-less run) is itself packed by words."""
    out: list[str] = []
    buf = ""
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if len(part) > max_chars:
            if buf:
                out.append(buf)
                buf = ""
            out.extend(_pack_words(part, max_chars))
            continue
        if buf and len(buf) + 1 + len(part) > max_chars:
            out.append(buf)
            buf = part
        else:
            buf = f"{buf} {part}" if buf else part
    if buf:
        out.append(buf)
    return out


def _pack_words(s: str, max_chars: int) -> list[str]:
    """Pack words into EVENLY-sized pieces (each <= max_chars), so a long
    comma-less run splits into balanced chunks instead of leaving a tiny orphan
    bubble (e.g. a lone "together,")."""
    n = max(1, -(-len(s) // max_chars))   # chunks needed (ceil div)
    target = -(-len(s) // n)              # even target per chunk, <= max_chars
    out: list[str] = []
    buf = ""
    for w in s.split():
        if buf and len(buf) + 1 + len(w) > target and len(out) < n - 1:
            out.append(buf)
            buf = w
        else:
            buf = f"{buf} {w}" if buf else w
    if buf:
        out.append(buf)
    return out


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

            # Run CPU-bound generation in thread to avoid blocking the event loop
            def _generate_and_save():
                chunks = engine.generate(sentence, voice=voice, speed=effective_speed)
                if not chunks:
                    return None
                all_samples = np.concatenate([c.samples for c in chunks])
                return _save_wav(all_samples, chunks[0].sample_rate)

            wav_path = await asyncio.to_thread(_generate_and_save)
            if not wav_path:
                continue

            await self._on_audio(wav_path, sentence, is_last)
