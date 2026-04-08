"""Check server health status."""

from __future__ import annotations

from typing import Annotated

import typer
from rich.console import Console

from vibe.cli._config import get_port

console = Console()


def status(
    port: Annotated[int, typer.Option(help="Server port")] = 0,
) -> None:
    """Check if the server is running and show status."""
    if port == 0:
        port = get_port()

    try:
        import httpx
        response = httpx.get(f"http://localhost:{port}/api/health", timeout=5)
        data = response.json()
        console.print(f"  [green]Server running[/green] on port {port}")
        console.print(f"  Engine: {data.get('engine', 'none')}")
        console.print(f"  Uptime: {data.get('uptime', 0)}s")
    except Exception:
        console.print(f"  [red]Server not running[/red] on port {port}")
        console.print(f"  Start with: [bold]uv run vibe start[/bold]")
