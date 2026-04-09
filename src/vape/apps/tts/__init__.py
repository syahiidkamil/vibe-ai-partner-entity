"""TTS domain layer — plugin-agnostic interface for all TTS operations."""

from vape.apps.tts.tts_app import TTSApp
from vape.apps.tts.plugin_loader import PluginLoader
from vape.apps.tts.registry import EngineRegistry

__all__ = ["TTSApp", "PluginLoader", "EngineRegistry"]
