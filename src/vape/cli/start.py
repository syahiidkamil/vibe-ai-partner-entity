"""Start VAPE — TTS server + desktop avatar."""

from __future__ import annotations

import os
import platform
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from vape.cli._config import get_port, read_config
from vape.cli._paths import PLUGINS_DIR

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


def _launch_avatar(plugin_name: str, port: int) -> subprocess.Popen | None:
    """Launch the avatar desktop window from its plugin directory."""
    import shutil

    avatar_dir = PLUGINS_DIR / f"avatar-{plugin_name}"
    main_js = avatar_dir / "main.js"
    if not main_js.exists():
        console.print(f"  [yellow]Avatar plugin '{plugin_name}' has no main.js — skipping desktop window[/yellow]")
        return None

    npm = shutil.which("npm")
    npx = shutil.which("npx")

    if not npx:
        console.print(f"  [yellow]npx not found — cannot launch avatar[/yellow]")
        return None

    # Ensure node_modules
    if npm and not (avatar_dir / "node_modules").exists():
        console.print(f"  Installing avatar dependencies...")
        subprocess.run([npm, "install"], cwd=str(avatar_dir), capture_output=True, timeout=120)

    console.print(f"  Launching avatar desktop window...")
    return subprocess.Popen(
        [npx, "electron", str(main_js), "--port", str(port)],
        cwd=str(avatar_dir),
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

    config = read_config()
    avatar_plugin = config.get("avatar", {}).get("plugin", "live2d-electron")

    if daemon:
        console.print(f"  Starting server in background on port {port}...")
        proc = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "vape.server.app:app",
             "--host", host, "--port", str(port)],
            start_new_session=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        from vape.cli._paths import cache_dir
        pid_file = cache_dir() / "server.pid"
        pid_file.write_text(str(proc.pid))
        console.print(f"  [green]Server started (PID {proc.pid})[/green]")

        if _wait_for_server(port):
            _launch_avatar(avatar_plugin, port)
        return

    console.print(f"  Starting VAPE on port {port}...")

    avatar_proc = None

    def _start_avatar_when_ready():
        nonlocal avatar_proc
        if _wait_for_server(port):
            avatar_proc = _launch_avatar(avatar_plugin, port)

    avatar_thread = threading.Thread(target=_start_avatar_when_ready, daemon=True)
    avatar_thread.start()

    console.print(f"  TTS server: http://localhost:{port}")
    console.print(f"  Press [bold]Ctrl+C[/bold] to stop.\n")

    try:
        import uvicorn
        uvicorn.run("vape.server.app:app", host=host, port=port)
    finally:
        if avatar_proc and avatar_proc.poll() is None:
            avatar_proc.terminate()
