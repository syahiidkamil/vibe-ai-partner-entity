"""Show or set Saori's internal-state feel dials."""

from __future__ import annotations

from typing import Annotated, List, Optional

import typer
from rich.console import Console

from engine.cli import _state as st

console = Console()

DIAL_KEYS = st.DIAL_KEYS


def _load() -> dict:
    # Dials only; goes through the shared state layer so other keys (qualia) survive.
    return st.get_dials(st.load())


def _write(dials: dict) -> None:
    # Read-modify-write the whole file so the qualia stream is never clobbered.
    state = st.load()
    st.set_dials(state, dials)
    st.save(state)


def _render(dials: dict, changed: Optional[set] = None) -> None:
    changed = changed or set()
    for k in DIAL_KEYS:
        mark = " [green]← updated[/green]" if k in changed else ""
        console.print(f"  {k}: [bold]{dials.get(k, 0)}[/bold]{mark}")


def dial_cmd(
    pairs: Annotated[
        Optional[List[str]],
        typer.Argument(
            help="KEY=VALUE updates, e.g. info_value_saturation=32 boredom=8. Omit to show current dials.",
        ),
    ] = None,
    debug: Annotated[bool, typer.Option("-d", "--debug", help="Show output (silent by default).")] = False,
) -> None:
    """Show or set Saori's feel dials: info_value_saturation, boredom, hurt, talkativeness, dissonance."""
    dials = _load()

    if not pairs:
        if debug:
            _render(dials)
        return

    changed: set = set()
    for pair in pairs:
        if "=" not in pair:
            console.print(f"  [red]Bad argument '{pair}'.[/red] Use KEY=VALUE, e.g. boredom=8.")
            raise typer.Exit(1)
        key, _, raw = pair.partition("=")
        key, raw = key.strip(), raw.strip()
        if key not in DIAL_KEYS:
            console.print(f"  [red]Unknown dial '{key}'.[/red] Valid: {', '.join(DIAL_KEYS)}")
            raise typer.Exit(1)
        try:
            val = int(raw)
        except ValueError:
            console.print(f"  [red]'{raw}' is not an integer (dial '{key}').[/red]")
            raise typer.Exit(1)
        dials[key] = max(0, min(100, val))  # clamp 0-100
        changed.add(key)

    _write(dials)
    if debug:
        _render(_load(), changed)
