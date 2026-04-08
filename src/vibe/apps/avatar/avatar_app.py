"""
AvatarApp — Plugin-agnostic avatar facade.

Discovers avatar plugins from plugins/avatar-*/ directories.
Each plugin provides pre-built static files (HTML/JS/CSS) that the
server serves. The selected plugin is determined by config.json.

Avatar plugins are frontend bundles, not Python packages — they only
need a plugin.json manifest and a dist/ directory.
"""

from __future__ import annotations

import json
from pathlib import Path


class AvatarPlugin:
    """Represents a discovered avatar plugin."""

    def __init__(self, manifest: dict, plugin_dir: Path) -> None:
        self.name: str = manifest["name"]
        self.display_name: str = manifest["displayName"]
        self.description: str = manifest["description"]
        self.tag: str = manifest.get("tag", "")
        self.renderer: str = manifest["renderer"]
        self.features: dict = manifest.get("features", {})
        self.models: list[dict] = manifest.get("models", [])
        self._plugin_dir = plugin_dir
        self._dist_dir_name = manifest.get("distDir", "dist")

    @property
    def dist_dir(self) -> Path:
        """Path to the pre-built static files."""
        return self._plugin_dir / self._dist_dir_name

    @property
    def is_ready(self) -> bool:
        """Check if the plugin has built static files."""
        return (self.dist_dir / "index.html").exists()

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "displayName": self.display_name,
            "description": self.description,
            "renderer": self.renderer,
            "features": self.features,
            "models": self.models,
            "ready": self.is_ready,
        }


class AvatarApp:
    """Plugin-agnostic avatar facade. Discovers and manages avatar plugins."""

    def __init__(self, plugins_dir: Path) -> None:
        self._plugins_dir = plugins_dir
        self._plugins: dict[str, AvatarPlugin] = {}
        self._discover()

    def _discover(self) -> None:
        """Discover avatar plugins from plugins/avatar-*/ directories."""
        for plugin_dir in sorted(self._plugins_dir.glob("avatar-*")):
            manifest_path = plugin_dir / "plugin.json"
            if not manifest_path.exists():
                continue
            try:
                manifest = json.loads(manifest_path.read_text())
                if manifest.get("category") != "avatar":
                    continue
                plugin = AvatarPlugin(manifest, plugin_dir)
                self._plugins[plugin.name] = plugin
            except (json.JSONDecodeError, KeyError):
                pass

    def get_plugin(self, name: str) -> AvatarPlugin | None:
        """Get a specific avatar plugin by name."""
        return self._plugins.get(name)

    def get_active(self, config_renderer: str | None = None) -> AvatarPlugin | None:
        """Get the active avatar plugin based on config. Falls back to first ready plugin."""
        if config_renderer and config_renderer in self._plugins:
            plugin = self._plugins[config_renderer]
            if plugin.is_ready:
                return plugin

        # Fallback: first ready plugin
        for plugin in self._plugins.values():
            if plugin.is_ready:
                return plugin
        return None

    def list_plugins(self) -> list[dict]:
        """List all discovered avatar plugins."""
        return [p.to_dict() for p in self._plugins.values()]

    def get_static_dir(self, config_renderer: str | None = None) -> Path | None:
        """Get the static files directory for the active avatar plugin."""
        plugin = self.get_active(config_renderer)
        if plugin and plugin.is_ready:
            return plugin.dist_dir
        return None
