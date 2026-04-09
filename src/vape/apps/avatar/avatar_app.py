"""
AvatarApp — Plugin-agnostic avatar facade.

Discovers avatar plugins, builds them via npm, generates a merged
interface that the server uses for expression resolution.

Three-layer interface contract:
  Default:  lipSync (amplitude), ttsState (speaking/idle) — always available
  Plugin:   what this renderer type supports (feelings, expressions, physics)
  Model:    what this specific model can do (feeling list, expression aliases)
"""

from __future__ import annotations

import json
import shutil
import subprocess
from datetime import datetime, timezone
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
        self.order: int = manifest.get("order", 99)
        self.interface: dict = manifest.get("interface") or manifest.get("features", {})
        self.models: list[dict] = manifest.get("models", [])
        self._plugin_dir = plugin_dir
        self._dist_dir_name = manifest.get("distDir", "dist")

    @property
    def plugin_dir(self) -> Path:
        return self._plugin_dir

    @property
    def dist_dir(self) -> Path:
        return self._plugin_dir / self._dist_dir_name

    @property
    def has_source(self) -> bool:
        return (self._plugin_dir / "package.json").exists()

    @property
    def is_built(self) -> bool:
        return (self.dist_dir / "index.html").exists()

    @property
    def is_ready(self) -> bool:
        return self.is_built

    @property
    def default_model(self) -> dict | None:
        for m in self.models:
            if m.get("default"):
                return m
        return self.models[0] if self.models else None

    def load_model_capabilities(self, model_id: str | None = None) -> dict | None:
        """Load capabilities.json for a specific model (or default)."""
        model = None
        if model_id:
            model = next((m for m in self.models if m["id"] == model_id), None)
        if not model:
            model = self.default_model
        if not model:
            return None

        caps_path = self.dist_dir / model["path"] / "capabilities.json"
        if not caps_path.exists():
            return None
        try:
            return json.loads(caps_path.read_text())
        except (json.JSONDecodeError, OSError):
            return None

    def build(self) -> bool:
        """Build this plugin via npm install && npm run build."""
        if not self.has_source:
            return False

        npm = shutil.which("npm")
        if not npm:
            return False

        try:
            result = subprocess.run(
                [npm, "install"], cwd=str(self._plugin_dir),
                capture_output=True, text=True, timeout=120,
            )
            if result.returncode != 0:
                console.print(f"  [red]npm install failed for {self.name}[/red]")
                return False

            result = subprocess.run(
                [npm, "run", "build"], cwd=str(self._plugin_dir),
                capture_output=True, text=True, timeout=120,
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
            "interface": self.interface,
            "models": self.models,
            "ready": self.is_ready,
            "hasSource": self.has_source,
        }


