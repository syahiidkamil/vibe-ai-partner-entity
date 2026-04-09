"""
TTS Plugin Loader — discovers engine plugins via entry points.

Primary: Python entry points (plugins self-register in pyproject.toml)
Fallback: try-import known plugin modules (backward compatibility)

Plugins register via:
  [project.entry-points."vibe.tts.engines"]
  kokoro-onnx = "vibe_plugin_tts_kokoro_onnx:KokoroOnnxEngine"
"""

from __future__ import annotations

import importlib
from importlib.metadata import entry_points

from vape.core import TTSEngineBase

# Known plugins for fallback discovery
_KNOWN_PLUGINS = [
    ("vibe_plugin_tts_kokoro_onnx", "KokoroOnnxEngine", "kokoro-onnx"),
    ("vibe_plugin_tts_kokoro", "KokoroEngine", "kokoro"),
    ("vibe_plugin_tts_kitten", "KittenEngine", "kitten"),
]


class PluginLoader:
    """Discover and instantiate TTS engine plugins."""

    @staticmethod
    def discover() -> dict[str, TTSEngineBase]:
        """Discover TTS plugins. Returns {name: engine_instance}."""
        engines: dict[str, TTSEngineBase] = {}

        # Primary: entry points
        for ep in entry_points(group="vibe.tts.engines"):
            try:
                engine_class = ep.load()
                engines[ep.name] = engine_class()
            except Exception:
                pass

        # Fallback: try-import known plugins
        if not engines:
            for module_name, class_name, name in _KNOWN_PLUGINS:
                try:
                    mod = importlib.import_module(module_name)
                    engines[name] = getattr(mod, class_name)()
                except (ImportError, AttributeError):
                    pass

        return engines
