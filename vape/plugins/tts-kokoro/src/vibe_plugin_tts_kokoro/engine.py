"""
Kokoro TTS Engine — full PyTorch model via KPipeline.

Multi-voice (52 voices), multi-language (9 languages), streaming per-sentence.
"""

from __future__ import annotations

import threading

import numpy as np
from kokoro import KPipeline

from engine.core import AudioChunk, TTSEngineBase

VOICE_LANG_MAP: dict[str, str] = {
    "a": "a", "b": "b", "e": "e", "f": "f",
    "h": "h", "i": "i", "j": "j", "p": "p", "z": "z",
}

KOKORO_VOICES = [
    # American English — Female
    {"id": "af_heart",   "name": "Heart",    "language": "en-us", "gender": "female"},
    {"id": "af_alloy",   "name": "Alloy",    "language": "en-us", "gender": "female"},
    {"id": "af_aoede",   "name": "Aoede",    "language": "en-us", "gender": "female"},
    {"id": "af_bella",   "name": "Bella",    "language": "en-us", "gender": "female"},
    {"id": "af_jessica", "name": "Jessica",  "language": "en-us", "gender": "female"},
    {"id": "af_kore",    "name": "Kore",     "language": "en-us", "gender": "female"},
    {"id": "af_nicole",  "name": "Nicole",   "language": "en-us", "gender": "female"},
    {"id": "af_nova",    "name": "Nova",     "language": "en-us", "gender": "female"},
    {"id": "af_river",   "name": "River",    "language": "en-us", "gender": "female"},
    {"id": "af_sarah",   "name": "Sarah",    "language": "en-us", "gender": "female"},
    {"id": "af_sky",     "name": "Sky",      "language": "en-us", "gender": "female"},
    # American English — Male
    {"id": "am_adam",    "name": "Adam",     "language": "en-us", "gender": "male"},
    {"id": "am_echo",    "name": "Echo",     "language": "en-us", "gender": "male"},
    {"id": "am_eric",    "name": "Eric",     "language": "en-us", "gender": "male"},
    {"id": "am_fenrir",  "name": "Fenrir",   "language": "en-us", "gender": "male"},
    {"id": "am_liam",    "name": "Liam",     "language": "en-us", "gender": "male"},
    {"id": "am_michael", "name": "Michael",  "language": "en-us", "gender": "male"},
    {"id": "am_onyx",    "name": "Onyx",     "language": "en-us", "gender": "male"},
    {"id": "am_puck",    "name": "Puck",     "language": "en-us", "gender": "male"},
    {"id": "am_santa",   "name": "Santa",    "language": "en-us", "gender": "male"},
    # British English — Female
    {"id": "bf_alice",    "name": "Alice",    "language": "en-gb", "gender": "female"},
    {"id": "bf_emma",     "name": "Emma",     "language": "en-gb", "gender": "female"},
    {"id": "bf_isabella", "name": "Isabella", "language": "en-gb", "gender": "female"},
    {"id": "bf_lily",     "name": "Lily",     "language": "en-gb", "gender": "female"},
    # British English — Male
    {"id": "bm_daniel",  "name": "Daniel",   "language": "en-gb", "gender": "male"},
    {"id": "bm_fable",   "name": "Fable",    "language": "en-gb", "gender": "male"},
    {"id": "bm_george",  "name": "George",   "language": "en-gb", "gender": "male"},
    {"id": "bm_lewis",   "name": "Lewis",    "language": "en-gb", "gender": "male"},
    # Japanese
    {"id": "jf_alpha",      "name": "Alpha",      "language": "ja", "gender": "female"},
    {"id": "jf_gongitsune", "name": "Gongitsune", "language": "ja", "gender": "female"},
    {"id": "jf_nezumi",     "name": "Nezumi",     "language": "ja", "gender": "female"},
    {"id": "jf_tebukuro",   "name": "Tebukuro",   "language": "ja", "gender": "female"},
    {"id": "jm_kumo",       "name": "Kumo",       "language": "ja", "gender": "male"},
    # Mandarin Chinese
    {"id": "zf_xiaobei",  "name": "Xiaobei",  "language": "zh", "gender": "female"},
    {"id": "zf_xiaoni",   "name": "Xiaoni",   "language": "zh", "gender": "female"},
    {"id": "zf_xiaoxiao", "name": "Xiaoxiao", "language": "zh", "gender": "female"},
    {"id": "zf_xiaoyi",   "name": "Xiaoyi",   "language": "zh", "gender": "female"},
    {"id": "zm_yunjian",  "name": "Yunjian",  "language": "zh", "gender": "male"},
    {"id": "zm_yunxi",    "name": "Yunxi",     "language": "zh", "gender": "male"},
    {"id": "zm_yunxia",   "name": "Yunxia",    "language": "zh", "gender": "male"},
    {"id": "zm_yunyang",  "name": "Yunyang",   "language": "zh", "gender": "male"},
    # Spanish
    {"id": "ef_dora",   "name": "Dora",   "language": "es", "gender": "female"},
    {"id": "em_alex",   "name": "Alex",   "language": "es", "gender": "male"},
    {"id": "em_santa",  "name": "Santa",  "language": "es", "gender": "male"},
    # French
    {"id": "ff_siwis",  "name": "Siwis",  "language": "fr", "gender": "female"},
    # Hindi
    {"id": "hf_alpha",  "name": "Alpha",  "language": "hi", "gender": "female"},
    {"id": "hf_beta",   "name": "Beta",   "language": "hi", "gender": "female"},
    {"id": "hm_omega",  "name": "Omega",  "language": "hi", "gender": "male"},
    {"id": "hm_psi",    "name": "Psi",    "language": "hi", "gender": "male"},
    # Italian
    {"id": "if_sara",   "name": "Sara",   "language": "it", "gender": "female"},
    {"id": "im_nicola", "name": "Nicola", "language": "it", "gender": "male"},
    # Brazilian Portuguese
    {"id": "pf_dora",   "name": "Dora",   "language": "pt-br", "gender": "female"},
    {"id": "pm_alex",   "name": "Alex",   "language": "pt-br", "gender": "male"},
    {"id": "pm_santa",  "name": "Santa",  "language": "pt-br", "gender": "male"},
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
        self._get_pipeline(self._lang_code_from_voice(self._voice))
        self._warmup()

    def _warmup(self) -> None:
        # First generate() pays for PyTorch graph compile and any per-voice
        # asset loading. Pay it once at startup so the user's first speak
        # is not delayed.
        try:
            self.generate(".", voice=self._voice, speed=1.0)
        except Exception:
            pass

    def _get_pipeline(self, lang_code: str) -> KPipeline:
        with self._pipelines_lock:
            if lang_code not in self._pipelines:
                self._pipelines[lang_code] = KPipeline(lang_code=lang_code)
            return self._pipelines[lang_code]

    def _lang_code_from_voice(self, voice: str) -> str:
        if voice and len(voice) >= 1:
            return VOICE_LANG_MAP.get(voice[0], "a")
        return "a"

    def generate(self, text: str, voice: str | None = None, speed: float = 1.0) -> list[AudioChunk]:
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
