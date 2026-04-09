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
        on_audio_chunk: Callable[[str, int, bool, str | None], Awaitable[None]],
    ) -> None:
        self.registry = registry
        self.pipeline = TTSPipeline(registry, on_audio_chunk)

    @classmethod
    def create(
        cls,
        config_path: Path,
        on_audio_chunk: Callable[[str, int, bool, str | None], Awaitable[None]],
    ) -> "TTSApp":
        """Factory: discover plugins, load config, wire everything."""
        # Discover available plugins
        engines = PluginLoader.discover()
        registry = EngineRegistry()
        for name, engine in engines.items():
            registry.register(name, engine)

        # Read preferred engine from config
        preferred = _read_preferred_engine(config_path)
        available = registry.list()

        # Activate preferred or first available
        if preferred and preferred in available:
            registry.switch(preferred)
        elif available:
            registry.switch(available[0])

        return cls(registry, on_audio_chunk)

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


def _read_preferred_engine(config_path: Path) -> str | None:
    """Read preferred TTS engine from config.json."""
    try:
        config = json.loads(config_path.read_text())
        return config.get("tts", {}).get("engine")
    except (FileNotFoundError, json.JSONDecodeError):
        return None
