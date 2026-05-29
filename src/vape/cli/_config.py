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


# Avatar selection — a running avatar is one renderer + one shell.
DEFAULT_RENDERER = "avatar-live2d"
DEFAULT_SHELL = "electron"

# Every legacy avatar.plugin value setup.py ever wrote was "<renderer>-electron".
LEGACY_PLUGIN_MAP = {
    "live2d-electron": ("avatar-live2d", "electron"),
    "threejs-electron": ("avatar-threejs", "electron"),
    "html-electron": ("avatar-html", "electron"),
}


def get_avatar_selection() -> tuple[str, str]:
    """Return (renderer, shell). New schema wins; legacy avatar.plugin is migrated in-memory."""
    avatar = read_config().get("avatar", {})
    renderer, shell = avatar.get("renderer"), avatar.get("shell")
    if renderer:
        return renderer, (shell or DEFAULT_SHELL)

    legacy = avatar.get("plugin")  # e.g. "live2d-electron"
    if legacy:
        if legacy in LEGACY_PLUGIN_MAP:
            return LEGACY_PLUGIN_MAP[legacy]
        if "-" in legacy:
            base, _, sh = legacy.rpartition("-")
            renderer, shell = base, (sh or DEFAULT_SHELL)
        else:
            renderer, shell = legacy, DEFAULT_SHELL
        return (renderer if renderer.startswith("avatar-") else f"avatar-{renderer}", shell)

    return (DEFAULT_RENDERER, DEFAULT_SHELL)


def get_avatar_renderer() -> str:
    """Get the configured avatar renderer name (e.g. 'avatar-live2d')."""
    return get_avatar_selection()[0]


def get_avatar_shell() -> str:
    """Get the configured shell name (e.g. 'electron')."""
    return get_avatar_selection()[1]


def get_avatar_plugin() -> str | None:
    """Deprecated shim — returns the resolved renderer name."""
    return get_avatar_selection()[0]


def get_vocal_mode() -> str:
    """Get the entity vocal mode."""
    return read_config().get("entity", {}).get("vocalMode", "silent")
