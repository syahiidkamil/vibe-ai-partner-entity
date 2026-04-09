"""Post-setup language/model download management."""

from __future__ import annotations

import json
import subprocess
from typing import Annotated

import typer
from rich.console import Console

from vape.cli._paths import ROOT_DIR, PLUGINS_DIR
from vape.cli._config import get_engine
from vape.cli._progress import download_models

console = Console()


def _load_manifest(engine: str) -> dict | None:
    """Load plugin manifest for an engine."""
    for plugin_dir in PLUGINS_DIR.glob("tts-*"):
        manifest_path = plugin_dir / "plugin.json"
        if manifest_path.exists():
            data = json.loads(manifest_path.read_text())
            if data["name"] == engine:
                return data
    return None


def download(
    language: Annotated[str | None, typer.Option("--language", "-l", help="Language code (e.g., zh, ja)")] = None,
    engine: Annotated[str | None, typer.Option("--engine", "-e", help="Engine name")] = None,
) -> None:
    """Download language packs or models for the current engine."""
    engine_name = engine or get_engine()
    if not engine_name:
        console.print("  [red]No engine configured.[/red] Run [bold]uv run vape setup[/bold] first.")
        raise typer.Exit(1)

    manifest = _load_manifest(engine_name)
    if not manifest:
        console.print(f"  [red]Plugin manifest not found for {engine_name}.[/red]")
        raise typer.Exit(1)

    if language:
        # Download specific language
        lang = next((l for l in manifest.get("languages", []) if l["code"] == language), None)
        if not lang:
            available = [l["code"] for l in manifest.get("languages", [])]
            console.print(f"  [red]Language '{language}' not available.[/red] Options: {', '.join(available)}")
            raise typer.Exit(1)

        if lang.get("included") and not lang.get("models") and not lang.get("postInstall"):
            console.print(f"  [green]{lang['name']} is already included (no extra download needed).[/green]")
            return

        console.print(f"  Downloading {lang['name']} language pack...")
        models = lang.get("models", [])
        if models:
            download_models(models)

        post_install = lang.get("postInstall")
        if post_install:
            check_cmd = lang.get("postInstallCheck")
            if check_cmd:
                result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True, cwd=str(ROOT_DIR))
                if result.returncode == 0 and "True" in result.stdout:
                    console.print(f"  [dim]✓ Post-install already done[/dim]")
                    return
            console.print(f"  Running post-install...")
            subprocess.run(post_install, shell=True, cwd=str(ROOT_DIR))

        console.print(f"  [green]{lang['name']} ready.[/green]")
    else:
        # Show available languages
        console.print(f"\n  [bold]Languages for {manifest['displayName']}:[/bold]\n")
        for lang in manifest.get("languages", []):
            status = "[green]included[/green]" if lang.get("included") else "[yellow]download needed[/yellow]"
            size = sum(m.get("size_mb", 0) for m in lang.get("models", []))
            size += lang.get("postInstallSize_mb", 0)
            size_str = f" (+{size}MB)" if size > 0 else ""
            console.print(f"  {lang['code']:8s} {lang['name']:25s} {status}{size_str}")
        console.print(f"\n  Download with: [bold]uv run vape download --language <code>[/bold]")
