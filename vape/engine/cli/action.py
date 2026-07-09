"""Trigger avatar action."""

from __future__ import annotations

from typing import Annotated

import typer
from rich.console import Console

from engine.cli._config import get_port

console = Console()


def action_cmd(
    name: Annotated[str, typer.Argument(help="Action name (e.g., wave, nod, celebrate)")],
    text: Annotated[
        str | None,
        typer.Argument(help="Optional caption text (e.g. laugh's default 'Hahaha!')"),
    ] = None,
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

    payload: dict = {"name": name}
    if text:
        payload["text"] = text

    try:
        import httpx
        httpx.post(f"http://localhost:{port}/api/action", json=payload, timeout=5)
        caption = f" — \"{text}\"" if text else ""
        console.print(f"  Action: [bold]{name}[/bold]{caption}")
    except httpx.ConnectError:
        console.print("  [red]Server not running.[/red] Start with: uv run vape start")
