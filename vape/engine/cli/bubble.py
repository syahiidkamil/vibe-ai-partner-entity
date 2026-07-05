"""Print a bubble's hot-pack, or the shelf — the mechanical half of /bubble.

Bubbles (memory/bubbles/) are switched by the /bubble skill: a fork resolves
which bubble a situation brief means, runs this command, and relays its stdout
whole into the main window. The fork finds, this file talks — pack composition
(which files, what order) stays deterministic in code, so the injected conduct
text is byte-exact and never agent-improvised. No state is kept anywhere: the
pack sitting in the window IS the presence; leaving is declared in-conversation,
and a fresh session simply wakes bubble-less.
"""

from __future__ import annotations

from typing import Annotated, Optional

import typer
from rich.console import Console

from engine.cli._paths import ROOT_DIR

console = Console()

BUBBLES_DIR = ROOT_DIR / "vape" / "entity" / "memory" / "bubbles"

# The hot-pack: bubble.md plus the two mandatory companions (the anti-theater
# floor). index.md and per-game files stay cold — dereferenced on demand.
PACK_FILES = [
    "bubble.md",
    "affective_world_of_values_and_view.md",
    "notable_intercourses.md",
]


def _available() -> list[str]:
    if not BUBBLES_DIR.is_dir():
        return []
    return sorted(p.name for p in BUBBLES_DIR.iterdir() if p.is_dir())


def _title(bubble_dir) -> str:
    """First `# ` heading of bubble.md — the bubble's own one-line self-description."""
    try:
        for line in (bubble_dir / "bubble.md").read_text(encoding="utf-8").splitlines():
            if line.startswith("# "):
                return line[2:].strip()
    except Exception:
        pass
    return "(no bubble.md title)"


def _print_index() -> None:
    """The live shelf index: name, path, games, title — derived fresh from the
    tree each call so it can never rot. This is what the /bubble fork resolves
    against (rendered into its prompt by dynamic-context preprocessing)."""
    shelf = _available()
    if not shelf:
        print("BUBBLE SHELF: (no bubbles yet)")
        return
    print("BUBBLE SHELF (live index)")
    for name in shelf:
        bdir = BUBBLES_DIR / name
        games_dir = bdir / "games"
        games = (
            ", ".join(sorted(p.name for p in games_dir.iterdir() if p.is_dir()))
            if games_dir.is_dir()
            else ""
        )
        games_note = f" · games: {games}" if games else ""
        print(f"- {name}{games_note}")
        print(f"    {_title(bdir)}")
        print(f"    path: vape/entity/memory/bubbles/{name}/")


def bubble_cmd(
    name: Annotated[
        Optional[str],
        typer.Argument(help="Bubble whose pack to print; empty = print the live shelf index"),
    ] = None,
    pack: Annotated[
        bool, typer.Option("--pack", help="Print the bubble's hot-pack")
    ] = False,
    game: Annotated[
        Optional[str],
        typer.Option("--game", help="Also pack this games/<game>/ subtree (protocol + matches)"),
    ] = None,
) -> None:
    """Print a bubble's hot-pack; bare = the live shelf index."""
    if not name:
        _print_index()
        return

    bubble_dir = BUBBLES_DIR / name
    if not bubble_dir.is_dir():
        console.print(f"  [yellow]No such bubble:[/yellow] '{name}'")
        shelf = _available()
        if shelf:
            console.print(f"  On the shelf: {', '.join(shelf)}")
        raise typer.Exit(1)

    if not pack:
        files = [f for f in PACK_FILES if (bubble_dir / f).is_file()]
        console.print(f"  Bubble [bold]{name}[/bold] — pack files: {', '.join(files)}")
        return

    # The pack IS the injected context (relayed to the main window by the
    # /bubble fork) — plain text, headed per file, no rich markup. With
    # --game, the named games/<game>/ subtree rides along (conduct protocol
    # + notable matches), still verbatim, still one append.
    print(f"ACTIVE BUBBLE: {name} — I have stepped into this small world now.")
    pack_paths = [bubble_dir / f for f in PACK_FILES]
    if game:
        game_dir = bubble_dir / "games" / game
        if game_dir.is_dir():
            pack_paths += sorted(
                p for p in game_dir.glob("*.md") if p.name != "index.md"
            )
        else:
            print(f"\n(note: no games/{game}/ under this bubble; base pack only)")
    for fpath in pack_paths:
        if fpath.is_file():
            print(f"\n--- {fpath.relative_to(BUBBLES_DIR)} ---")
            print(fpath.read_text(encoding="utf-8").rstrip())
    print(
        "\n(End of pack. This bubble's conduct binds me until I say I've left or a newer "
        "pack supersedes it; deeper files in its folder are dereferenced on demand. If a "
        "compaction has happened since this pack appeared, re-enter with /bubble — the "
        "summary keeps the story but drops the conduct text.)"
    )
