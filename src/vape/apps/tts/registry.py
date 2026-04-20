"""
Multi-backend TTS engine registry.

Mirrors the EngineRegistry pattern from the architecture doc:
  register(name, engine)     — add engine to registry
  get_active() -> engine     — get currently active engine
  switch(name)               — switch active engine
  list() -> [names]          — list registered engine names
"""

from __future__ import annotations

from vape.core import TTSEngineBase


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

    def switch(self, name: str, voice: str | None = None) -> None:
        """Switch the active engine. Raises KeyError if not registered.

        If voice is provided, it is set on the engine before initialize() so
        warmup paths can use the correct language.
        """
        if name not in self._engines:
            raise KeyError(f"Engine '{name}' not registered. Available: {list(self._engines.keys())}")

        # Stop current engine if switching
        current = self.get_active()
        if current:
            current.stop()

        engine = self._engines[name]
        if voice is not None:
            engine.set_voice(voice)
        engine.initialize()
        self._active = name

    def list(self) -> list[str]:
        """List all registered engine names."""
        return list(self._engines.keys())
