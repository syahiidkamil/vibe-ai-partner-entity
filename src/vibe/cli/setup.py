"""Interactive setup wizard — engine selection, model downloads, language opt-in."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import IntPrompt, Confirm

from vibe.cli._paths import ROOT_DIR, PLUGINS_DIR
from vibe.cli._config import read_config, write_config
from vibe.cli._prereqs import run_all_checks
from vibe.cli._progress import download_models

console = Console()


def _load_plugin_manifests() -> list[dict]:
    """Load all plugin.json files from plugins/tts-*/ directories."""
    manifests = []
    for plugin_dir in sorted(PLUGINS_DIR.glob("tts-*")):
        manifest_path = plugin_dir / "plugin.json"
        if manifest_path.exists():
            data = json.loads(manifest_path.read_text())
            data["_dir"] = str(plugin_dir)
            manifests.append(data)
    return manifests


def _total_model_size(manifest: dict) -> int:
    """Sum up required model sizes in MB."""
    return sum(m.get("size_mb", 0) for m in manifest.get("models", []))


def _select_engine(manifests: list[dict], current: str | None) -> dict:
    """Display engine menu, return selected manifest."""
    console.print("\n  [bold]Select TTS engine:[/bold]\n")

    for i, m in enumerate(manifests, 1):
        tag = f" [green]({m['tag']})[/green]" if m.get("tag") else ""
        size = _total_model_size(m)
        size_str = f"~{size}MB download" if size > 0 else "auto-downloads on first use"
        current_mark = " [yellow]← current[/yellow]" if m["name"] == current else ""
        console.print(f"  [bold]{i}.[/bold] {m['displayName']}{tag}{current_mark}")
        console.print(f"     {m['description']} ({size_str})")
        console.print()

    choice = IntPrompt.ask("  Enter choice", default=1)
    if choice < 1 or choice > len(manifests):
        choice = 1
    return manifests[choice - 1]


def _install_deps(manifest: dict) -> None:
    """Run uv sync with the appropriate --extra for this engine."""
    extra = manifest["uvExtra"]
    console.print(f"\n  Installing {manifest['displayName']} dependencies...")
    result = subprocess.run(
        [sys.executable, "-m", "uv", "sync", "--extra", extra],
        cwd=str(ROOT_DIR),
        capture_output=False,
    )
    if result.returncode != 0:
        console.print("  [red]Dependency installation failed.[/red]")
        raise typer.Exit(1)
    console.print("  [green]Dependencies installed.[/green]")


def _select_languages(manifest: dict) -> list[dict]:
    """Display language selection, return list of selected non-included languages."""
    languages = manifest.get("languages", [])
    included = [l for l in languages if l.get("included")]
    optional = [l for l in languages if not l.get("included")]

    if not optional:
        return []

    included_names = ", ".join(l["name"] for l in included)
    console.print(f"\n  [bold]Language packs[/bold]")
    console.print(f"  Included: {included_names}")
    console.print(f"\n  Additional languages available:")

    for i, lang in enumerate(optional, 1):
        size = lang.get("postInstallSize_mb", 0) + sum(
            m.get("size_mb", 0) for m in lang.get("models", [])
        )
        console.print(f"    {i}. {lang['name']} (+{size}MB)")

    if not Confirm.ask("\n  Download additional languages?", default=False):
        return []

    selection = typer.prompt("  Select languages (comma-separated numbers)")
    selected = []
    for part in selection.split(","):
        try:
            idx = int(part.strip()) - 1
            if 0 <= idx < len(optional):
                selected.append(optional[idx])
        except ValueError:
            pass

    return selected


def _download_language_pack(lang: dict) -> None:
    """Download models and run postInstall for a language."""
    console.print(f"\n  Downloading {lang['name']} support...")

    # Download language-specific models
    models = lang.get("models", [])
    if models:
        download_models(models)

    # Run post-install command (e.g., UniDic download)
    post_install = lang.get("postInstall")
    if post_install:
        # Check if already installed
        check_cmd = lang.get("postInstallCheck")
        if check_cmd:
            result = subprocess.run(
                check_cmd, shell=True, capture_output=True, text=True, cwd=str(ROOT_DIR),
            )
            if result.returncode == 0 and "True" in result.stdout:
                console.print(f"  [dim]✓ {lang['name']} post-install already done[/dim]")
                return

        console.print(f"  Running post-install for {lang['name']}...")
        subprocess.run(post_install, shell=True, cwd=str(ROOT_DIR))


def setup() -> None:
    """Interactive setup wizard — choose engine, download models, pick languages."""
    console.print(Panel("[bold]Vibe AI Partner Setup[/bold]", style="blue"))

    # Step 1: Prerequisites
    console.print("\n  [bold]Checking prerequisites...[/bold]")
    if not run_all_checks():
        console.print("\n  [red]Prerequisites not met. Fix the issues above and retry.[/red]")
        raise typer.Exit(1)

    # Step 2: Load plugin manifests
    manifests = _load_plugin_manifests()
    if not manifests:
        console.print("  [red]No TTS plugins found in plugins/ directory.[/red]")
        raise typer.Exit(1)

    # Step 3: Engine selection
    current = read_config().get("ttsEngine")
    manifest = _select_engine(manifests, current)

    # Step 4: Install dependencies
    _install_deps(manifest)

    # Step 5: Download models
    models = manifest.get("models", [])
    if models:
        console.print(f"\n  [bold]Downloading model files...[/bold]")
        download_models(models)

    # Step 6: Language selection
    selected_langs = _select_languages(manifest)
    for lang in selected_langs:
        _download_language_pack(lang)

    # Step 7: Save config
    write_config({"ttsEngine": manifest["name"]})

    # Done
    console.print(Panel(
        "[green]Setup complete![/green]\n\n"
        "  Start:   [bold]uv run vibe start[/bold]\n"
        "  Stop:    [bold]Ctrl+C[/bold] (or uv run vibe stop)\n"
        "  Status:  [bold]uv run vibe status[/bold]\n\n"
        "  Add languages later: [bold]uv run vibe download --language zh[/bold]",
        style="green",
    ))
