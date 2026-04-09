"""
AvatarApp — Plugin-agnostic avatar facade.

Discovers avatar plugins from plugins/avatar-*/ directories.
Each plugin has source code (package.json + src/) that gets built
automatically during setup via npm install && npm run build.

The user never runs npm commands — the CLI handles it.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from rich.console import Console

console = Console()


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
    def plugin_dir(self) -> Path:
        return self._plugin_dir

    @property
    def dist_dir(self) -> Path:
        """Path to the built static files."""
        return self._plugin_dir / self._dist_dir_name

    @property
    def has_source(self) -> bool:
        """Check if this plugin has buildable source code."""
        return (self._plugin_dir / "package.json").exists()

    @property
    def is_built(self) -> bool:
        """Check if the plugin has been built (dist/index.html exists)."""
        return (self.dist_dir / "index.html").exists()

    @property
    def is_ready(self) -> bool:
        """Check if the plugin can be served."""
        return self.is_built

    def build(self) -> bool:
        """Build this plugin via npm install && npm run build. Returns success."""
        if not self.has_source:
            return False

        node = shutil.which("node")
        npm = shutil.which("npm")
        if not node or not npm:
            return False

        try:
            # npm install
            result = subprocess.run(
                [npm, "install"],
                cwd=str(self._plugin_dir),
                capture_output=True,
                text=True,
                timeout=120,
            )
            if result.returncode != 0:
                console.print(f"  [red]npm install failed for {self.name}[/red]")
                return False

            # npm run build
            result = subprocess.run(
                [npm, "run", "build"],
                cwd=str(self._plugin_dir),
                capture_output=True,
                text=True,
                timeout=120,
            )
            if result.returncode != 0:
                console.print(f"  [red]npm run build failed for {self.name}[/red]")
                return False

            return True
        except subprocess.TimeoutExpired:
            console.print(f"  [red]Build timed out for {self.name}[/red]")
            return False

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "displayName": self.display_name,
            "description": self.description,
            "renderer": self.renderer,
            "features": self.features,
            "models": self.models,
            "ready": self.is_ready,
            "hasSource": self.has_source,
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

    def build_plugin(self, name: str) -> bool:
        """Build a specific avatar plugin. Returns success."""
        plugin = self._plugins.get(name)
        if not plugin:
            return False
        if plugin.is_built:
            console.print(f"  [dim]✓ {plugin.display_name} already built[/dim]")
            return True
        if not plugin.has_source:
            console.print(f"  [yellow]No source code for {plugin.display_name}[/yellow]")
            return False
        console.print(f"  Building {plugin.display_name}...")
        success = plugin.build()
        if success:
            console.print(f"  [green]✓ {plugin.display_name} built[/green]")
        return success

    def build_active(self, config_renderer: str | None = None) -> bool:
        """Build the active avatar plugin if not already built."""
        name = config_renderer or next(iter(self._plugins), None)
        if not name:
            return False
        return self.build_plugin(name)

    def list_plugins(self) -> list[dict]:
        """List all discovered avatar plugins."""
        return [p.to_dict() for p in self._plugins.values()]

    def get_static_dir(self, config_renderer: str | None = None) -> Path | None:
        """Get the static files directory for the active avatar plugin."""
        plugin = self.get_active(config_renderer)
        if plugin and plugin.is_ready:
            return plugin.dist_dir
        return None
