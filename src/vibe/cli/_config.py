"""Read/write config.json at the project root."""

from __future__ import annotations

import json
from vibe.cli._paths import CONFIG_PATH


def read_config() -> dict:
    """Read config.json, return dict or empty dict on error."""
    try:
        return json.loads(CONFIG_PATH.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def write_config(updates: dict) -> None:
    """Merge updates into config.json and write atomically."""
    config = read_config()
    config.update(updates)
    CONFIG_PATH.write_text(json.dumps(config, indent=2) + "\n")


def get_engine() -> str | None:
    """Get the configured TTS engine name."""
    return read_config().get("ttsEngine")


def get_port() -> int:
    """Get the configured server port."""
    return read_config().get("ttsPort", 5111)
