"""Show or set the standing speech volume."""

from __future__ import annotations

from typing import Annotated

import typer
from rich.console import Console

from engine.cli._config import read_config, write_config

console = Console()


def volume_cmd(
    level: Annotated[
        int | None,
        typer.Argument(min=0, max=100, help="Standing volume 0-100 (omit to show current)"),
    ] = None,
) -> None:
    """Show or set the standing speech volume (0-100, persists in config.json).

    The server reads it per utterance, so a change takes effect immediately —
    no restart. `vape speak --volume N` overrides it for one utterance only.
    """
    if level is None:
        current = read_config().get("tts", {}).get("volume", 100)
        console.print(f"  Volume: [bold]{current}[/bold] / 100")
        return

    write_config({"tts": {"volume": level}})
    console.print(f"  [green]Volume set:[/green] {level} / 100")
