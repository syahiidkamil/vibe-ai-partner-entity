"""Start VAPE — TTS server + desktop avatar (renderer + shell)."""

from __future__ import annotations

import json
import os
import platform
import shutil
import signal
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from engine.apps.avatar import AvatarApp
from engine.cli._config import get_avatar_selection, get_port, read_config
from engine.cli._paths import RENDERERS_DIR, SHELLS_DIR, cache_dir

console = Console()


def _is_port_in_use(port: int) -> bool:
    try:
        with socket.create_connection(("localhost", port), timeout=1):
            return True
    except (ConnectionRefusedError, OSError):
        return False


def _wait_for_server(port: int, timeout: int = 30) -> bool:
    """Wait for the server to be ready."""
    for _ in range(timeout * 2):
        if _is_port_in_use(port):
            return True
        time.sleep(0.5)
    return False


def _set_env_defaults() -> None:
    kokoro_config = read_config().get("tts", {}).get("plugins", {}).get("kokoro", {})
    if kokoro_config.get("pytorchMpsFallback", True) and "PYTORCH_ENABLE_MPS_FALLBACK" not in os.environ:
        os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

    if platform.system() == "Darwin" and "PHONEMIZER_ESPEAK_LIBRARY" not in os.environ:
        for lib_path in [
            "/opt/homebrew/lib/libespeak-ng.dylib",
            "/usr/local/lib/libespeak-ng.dylib",
        ]:
            if Path(lib_path).exists():
                os.environ["PHONEMIZER_ESPEAK_LIBRARY"] = lib_path
                break


def _ensure_node_deps(directory: Path) -> None:
    """Run `npm install` in a dir that has a package.json but no node_modules."""
    if not (directory / "package.json").exists():
        return
    if (directory / "node_modules").exists():
        return
    npm = shutil.which("npm")
    if not npm:
        console.print("  [yellow]npm not found — cannot install dependencies[/yellow]")
        return
    console.print(f"  Installing dependencies in {directory.name}...")
    subprocess.run([npm, "install"], cwd=str(directory), capture_output=True, timeout=180)


def _find_tauri_binary(shell_dir: Path) -> Path | None:
    """Locate a built Tauri binary (release preferred) under the shell's src-tauri."""
    target = shell_dir / "src-tauri" / "target"
    for profile in ("release", "debug"):
        binary = target / profile / "vape-avatar"
        if binary.exists() and os.access(binary, os.X_OK):
            return binary
    return None


def _avatar_pid_file() -> Path:
    return cache_dir() / "avatar.pid"


def _launch_avatar(renderer: str, shell: str, port: int) -> subprocess.Popen | None:
    """Launch the avatar window: resolve renderer + shell, then host the renderer."""
    avatar_app = AvatarApp(RENDERERS_DIR, SHELLS_DIR)

    plugin = avatar_app.get_active(renderer)
    if plugin is None:
        console.print(
            f"  [yellow]Avatar renderer '{renderer}' is not available — skipping desktop window.[/yellow]\n"
            f"  [dim]Run `vape setup` to install it, or check vape/plugins/renderers/{renderer}.[/dim]"
        )
        return None

    shell_obj = avatar_app.get_shell(shell)
    if shell_obj is None:
        console.print(f"  [yellow]Shell '{shell}' not found under plugins/shells — skipping desktop window.[/yellow]")
        return None

    # Renderer assets (pixi/three) live in the renderer dir; the shell runtime
    # (electron) installs in the shell dir.
    _ensure_node_deps(plugin.plugin_dir)

    if shell == "electron":
        proc = _launch_electron(shell_obj.shell_dir, plugin.window, port)
    elif shell == "tauri":
        proc = _launch_tauri(shell_obj.shell_dir, plugin.window, port)
    else:
        console.print(f"  [yellow]Unknown shell '{shell}' — skipping desktop window.[/yellow]")
        return None

    if proc is not None:
        _avatar_pid_file().write_text(str(proc.pid))
    return proc


