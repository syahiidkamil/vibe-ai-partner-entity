"""
Kokoro ONNX Engine — lightweight ONNX runtime, CPU-friendly, ~300MB model.

Auto-downloads model files from GitHub releases on first init.
Uses misaki G2P for non-English languages (Japanese, etc.).
"""

from __future__ import annotations

import os
import threading
import urllib.request
from pathlib import Path

import numpy as np

from engine.core import AudioChunk, TTSEngineBase

MODEL_REPO = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0"
MODEL_FILE = "kokoro-v1.0.onnx"
VOICES_FILE = "voices-v1.0.bin"

ZH_MODEL_REPO = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.1"
ZH_MODEL_FILE = "kokoro-v1.1-zh.onnx"
ZH_VOICES_FILE = "voices-v1.1-zh.bin"
ZH_VOCAB_URL = "https://huggingface.co/hexgrad/Kokoro-82M-v1.1-zh/raw/main/config.json"
ZH_VOCAB_FILE = "kokoro-v1.1-zh-config.json"

# Language code → espeak language identifier
ESPEAK_LANG_MAP: dict[str, str] = {
    "fr": "fr-fr", "es": "es", "hi": "hi",
    "it": "it", "pt-br": "pt-br",
}

# Voice prefix → language code (same as PyTorch Kokoro)
VOICE_LANG_MAP: dict[str, str] = {
    "a": "en", "b": "en-gb",
    "j": "ja",
    "e": "es", "f": "fr", "h": "hi",
    "i": "it", "p": "pt-br", "z": "zh",
}

KOKORO_ONNX_VOICES = [
    # American English
    {"id": "af_heart",   "name": "Heart (Female)",    "language": "en-us", "gender": "female"},
    {"id": "af_bella",   "name": "Bella (Female)",    "language": "en-us", "gender": "female"},
    {"id": "af_nova",    "name": "Nova (Female)",     "language": "en-us", "gender": "female"},
    {"id": "af_sarah",   "name": "Sarah (Female)",    "language": "en-us", "gender": "female"},
    {"id": "am_adam",    "name": "Adam (Male)",        "language": "en-us", "gender": "male"},
    {"id": "am_michael", "name": "Michael (Male)",     "language": "en-us", "gender": "male"},
    # British English
    {"id": "bf_emma",    "name": "Emma (British F)",   "language": "en-gb", "gender": "female"},
    {"id": "bm_george",  "name": "George (British M)", "language": "en-gb", "gender": "male"},
    # Japanese
    {"id": "jf_alpha",      "name": "Alpha (Japanese F)",      "language": "ja", "gender": "female"},
    {"id": "jf_gongitsune", "name": "Gongitsune (Japanese F)", "language": "ja", "gender": "female"},
    {"id": "jf_nezumi",     "name": "Nezumi (Japanese F)",     "language": "ja", "gender": "female"},
    {"id": "jf_tebukuro",   "name": "Tebukuro (Japanese F)",   "language": "ja", "gender": "female"},
    {"id": "jm_kumo",       "name": "Kumo (Japanese M)",       "language": "ja", "gender": "male"},
    # French
    {"id": "ff_siwis",      "name": "Siwis (French F)",        "language": "fr", "gender": "female"},
    # Spanish
    {"id": "ef_dora",       "name": "Dora (Spanish F)",        "language": "es", "gender": "female"},
    {"id": "em_alex",       "name": "Alex (Spanish M)",        "language": "es", "gender": "male"},
    {"id": "em_santa",      "name": "Santa (Spanish M)",       "language": "es", "gender": "male"},
    # Hindi
    {"id": "hf_alpha",      "name": "Alpha (Hindi F)",         "language": "hi", "gender": "female"},
    {"id": "hf_beta",       "name": "Beta (Hindi F)",          "language": "hi", "gender": "female"},
    {"id": "hm_omega",      "name": "Omega (Hindi M)",         "language": "hi", "gender": "male"},
    {"id": "hm_psi",        "name": "Psi (Hindi M)",           "language": "hi", "gender": "male"},
    # Italian
    {"id": "if_sara",       "name": "Sara (Italian F)",        "language": "it", "gender": "female"},
    {"id": "im_nicola",     "name": "Nicola (Italian M)",      "language": "it", "gender": "male"},
    # Brazilian Portuguese
    {"id": "pf_dora",       "name": "Dora (Portuguese F)",     "language": "pt-br", "gender": "female"},
    {"id": "pm_alex",       "name": "Alex (Portuguese M)",     "language": "pt-br", "gender": "male"},
    {"id": "pm_santa",      "name": "Santa (Portuguese M)",    "language": "pt-br", "gender": "male"},
    # Mandarin Chinese (requires separate v1.1-zh model, downloaded on first use)
    {"id": "zf_001",        "name": "Chinese F1",              "language": "zh", "gender": "female"},
    {"id": "zf_002",        "name": "Chinese F2",              "language": "zh", "gender": "female"},
    {"id": "zf_003",        "name": "Chinese F3",              "language": "zh", "gender": "female"},
    {"id": "zf_004",        "name": "Chinese F4",              "language": "zh", "gender": "female"},
    {"id": "zm_009",        "name": "Chinese M1",              "language": "zh", "gender": "male"},
    {"id": "zm_010",        "name": "Chinese M2",              "language": "zh", "gender": "male"},
    {"id": "zm_011",        "name": "Chinese M3",              "language": "zh", "gender": "male"},
    {"id": "zm_012",        "name": "Chinese M4",              "language": "zh", "gender": "male"},
]

MAX_CHARS = 500


