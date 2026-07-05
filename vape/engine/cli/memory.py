"""`vape memory` — tend the retrieval index: index / doctor / schema / stats.

S1 ships doctor + schema (the tier truth-teller); index and stats arrive with
the S2 store and grow in S5.
"""

from __future__ import annotations

from typing import Annotated

import typer
from rich.console import Console

console = Console()

memory_app = typer.Typer(help="Tend the memory retrieval index", no_args_is_help=True)


@memory_app.command("doctor")
def doctor_cmd() -> None:
    """Which tier am I actually on, and what's missing for the next rung."""
    from engine.cli._config import read_config
    from engine.memory.factory import get_firewall, memory_config, _root_dir

    root = _root_dir()
    cfg = memory_config(root)
    fw, note = get_firewall()
    caps = fw.backend.capabilities()

    console.print(f"  configured: retrieval=[bold]{cfg['retrieval']}[/bold] · embedder={cfg['embedder']}")
    legs = ", ".join(x for x, on in (("fts", caps.fts), ("vector", caps.vector)) if on) or "pure scan"
    console.print(
        f"  actual:     backend=[bold]{caps.name}[/bold] ({legs}) · "
        f"spaces={'+'.join(sorted(caps.spaces))} · persistent={'yes' if caps.persistent else 'no'}"
    )
    if note:
        console.print(f"  [yellow]{note}[/yellow]")
    if caps.name == "files":
        console.print("  [dim]next rung: the sqlite index (S2) — uv run vape memory index once it lands[/dim]")


@memory_app.command("schema")
def schema_cmd() -> None:
    """Live schema introspection from the running backend (never stale)."""
    from engine.memory.factory import get_firewall

    fw, _ = get_firewall()
    console.print(fw.backend.schema())


@memory_app.command("index")
def index_cmd(
    full: Annotated[bool, typer.Option("--full", help="Drop and rebuild the whole index")] = False,
) -> None:
    """Sweep the tree into the index (arrives with the S2 store)."""
    console.print("  [yellow]The indexer arrives with S2 (core store + retrieval-sqlite).[/yellow]")
    raise typer.Exit(1)


@memory_app.command("stats")
def stats_cmd() -> None:
    """Usage distribution — the dogma thermometer (arrives with the S2 store)."""
    console.print("  [yellow]Stats arrive with S2 (usage counters need the core store).[/yellow]")
    raise typer.Exit(1)
