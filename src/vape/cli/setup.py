"""Interactive setup wizard — engine selection, model downloads, language opt-in."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import IntPrompt

from vape.cli._paths import ROOT_DIR, PLUGINS_DIR, RENDERERS_DIR, SHELLS_DIR, CONFIG_PATH
from vape.cli._config import read_config, get_avatar_renderer, get_avatar_shell
from vape.cli._prereqs import run_all_checks
from vape.cli._progress import download_models, download_file, is_cached

console = Console()


def _load_plugin_manifests() -> list[dict]:
    """Load all plugin.json files from plugins/tts-*/ directories. Recommended first."""
    manifests = []
    for plugin_dir in sorted(PLUGINS_DIR.glob("tts-*")):
        manifest_path = plugin_dir / "plugin.json"
        if manifest_path.exists():
            data = json.loads(manifest_path.read_text())
            data["_dir"] = str(plugin_dir)
            manifests.append(data)
    # Fixed order: kokoro-onnx (recommended), kokoro (pytorch), kitten
    _order = {"kokoro-onnx": 0, "kokoro": 1, "kitten": 2}
    manifests.sort(key=lambda m: _order.get(m["name"], 99))
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
        ["uv", "sync", "--extra", extra],
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

    console.print(f"\n  [dim]Enter: 1,2 for specific, * for all, 0 or empty to skip[/dim]")
    selection = typer.prompt("  Select languages", default="0")

    if selection.strip() in ("0", ""):
        return []

    if selection.strip() == "*":
        return list(optional)

    selected = []
    for part in selection.split(","):
        try:
            idx = int(part.strip()) - 1
            if 0 <= idx < len(optional):
                selected.append(optional[idx])
        except ValueError:
            pass

    return selected


def _select_avatar(avatar_app, current: str | None) -> dict | None:
    """Display avatar menu, return selected plugin dict."""
    plugins = avatar_app.list_plugins_sorted()
    if not plugins:
        return None

    console.print("\n  [bold]Select Avatar:[/bold]\n")
    for i, p in enumerate(plugins, 1):
        tag = f" [green]({p.get('tag', '')})[/green]" if p.get("tag") else ""
        current_mark = " [yellow]<- current[/yellow]" if p["name"] == current else ""
        ready = "" if p.get("ready") or p.get("hasSource") else " [dim](not available)[/dim]"
        console.print(f"  [bold]{i}.[/bold] {p['displayName']}{tag}{current_mark}{ready}")
        console.print(f"     {p['description']}")
        console.print()

    choice = IntPrompt.ask("  Enter choice", default=1)
    if choice < 1 or choice > len(plugins):
        choice = 1
    return plugins[choice - 1]


def _select_shell(avatar_app, current: str | None) -> dict | None:
    """Display shell menu, return selected shell dict."""
    shells = avatar_app.discover_shells()
    if not shells:
        return None

    console.print("\n  [bold]Select Desktop Shell:[/bold]\n")
    for i, s in enumerate(shells, 1):
        tag = f" [green]({s.get('tag', '')})[/green]" if s.get("tag") else ""
        current_mark = " [yellow]<- current[/yellow]" if s["name"] == current else ""
        console.print(f"  [bold]{i}.[/bold] {s['displayName']}{tag}{current_mark}")
        console.print(f"     {s['description']}")
        console.print()

    choice = IntPrompt.ask("  Enter choice", default=1)
    if choice < 1 or choice > len(shells):
        choice = 1
    return shells[choice - 1]


# The Live2D Cubism Core is proprietary and not redistributable via git
# (.gitignore excludes it), so we fetch it from Live2D's official CDN on setup.
LIVE2D_CORE_URL = "https://cubism.live2d.com/sdk-web/cubismcore/live2dcubismcore.min.js"


def _ensure_live2d_core() -> None:
    """Download the Live2D Cubism Core into the live2d renderer if missing."""
    dest = RENDERERS_DIR / "avatar-live2d" / "lib" / "live2dcubismcore.min.js"
    if is_cached(dest):
        console.print("  [dim]✓ Live2D Cubism Core present[/dim]")
        return
    console.print("\n  Downloading Live2D Cubism Core...")
    try:
        download_file(LIVE2D_CORE_URL, dest, label="live2dcubismcore.min.js")
        console.print("  [green]✓ Live2D Cubism Core ready[/green]")
    except Exception as exc:  # network/offline — fail loud with instructions
        console.print(
            f"  [yellow]Could not download the Live2D Cubism Core ({exc}).[/yellow]\n"
            f"  [dim]Download it manually from {LIVE2D_CORE_URL}\n"
            f"  and save it to {dest}[/dim]"
        )


def _ensure_shell_deps(shell_name: str) -> None:
    """Install a shell's node deps (e.g. Electron) so first `vape start` is instant."""
    import shutil

    shell_dir = SHELLS_DIR / shell_name
    if not (shell_dir / "package.json").exists() or (shell_dir / "node_modules").exists():
        return
    npm = shutil.which("npm")
    if not npm:
        console.print(f"  [yellow]npm not found — {shell_name} shell deps not installed.[/yellow]")
        return
    console.print(f"\n  Installing {shell_name} shell dependencies...")
    result = subprocess.run([npm, "install"], cwd=str(shell_dir), timeout=180)
    if result.returncode == 0:
        console.print(f"  [green]✓ {shell_name} shell ready[/green]")
    else:
        console.print(f"  [yellow]{shell_name} shell dependency install failed.[/yellow]")


