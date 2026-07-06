"""Trigger avatar action."""

from __future__ import annotations

from typing import Annotated

import typer
from rich.console import Console

from engine.cli._config import get_port

console = Console()


def action_cmd(
    name: Annotated[str, typer.Argument(help="Action name (e.g., wave, nod, celebrate)")],
    port: Annotated[int, typer.Option(help="Server port")] = 0,
) -> None:
    """Trigger an avatar action."""
    from engine.cli._action import ACTIONS  # canonical gesture verbs (single source)
    if name not in ACTIONS:
        console.print(f"  [yellow]Action unrecognized:[/yellow] '{name}'. "
                      f"Valid: {', '.join(sorted(ACTIONS))}")
        raise typer.Exit(1)

    if port == 0:
        port = get_port()

    try:
        import httpx
        httpx.post(f"http://localhost:{port}/api/action", json={"name": name}, timeout=5)
        console.print(f"  Action: [bold]{name}[/bold]")
    except httpx.ConnectError:
        console.print("  [red]Server not running.[/red] Start with: uv run vape start")
