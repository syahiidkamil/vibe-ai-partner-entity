"""TTS domain layer — plugin-agnostic interface for all TTS operations."""

from engine.apps.tts.tts_app import TTSApp
from engine.apps.tts.plugin_loader import PluginLoader
from engine.apps.tts.registry import EngineRegistry

__all__ = ["TTSApp", "PluginLoader", "EngineRegistry"]