def _build_tauri() -> None:
    """Build the Tauri shell binary (compiles Rust — only when Tauri is chosen)."""
    import shutil

    shell_dir = SHELLS_DIR / "tauri"
    if not (shell_dir / "src-tauri").exists():
        console.print("  [yellow]Tauri shell scaffold not found — skipping.[/yellow]")
        return

    from vape.cli.start import _find_tauri_binary
    if _find_tauri_binary(shell_dir):
        console.print("  [dim]✓ Tauri shell already built[/dim]")
        return

    npx = shutil.which("npx")
    if not npx:
        console.print("  [yellow]npx not found — skipping Tauri build.[/yellow]")
        return

    npm = shutil.which("npm")
    if npm and not (shell_dir / "node_modules").exists():
        console.print("  Installing Tauri CLI...")
        subprocess.run([npm, "install"], cwd=str(shell_dir), capture_output=True, timeout=180)

    console.print("  Building Tauri shell (compiling Rust — this takes a few minutes)...")
    result = subprocess.run([npx, "tauri", "build"], cwd=str(shell_dir), timeout=900)
    if result.returncode == 0:
        console.print("  [green]✓ Tauri shell built[/green]")
    else:
        console.print("  [yellow]Tauri build failed — Electron remains available as the default shell.[/yellow]")


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


BANNER = r"""[bold cyan]
 ██╗   ██╗ █████╗ ██████╗ ███████╗
 ██║   ██║██╔══██╗██╔══██╗██╔════╝
 ██║   ██║███████║██████╔╝█████╗
 ╚██╗ ██╔╝██╔══██║██╔═══╝ ██╔══╝
  ╚████╔╝ ██║  ██║██║     ███████╗
   ╚═══╝  ╚═╝  ╚═╝╚═╝     ╚══════╝[/bold cyan]
 [dim]Vibe AI Partner Entity[/dim]
"""


def setup() -> None:
    """Interactive setup wizard — choose engine, download models, pick languages."""
    console.print(BANNER)

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
    current = read_config().get("tts", {}).get("engine")
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

    # Step 7: Avatar — pick a renderer (content) and a shell (window host)
    from vape.apps.avatar import AvatarApp
    avatar_app = AvatarApp(RENDERERS_DIR, SHELLS_DIR)
    avatar_manifest = _select_avatar(avatar_app, get_avatar_renderer())
    shell_manifest = _select_shell(avatar_app, get_avatar_shell())

    # Step 8: Install renderer deps + assets; prepare the chosen shell
    if avatar_manifest:
        avatar_app.build_plugin(avatar_manifest["name"])
        if avatar_manifest["name"] == "avatar-live2d":
            _ensure_live2d_core()
    if shell_manifest:
        if shell_manifest["name"] == "tauri":
            _build_tauri()
        else:
            _ensure_shell_deps(shell_manifest["name"])

    # Step 9: Save config. Voice IDs are engine-specific, so clear the old
    # voice when switching engines to avoid stale "voice X for engine Y" state.
    cfg = read_config()
    old_engine = cfg.get("tts", {}).get("engine")
    cfg.setdefault("tts", {})["engine"] = manifest["name"]
    if old_engine and old_engine != manifest["name"]:
        cfg["tts"].pop("voice", None)

    avatar_cfg = cfg.setdefault("avatar", {})
    avatar_cfg["renderer"] = avatar_manifest["name"] if avatar_manifest else "avatar-live2d"
    avatar_cfg["shell"] = shell_manifest["name"] if shell_manifest else "electron"
    # Migrate away from the legacy single-key schema.
    legacy_plugin = avatar_cfg.pop("plugin", None)
    plugins = avatar_cfg.get("plugins")
    if isinstance(plugins, dict) and legacy_plugin and legacy_plugin in plugins:
        plugins.setdefault(avatar_cfg["renderer"], plugins.pop(legacy_plugin))
    CONFIG_PATH.write_text(json.dumps(cfg, indent=2) + "\n")

    # Done
    console.print(Panel(
        "[green]Setup complete![/green]\n\n"
        "  Start:   [bold]uv run vape start[/bold]\n"
        "  Stop:    [bold]Ctrl+C[/bold] (or uv run vape stop)\n"
        "  Status:  [bold]uv run vape status[/bold]\n\n"
        "  Add languages later: [bold]uv run vape download --language zh[/bold]",
        style="green",
    ))
