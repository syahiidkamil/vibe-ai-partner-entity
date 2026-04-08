"""TTS domain layer — plugin-agnostic interface for all TTS operations."""

from vibe.apps.tts.tts_app import TTSApp
from vibe.apps.tts.plugin_loader import PluginLoader
from vibe.apps.tts.registry import EngineRegistry

__all__ = ["TTSApp", "PluginLoader", "EngineRegistry"]