class AvatarApp:
    """Plugin-agnostic avatar facade. Discovers, builds, and manages avatar plugins."""

    def __init__(self, plugins_dir: Path) -> None:
        self._plugins_dir = plugins_dir
        self._plugins: dict[str, AvatarPlugin] = {}
        self._interface: dict | None = None
        self._discover()

    def _discover(self) -> None:
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
        return self._plugins.get(name)

    def get_active(self, config_plugin: str | None = None) -> AvatarPlugin | None:
        if config_plugin and config_plugin in self._plugins:
            plugin = self._plugins[config_plugin]
            if plugin.is_ready:
                return plugin
        for plugin in self._plugins.values():
            if plugin.is_ready:
                return plugin
        return None

    def build_plugin(self, name: str) -> bool:
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

    def build_active(self, config_plugin: str | None = None) -> bool:
        name = config_plugin or next(iter(self._plugins), None)
        if not name:
            return False
        return self.build_plugin(name)

    def list_plugins(self) -> list[dict]:
        return [p.to_dict() for p in self._plugins.values()]

    def list_plugins_sorted(self) -> list[dict]:
        """List plugins sorted by order field."""
        plugins = sorted(self._plugins.values(), key=lambda p: p.order)
        return [p.to_dict() for p in plugins]

    def get_static_dir(self, config_plugin: str | None = None) -> Path | None:
        plugin = self.get_active(config_plugin)
        if plugin and plugin.is_ready:
            return plugin.dist_dir
        return None

    # ─── Interface Contract System ────────────────────────────

    def generate_interface(self, config_plugin: str | None = None, model_id: str | None = None) -> dict | None:
        """Generate merged interface from plugin.json + capabilities.json."""
        plugin = self.get_active(config_plugin)
        if not plugin:
            self._interface = None
            return None

        model = None
        if model_id:
            model = next((m for m in plugin.models if m["id"] == model_id), None)
        if not model:
            model = plugin.default_model

        caps = plugin.load_model_capabilities(model["id"] if model else None)

        interface: dict = {
            "version": "1.0",
            "generatedAt": datetime.now(timezone.utc).isoformat(),
            "default": {
                "lipSync": {"method": "rms", "range": [0, 1]},
                "ttsState": {"modes": ["speaking", "idle"]},
            },
            "plugin": {
                "name": plugin.name,
                "displayName": plugin.display_name,
                "renderer": plugin.renderer,
                "supports": plugin.interface,
            },
            "model": None,
        }

        if caps and model:
            interface["model"] = {
                "id": model["id"],
                "name": model.get("name", model["id"]),
                "feelings": [k for k, v in caps.get("feelings", {}).items() if v is not None],
                "selfExpressions": list(caps.get("selfExpressions", {}).keys()),
                "expressionAliases": caps.get("expressionAliases", {}),
                "lipSync": caps.get("lipSync", {}),
            }

        self._interface = interface
        return interface

    def get_interface(self) -> dict | None:
        """Return the current interface (generate if not yet done)."""
        return self._interface

    def resolve_action(self, action_name: str) -> str | None:
        """Translate system expression trigger to model self-expression.

        Returns model expression name, or None if unsupported.
        Falls through to original name if no alias mapping exists.
        """
        if not self._interface or not self._interface.get("model"):
            return action_name

        aliases = self._interface["model"].get("expressionAliases", {})
        if action_name in aliases:
            return aliases[action_name]  # None means "can't do this"

        return action_name  # Not in alias map — pass through

    # ─── Shell System ─────────────────────────────────────────

    def discover_shells(self) -> list[dict]:
        """Discover shell plugins (plugins/shell-*/)."""
        shells = []
        for shell_dir in sorted(self._plugins_dir.glob("shell-*")):
            manifest_path = shell_dir / "plugin.json"
            if not manifest_path.exists():
                continue
            try:
                data = json.loads(manifest_path.read_text())
                if data.get("category") != "shell":
                    continue
                data["_dir"] = str(shell_dir)
                shells.append(data)
            except (json.JSONDecodeError, KeyError):
                pass
        shells.sort(key=lambda s: s.get("order", 99))
        return shells

    def launch_shell(self, shell_name: str, avatar_dist: Path) -> subprocess.Popen | None:
        """Launch a shell plugin with the given avatar dist path."""
        shell_dir = self._plugins_dir / f"shell-{shell_name}"
        manifest_path = shell_dir / "plugin.json"
        if not manifest_path.exists():
            console.print(f"  [yellow]Shell '{shell_name}' not found[/yellow]")
            return None

        npm = shutil.which("npm")
        npx = shutil.which("npx")

        # Ensure node_modules
        if npm and not (shell_dir / "node_modules").exists():
            console.print(f"  Installing shell dependencies...")
            subprocess.run([npm, "install"], cwd=str(shell_dir), capture_output=True, timeout=120)

        if shell_name == "electron" and npx:
            console.print(f"  Launching avatar desktop window...")
            return subprocess.Popen(
                [npx, "electron", str(shell_dir / "main.js"), "--dist", str(avatar_dist)],
                cwd=str(shell_dir),
                start_new_session=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

        console.print(f"  [yellow]Shell '{shell_name}' not yet supported[/yellow]")
        return None
