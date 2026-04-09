"""Read/write config.json at the project root."""

from __future__ import annotations

import json
from vape.cli._paths import CONFIG_PATH


def read_config() -> dict:
    """Read config.json, return dict or empty dict on error."""
    try:
        return json.loads(CONFIG_PATH.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def write_config(updates: dict) -> None:
    """Deep-merge updates into config.json and write."""
    config = read_config()
    _deep_merge(config, updates)
    CONFIG_PATH.write_text(json.dumps(config, indent=2) + "\n")


def _deep_merge(base: dict, updates: dict) -> None:
    """Recursively merge updates into base dict."""
    for key, value in updates.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value


def get_engine() -> str | None:
    """Get the configured TTS engine name."""
    return read_config().get("tts", {}).get("engine")


def get_port() -> int:
    """Get the configured server port."""
    return read_config().get("server", {}).get("port", 5111)


def get_avatar_plugin() -> str | None:
    """Get the configured avatar renderer."""
    return read_config().get("avatar", {}).get("plugin")


def get_vocal_mode() -> str:
    """Get the entity vocal mode."""
    return read_config().get("entity", {}).get("vocalMode", "silent")
