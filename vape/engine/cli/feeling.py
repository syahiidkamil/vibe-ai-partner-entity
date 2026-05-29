"""Set avatar feeling."""

from __future__ import annotations

from typing import Annotated

import typer
from rich.console import Console

from engine.cli._config import get_port

console = Console()


def feeling_cmd(
    name: Annotated[str, typer.Argument(help="Feeling name (e.g., happy, curious, proud)")],
    port: Annotated[int, typer.Option(help="Server port")] = 0,
) -> None:
    """Set the avatar's feeling."""
    if port == 0:
        port = get_port()

    try:
        import httpx
        httpx.post(f"http://localhost:{port}/api/feeling", json={"name": name}, timeout=5)
        console.print(f"  Feeling: [bold]{name}[/bold]")
    except httpx.ConnectError:
        console.print("  [red]Server not running.[/red] Start with: uv run vape start")
