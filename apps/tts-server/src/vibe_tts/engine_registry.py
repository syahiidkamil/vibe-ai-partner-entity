"""
Multi-backend TTS engine registry.

Mirrors the EngineRegistry pattern from the architecture doc:
  register(name, engine)     — add engine to registry
  get_active() -> engine     — get currently active engine
  switch(name)               — switch active engine
  list() -> [names]          — list registered engine names
"""

from __future__ import annotations

from vibe_tts.engines.base import TTSEngineBase


class EngineRegistry:
    def __init__(self) -> None:
        self._engines: dict[str, TTSEngineBase] = {}
        self._active: str | None = None

    def register(self, name: str, engine: TTSEngineBase) -> None:
        """Register an engine. Does not activate it."""
        self._engines[name] = engine

    def get_active(self) -> TTSEngineBase | None:
        """Return the currently active engine, or None."""
        if self._active is None:
            return None
        return self._engines.get(self._active)

    def switch(self, name: str) -> None:
        """Switch the active engine. Raises KeyError if not registered."""
        if name not in self._engines:
            raise KeyError(f"Engine '{name}' not registered. Available: {list(self._engines.keys())}")

        # Stop current engine if switching
        current = self.get_active()
        if current:
            current.stop()

        self._engines[name].initialize()
        self._active = name

    def list(self) -> list[str]:
        """List all registered engine names."""
        return list(self._engines.keys())
