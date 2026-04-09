"""Stop the running Vibe AI Partner server."""

from __future__ import annotations

import os
import signal
from typing import Annotated

import typer
from rich.console import Console

from vape.cli._config import get_port

console = Console()


def stop(
    port: Annotated[int, typer.Option(help="Server port")] = 0,
) -> None:
    """Stop the running server."""
    if port == 0:
        port = get_port()

    # Try HTTP shutdown first
    try:
        import httpx
        response = httpx.post(f"http://localhost:{port}/api/shutdown", timeout=5)
        if response.status_code == 200:
            console.print("  [green]Server shutting down.[/green]")
            return
    except (httpx.ConnectError, httpx.ReadError):
        pass

    # Fallback: PID file
    from vape.cli._paths import cache_dir
    pid_file = cache_dir() / "server.pid"
    if pid_file.exists():
        try:
            pid = int(pid_file.read_text().strip())
            os.kill(pid, signal.SIGTERM)
            pid_file.unlink(missing_ok=True)
            console.print(f"  [green]Server stopped (PID {pid}).[/green]")
            return
        except (ProcessLookupError, ValueError):
            pid_file.unlink(missing_ok=True)

    console.print(f"  [yellow]No server found on port {port}.[/yellow]")
