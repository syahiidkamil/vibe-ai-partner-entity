"""``vape bubble`` — declare / release / list memory scopes (bubbles).

A thin delegate over ``engine.memory.bubble``. The register lives in
``vape/entity/mental/active_bubble.json``; entering writes it, leaving nulls it, and
the per-turn hook (``bubble-ground.sh``) injects the active bubble's pack.

  ``vape bubble enter chess``   — DECLARE the chess scope active (the willed Eve act).
  ``vape bubble leave``         — RELEASE: write ``active: null``.
  ``vape bubble list``          — list available bubbles + show which is active.

This sub-app is registered into ``main.py`` by the INTEGRATOR, never here.
"""

from __future__ import annotations

import typer
from rich.console import Console

console = Console()

bubble_app = typer.Typer(
    name="bubble",
    help="Declare / release / list memory scopes (bubbles).",
    no_args_is_help=True,
)


@bubble_app.command("enter")
def enter(
    name: str = typer.Argument(..., help="The bubble (scope) to enter, e.g. chess."),
    by: str = typer.Option(
        "saori",
        "--by",
        help="Provenance: saori (willed), kamil (human path), or auto (advisory).",
    ),
) -> None:
    """DECLARE a bubble active. Its pack injects from the next turn onward."""
    from engine.memory import bubble as B

    available = B.list_bubbles()
    norm = name.strip().lower()
    try:
        B.enter(norm, by=by)
    except ValueError as e:
        console.print(f"  [red]cannot enter[/red]: {e}")
        raise typer.Exit(code=2)

    if norm not in available:
        console.print(
            f"  [yellow]entered[/yellow] [bold]{norm}[/bold] — but no "
            f"[bold]bubbles/{norm}/HOT.md[/bold] pack exists yet, so nothing will "
            f"inject until one is built. Available: {', '.join(available) or '(none)'}"
        )
    else:
        console.print(
            f"  [green]entered[/green] bubble [bold]{norm}[/bold] (by {by}). "
            f"Its soul-pack injects from the next turn. Release with "
            f"[bold]vape bubble leave[/bold]."
        )


@bubble_app.command("leave")
def leave() -> None:
    """RELEASE the active bubble (write ``active: null``)."""
    from engine.memory import bubble as B

    reg = B.active()
    B.leave()
    if reg is None:
        console.print("  no bubble was active — nothing to release.")
    else:
        console.print(
            f"  [green]left[/green] bubble [bold]{reg['active']}[/bold]. "
            f"The injection stops next turn."
        )


@bubble_app.command("list")
def list_cmd() -> None:
    """List available bubbles and show which one (if any) is active."""
    from engine.memory import bubble as B

    available = B.list_bubbles()
    reg = B.active()
    active_name = reg["active"] if reg else None

    if not available:
        console.print("  no bubbles built yet (no [bold]bubbles/<name>/HOT.md[/bold]).")
    else:
        console.print("  bubbles:")
        for name in available:
            mark = "  [green]● active[/green]" if name == active_name else ""
            console.print(f"    - {name}{mark}")

    if reg is not None:
        console.print(
            f"  active: [bold]{active_name}[/bold] "
            f"(by {reg.get('entered_by')}, {reg.get('turns_active', 0)} turns)"
        )
    else:
        console.print("  active: [dim]none[/dim]")
