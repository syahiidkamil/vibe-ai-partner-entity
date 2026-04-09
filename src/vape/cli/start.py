"""Start the Vibe AI Partner server."""

from __future__ import annotations

import os
import platform
import socket
import subprocess
import sys
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from vape.cli._config import get_port

console = Console()


def _is_port_in_use(port: int) -> bool:
    """Check if a port is already in use."""
    try:
        with socket.create_connection(("localhost", port), timeout=1):
            return True
    except (ConnectionRefusedError, OSError):
        return False


def _set_env_defaults() -> None:
    """Set platform-specific environment variables."""
    # PyTorch MPS fallback for macOS (reads from tts.plugins.kokoro config)
    from vape.cli._config import read_config
    kokoro_config = read_config().get("tts", {}).get("plugins", {}).get("kokoro", {})
    if kokoro_config.get("pytorchMpsFallback", True) and "PYTORCH_ENABLE_MPS_FALLBACK" not in os.environ:
        os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

    # macOS: espeak-ng library path
    if platform.system() == "Darwin" and "PHONEMIZER_ESPEAK_LIBRARY" not in os.environ:
        for lib_path in [
            "/opt/homebrew/lib/libespeak-ng.dylib",
            "/usr/local/lib/libespeak-ng.dylib",
        ]:
            if Path(lib_path).exists():
                os.environ["PHONEMIZER_ESPEAK_LIBRARY"] = lib_path
                break


def start(
    port: Annotated[int, typer.Option(help="Server port")] = 0,
    host: Annotated[str, typer.Option(help="Bind address")] = "0.0.0.0",
    daemon: Annotated[bool, typer.Option("--daemon", help="Run in background")] = False,
) -> None:
    """Start TTS server + avatar (foreground by default)."""
    if port == 0:
        port = get_port()

    if _is_port_in_use(port):
        console.print(f"  [red]Port {port} is already in use.[/red]")
        console.print(f"  Run [bold]uv run vape stop[/bold] or use [bold]--port {port + 1}[/bold]")
        raise typer.Exit(1)

    _set_env_defaults()

    if daemon:
        console.print(f"  Starting server in background on port {port}...")
        proc = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "vape.server.app:app",
             "--host", host, "--port", str(port)],
            start_new_session=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        # Write PID for stop command
        from vape.cli._paths import cache_dir
        pid_file = cache_dir() / "server.pid"
        pid_file.write_text(str(proc.pid))
        console.print(f"  [green]Server started (PID {proc.pid})[/green]")
        console.print(f"  Avatar: http://localhost:{port}")
        return

    console.print(f"  Starting VAPE on port {port}...")
    console.print(f"  Avatar: http://localhost:{port}")
    console.print(f"  Press [bold]Ctrl+C[/bold] to stop.\n")

    import uvicorn
    uvicorn.run("vape.server.app:app", host=host, port=port)