def _launch_electron(shell_dir: Path, window: dict, port: int) -> subprocess.Popen | None:
    npx = shutil.which("npx")
    if not npx:
        console.print("  [yellow]npx not found — cannot launch Electron shell.[/yellow]")
        return None

    _ensure_node_deps(shell_dir)

    console.print("  Launching avatar window (Electron)...")
    return subprocess.Popen(
        [npx, "electron", str(shell_dir / "main.js"),
         "--port", str(port), "--window", json.dumps(window)],
        cwd=str(shell_dir),
        start_new_session=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def _launch_tauri(shell_dir: Path, window: dict, port: int) -> subprocess.Popen | None:
    """Launch the Tauri shell. Requires a built binary (built during `vape setup`)."""
    binary = _find_tauri_binary(shell_dir)
    if binary is None:
        console.print(
            "  [yellow]Tauri shell is not built yet.[/yellow]\n"
            "  [dim]Run `vape setup` and choose the Tauri shell, or build it with "
            "`npx tauri build` in plugins/shells/tauri.[/dim]"
        )
        return None

    console.print("  [dim]Launching avatar window (Tauri — experimental)...[/dim]")
    env = {
        **os.environ,
        "VAPE_PORT": str(port),
        "VAPE_WIDTH": str(window.get("width", 420)),
        "VAPE_HEIGHT": str(window.get("height", 400)),
        "VAPE_TITLE": str(window.get("title", "VAPE Avatar")),
    }
    return subprocess.Popen(
        [str(binary)],
        cwd=str(shell_dir / "src-tauri"),
        env=env,
        start_new_session=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def start(
    port: Annotated[int, typer.Option(help="Server port")] = 0,
    host: Annotated[str, typer.Option(help="Bind address")] = "0.0.0.0",
    daemon: Annotated[bool, typer.Option("--daemon", help="Run in background")] = False,
) -> None:
    """Start TTS server + desktop avatar."""
    if port == 0:
        port = get_port()

    if _is_port_in_use(port):
        console.print(f"  [red]Port {port} is already in use.[/red]")
        console.print(f"  Run [bold]uv run vape stop[/bold] or use [bold]--port {port + 1}[/bold]")
        raise typer.Exit(1)

    _set_env_defaults()

    renderer, shell = get_avatar_selection()

    if daemon:
        console.print(f"  Starting server in background on port {port}...")
        proc = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "engine.server.app:app",
             "--host", host, "--port", str(port)],
            start_new_session=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        pid_file = cache_dir() / "server.pid"
        pid_file.write_text(str(proc.pid))
        console.print(f"  [green]Server started (PID {proc.pid})[/green]")

        if _wait_for_server(port):
            _launch_avatar(renderer, shell, port)
        return

    console.print(f"  Starting VAPE on port {port}...")
    console.print(f"  [dim]renderer: {renderer}  •  shell: {shell}[/dim]")

    avatar_proc = None

    def _start_avatar_when_ready():
        nonlocal avatar_proc
        if _wait_for_server(port):
            avatar_proc = _launch_avatar(renderer, shell, port)

    avatar_thread = threading.Thread(target=_start_avatar_when_ready, daemon=True)
    avatar_thread.start()

    console.print(f"  TTS server: http://localhost:{port}")
    console.print(f"  Press [bold]Ctrl+C[/bold] to stop.\n")

    try:
        import uvicorn
        uvicorn.run("engine.server.app:app", host=host, port=port)
    finally:
        if avatar_proc and avatar_proc.poll() is None:
            # avatar_proc is the launcher (npx) group leader — kill the whole
            # group so the spawned window process goes down with it.
            try:
                os.killpg(os.getpgid(avatar_proc.pid), signal.SIGTERM)
            except (ProcessLookupError, PermissionError):
                avatar_proc.terminate()
        _avatar_pid_file().unlink(missing_ok=True)
