"""Speak text via the TTS server."""

from __future__ import annotations

from typing import Annotated

import typer
from rich.console import Console

from engine.cli._config import get_port

console = Console()


def speak_cmd(
    text: Annotated[str, typer.Argument(help="Text to speak")],
    voice: Annotated[str | None, typer.Option(help="Voice ID")] = None,
    speed: Annotated[float, typer.Option(help="Speech speed")] = 1.0,
    volume: Annotated[
        int | None, typer.Option(min=0, max=100, help="Volume 0-100, this utterance only")
    ] = None,
    port: Annotated[int, typer.Option(help="Server port")] = 0,
) -> None:
    """Send text to the TTS server to speak."""
    if port == 0:
        port = get_port()

    try:
        import httpx
        payload: dict = {"text": text, "speed": speed}
        if voice:
            payload["voice"] = voice
        if volume is not None:
            payload["volume"] = volume
        response = httpx.post(f"http://localhost:{port}/api/speak", json=payload, timeout=10)
        data = response.json()
        if data.get("status") == "ok":
            console.print(f"  [green]Speaking:[/green] {text[:80]}{'...' if len(text) > 80 else ''}")
        else:
            console.print(f"  [red]Error:[/red] {data.get('message', 'unknown')}")
    except httpx.ConnectError:
        console.print("  [red]Server not running.[/red] Start with: uv run vape start")
