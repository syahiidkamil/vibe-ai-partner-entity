"""
TTSApp — Plugin-agnostic TTS facade.

All TTS operations go through this class. The server and CLI never
interact with engines directly — they use TTSApp as the single entry point.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, Awaitable

from vape.apps.tts.pipeline import TTSPipeline
from vape.apps.tts.plugin_loader import PluginLoader
from vape.apps.tts.registry import EngineRegistry


class TTSApp:
    """Plugin-agnostic TTS facade. All TTS operations go through here."""

    def __init__(
        self,
        registry: EngineRegistry,
        on_audio: Callable[[str, str, bool], Awaitable[None]],
    ) -> None:
        self.registry = registry
        self.pipeline = TTSPipeline(registry, on_audio)

    @classmethod
    def create(
        cls,
        config_path: Path,
        on_audio: Callable[[str, str, bool], Awaitable[None]],
    ) -> "TTSApp":
        """Factory: discover plugins, load config, wire everything."""
        # Discover available plugins
        engines = PluginLoader.discover()
        registry = EngineRegistry()
        for name, engine in engines.items():
            registry.register(name, engine)

        # Read preferred engine + voice from config
        preferred, voice = _read_tts_config(config_path)
        available = registry.list()

        # Pick target engine. Voice from config only applies when the preferred
        # engine is actually available AND the voice ID belongs to that engine.
        if preferred and preferred in available:
            valid_voice = _validate_voice(registry.get(preferred), voice, preferred)
            registry.switch(preferred, voice=valid_voice)
        elif available:
            target = available[0]
            if preferred:
                print(
                    f"[tts] WARNING: configured engine '{preferred}' is not installed; "
                    f"falling back to '{target}'. Available: {available}"
                )
            registry.switch(target)
        elif preferred:
            print(f"[tts] WARNING: no TTS engine plugins installed (configured: '{preferred}')")

        return cls(registry, on_audio)

    async def speak(self, text: str, voice: str | None = None, speed: float | None = None) -> None:
        """Generate and play TTS audio."""
        await self.pipeline.speak(text, voice=voice, speed=speed)

    def stop(self) -> None:
        """Abort current generation."""
        active = self.registry.get_active()
        if active:
            active.stop()

    def get_voices(self) -> list[dict]:
        """List available voices for the active engine."""
        active = self.registry.get_active()
        if not active:
            return []
        return active.get_voices()

    def switch_voice(self, voice_id: str) -> None:
        """Switch the active voice on the current engine."""
        active = self.registry.get_active()
        if active:
            active.set_voice(voice_id)

    @property
    def active_engine_name(self) -> str | None:
        """Get the name of the active engine."""
        active = self.registry.get_active()
        return active.name if active else None

    @property
    def available_engines(self) -> list[str]:
        """List all registered engine names."""
        return self.registry.list()

    def shutdown(self) -> None:
        """Clean shutdown — stop active engine."""
        active = self.registry.get_active()
        if active:
            active.stop()


def _read_tts_config(config_path: Path) -> tuple[str | None, str | None]:
    """Read preferred TTS engine and voice from config.json."""
    try:
        config = json.loads(config_path.read_text())
        tts = config.get("tts", {})
        return tts.get("engine"), tts.get("voice")
    except (FileNotFoundError, json.JSONDecodeError):
        return None, None


def _validate_voice(engine, voice: str | None, engine_name: str) -> str | None:
    """Return voice if it's a valid ID for the engine, else None (with warning)."""
    if not voice or engine is None:
        return None
    voice_ids = {v["id"] for v in engine.get_voices()}
    if voice in voice_ids:
        return voice
    print(
        f"[tts] WARNING: configured voice '{voice}' is not available for engine "
        f"'{engine_name}'; using engine default."
    )
    return None