def _cache_dir() -> Path:
    d = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "kokoro-onnx"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _download_if_missing(filename: str, repo: str | None = MODEL_REPO, direct_url: str | None = None) -> str:
    path = _cache_dir() / filename
    if path.exists():
        return str(path)
    url = direct_url or f"{repo}/{filename}"
    print(f"  Downloading {filename}...")
    urllib.request.urlretrieve(url, path)
    print(f"  Downloaded {filename} ({path.stat().st_size / 1024 / 1024:.1f}MB)")
    return str(path)


def _lang_from_voice(voice: str) -> str:
    """Detect language from voice ID prefix."""
    if voice and len(voice) >= 1:
        return VOICE_LANG_MAP.get(voice[0], "en")
    return "en"


class KokoroOnnxEngine(TTSEngineBase):
    name = "kokoro-onnx"

    def __init__(self) -> None:
        self._kokoro = None
        self._kokoro_zh = None
        self._g2p_cache: dict[str, object] = {}
        self._g2p_lock = threading.Lock()
        self._voice: str = "af_heart"
        self._stopped = False

    def initialize(self) -> None:
        from kokoro_onnx import Kokoro

        model_path = _download_if_missing(MODEL_FILE)
        voices_path = _download_if_missing(VOICES_FILE)
        self._kokoro = Kokoro(model_path, voices_path)

        self._warmup()

    def _warmup(self) -> None:
        # First call to generate() pays for G2P import (misaki + espeak) plus
        # the initial ONNX inference compile. Pay it once at startup so the
        # first user-triggered speak is not delayed by ~5s.
        try:
            kokoro = self._get_kokoro(self._voice)
            processed, is_phonemes = self._phonemize(".", self._voice)
            kokoro.create(processed, voice=self._voice, speed=1.0, is_phonemes=is_phonemes)
        except Exception:
            pass

    def _get_kokoro(self, voice: str):
        """Return the correct Kokoro instance for the voice. Lazy-loads zh model."""
        if _lang_from_voice(voice) == "zh":
            if self._kokoro_zh is None:
                from kokoro_onnx import Kokoro

                model_path = _download_if_missing(ZH_MODEL_FILE, ZH_MODEL_REPO)
                voices_path = _download_if_missing(ZH_VOICES_FILE, ZH_MODEL_REPO)
                vocab_path = _download_if_missing(ZH_VOCAB_FILE, None, ZH_VOCAB_URL)
                self._kokoro_zh = Kokoro(model_path, voices_path, vocab_config=vocab_path)
            return self._kokoro_zh
        return self._kokoro

    def _get_g2p(self, lang: str):
        """Get or create a G2P instance for the language."""
        with self._g2p_lock:
            if lang in self._g2p_cache:
                return self._g2p_cache[lang]

            g2p = None
            if lang == "zh":
                from misaki import zh
                g2p = zh.ZHG2P(version="1.1")
            elif lang == "ja":
                from misaki import ja
                g2p = ja.JAG2P()
            elif lang in ("en", "en-gb"):
                from misaki import en, espeak
                fallback = espeak.EspeakFallback(british=(lang == "en-gb"))
                g2p = en.G2P(trf=False, british=(lang == "en-gb"), fallback=fallback)
            elif lang in ESPEAK_LANG_MAP:
                from misaki.espeak import EspeakG2P
                g2p = EspeakG2P(language=ESPEAK_LANG_MAP[lang])

            if g2p:
                self._g2p_cache[lang] = g2p
            return g2p

    def _phonemize(self, text: str, voice: str) -> tuple[str, bool]:
        """Convert text to phonemes if needed. Returns (text_or_phonemes, is_phonemes)."""
        lang = _lang_from_voice(voice)
        g2p = self._get_g2p(lang)
        if g2p:
            phonemes, _ = g2p(text)
            return phonemes, True
        # Fallback: let kokoro-onnx use its built-in tokenizer
        return text, False

    def generate(self, text: str, voice: str | None = None, speed: float = 1.0) -> list[AudioChunk]:
        if self._kokoro is None:
            raise RuntimeError("KokoroOnnxEngine not initialized")

        voice = voice or self._voice
        self._stopped = False

        if len(text) > MAX_CHARS:
            text = text[:MAX_CHARS].rsplit(" ", 1)[0]

        kokoro = self._get_kokoro(voice)
        processed, is_phonemes = self._phonemize(text, voice)
        audio, sr = kokoro.create(processed, voice=voice, speed=speed, is_phonemes=is_phonemes)

        if self._stopped:
            return []

        samples = np.array(audio, dtype=np.float32)
        return [AudioChunk(samples=samples, sample_rate=sr, is_last=True)]

    async def generate_stream(self, text: str, voice: str | None = None, speed: float = 1.0):
        if self._kokoro is None:
            raise RuntimeError("KokoroOnnxEngine not initialized")

        voice = voice or self._voice
        self._stopped = False

        if len(text) > MAX_CHARS:
            text = text[:MAX_CHARS].rsplit(" ", 1)[0]

        kokoro = self._get_kokoro(voice)
        processed, is_phonemes = self._phonemize(text, voice)
        async for audio, sr in kokoro.create_stream(processed, voice=voice, speed=speed, is_phonemes=is_phonemes):
            if self._stopped:
                break
            samples = np.array(audio, dtype=np.float32)
            yield AudioChunk(samples=samples, sample_rate=sr, is_last=False)

    def get_voices(self) -> list[dict]:
        return KOKORO_ONNX_VOICES

    def set_voice(self, voice_id: str) -> None:
        self._voice = voice_id

    def stop(self) -> None:
        self._stopped = True
