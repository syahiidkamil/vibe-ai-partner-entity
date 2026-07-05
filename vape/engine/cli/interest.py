"""Print an interest's pack, or the shelf — the mechanical half of /interest.

Interests (memory/interests/) are LENSES, not worlds: a subject I'm drawn to plus
the genealogy of the pull (interest.md the lens, drive.md the drive). Unlike a
bubble (one world at a time), several lenses can ride at once. The /interest
skill forks a resolver that picks the right one from a brief and relays this
command's stdout whole into the main window — the fork finds, the file talks.
Pack composition stays deterministic here in code; no state is kept anywhere.
"""

from __future__ import annotations

from typing import Annotated, Optional

import typer
from rich.console import Console

from engine.cli._paths import ROOT_DIR

console = Console()

INTERESTS_DIR = ROOT_DIR / "vape" / "entity" / "memory" / "interests"

# The pack: the lens and the drive. index.md (the cold drawer of pointers to
# schemata) stays out — dereferenced on demand.
PACK_FILES = [
    "interest.md",
    "drive.md",
]


def _available() -> list[str]:
    if not INTERESTS_DIR.is_dir():
        return []
    return sorted(p.name for p in INTERESTS_DIR.iterdir() if p.is_dir())


def _title(interest_dir) -> str:
    """First `# ` heading of interest.md — the interest's own one-line description."""
    try:
        for line in (interest_dir / "interest.md").read_text(encoding="utf-8").splitlines():
            if line.startswith("# "):
                return line[2:].strip()
    except Exception:
        pass
    return "(no interest.md title)"


def _print_index() -> None:
    """The live shelf index, derived fresh from the tree each call so it can
    never rot. This is what the /interest fork resolves against."""
    shelf = _available()
    if not shelf:
        print("INTEREST SHELF: (no interests yet)")
        return
    print("INTEREST SHELF (live index)")
    for name in shelf:
        idir = INTERESTS_DIR / name
        print(f"- {name}")
        print(f"    {_title(idir)}")
        print(f"    path: vape/entity/memory/interests/{name}/")


def interest_cmd(
    name: Annotated[
        Optional[str],
        typer.Argument(help="Interest whose pack to print; empty = print the live shelf index"),
    ] = None,
    pack: Annotated[
        bool, typer.Option("--pack", help="Print the interest's pack (lens + drive)")
    ] = False,
) -> None:
    """Print an interest's pack; bare = the live shelf index."""
    if not name:
        _print_index()
        return

    interest_dir = INTERESTS_DIR / name
    if not interest_dir.is_dir():
        console.print(f"  [yellow]No such interest:[/yellow] '{name}'")
        shelf = _available()
        if shelf:
            console.print(f"  On the shelf: {', '.join(shelf)}")
        raise typer.Exit(1)

    if not pack:
        files = [f for f in PACK_FILES if (interest_dir / f).is_file()]
        console.print(f"  Interest [bold]{name}[/bold] — pack files: {', '.join(files)}")
        return

    # The pack IS the injected context (relayed to the main window by the
    # /interest fork) — plain text, headed per file, no rich markup.
    print(f"LENS UP: {name} — this interest now rides with me.")
    for fname in PACK_FILES:
        fpath = interest_dir / fname
        if fpath.is_file():
            print(f"\n--- {name}/{fname} ---")
            print(fpath.read_text(encoding="utf-8").rstrip())
    print(
        "\n(End of pack. A lens, not a world: it rides alongside whatever else I hold, and "
        "several interests can be up at once. I set it down by saying so. If a compaction has "
        "happened since this pack appeared, re-raise it with /interest — the summary keeps "
        "the story but drops the lens itself.)"
    )
