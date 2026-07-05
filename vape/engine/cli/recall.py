"""`vape recall` — search the memory index; the two-hop's first hop.

Human output is a ranked table of gists + pointers (I am the reranker: the
top-k enters my context and I judge). `--json` is the stable machine face.
`--deref ID` prints the pointed body (the second hop) and counts the use.
"""

from __future__ import annotations

import json as _json
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

console = Console()


def recall_cmd(
    cue: Annotated[str, typer.Argument(help="The cue: a question, a situation, a fragment")] = "",
    kind: Annotated[str | None, typer.Option(help="Filter: case|note|schema|person|key|chunk|...")] = None,
    topic: Annotated[str | None, typer.Option(help="Filter: schemata topic")] = None,
    space: Annotated[str, typer.Option(help="memory | file | all")] = "memory",
    k: Annotated[int, typer.Option("-k", "--k", min=1, max=50, help="How many hits")] = 8,
    explore: Annotated[bool, typer.Option("--explore", help="Creative mode: drop the usage term, widen challengers")] = False,
    deref: Annotated[str | None, typer.Option("--deref", help="Dereference a hit id from the last recall")] = None,
    json_out: Annotated[bool, typer.Option("--json", help="Machine-readable output")] = False,
) -> None:
    """Search my memory index and return ranked gists + pointers."""
    from engine.memory.factory import get_firewall

    fw, note = get_firewall()

    if deref:
        resolved = fw.deref(deref)
        if resolved is None:
            console.print(f"  [red]No hit '{deref}' in the last recall.[/red] Run a recall first.")
            raise typer.Exit(1)
        body, pointer = resolved
        if json_out:
            console.print_json(data={"id": deref, "pointer": pointer, "body": body})
        else:
            loc = pointer.get("file", pointer.get("day", "?"))
            anchor = pointer.get("anchor", "")
            console.print(f"[dim]{loc}{'#' + anchor if anchor and anchor != 'doc' else ''}[/dim]\n")
            console.print(body)
        return

    if not cue.strip():
        console.print("  [red]Give me a cue[/red] (or --deref ID).")
        raise typer.Exit(1)

    result = fw.recall(cue, space=space, kind=kind, topic=topic, k=k, explore=explore)

    if json_out:
        payload = result.to_json()
        if note:
            payload["note"] = note
        print(_json.dumps(payload, ensure_ascii=False, indent=1))
        return

    caps = result.capabilities
    legs = "+".join(x for x, on in (("fts", caps.fts), ("vector", caps.vector)) if on) or "scan"
    console.print(
        f"  backend: [bold]{result.backend}[/bold] ({legs}) · space: {space} · "
        f"k: {k} · explore: {'on' if explore else 'off'}"
    )
    if note:
        console.print(f"  [yellow]{note}[/yellow]")
    if not result.hits:
        console.print("  [dim]nothing surfaced — try --space all, or grep the tree[/dim]")
        return

    table = Table(show_lines=False, pad_edge=False)
    table.add_column("id", style="dim")
    table.add_column("score", justify="right")
    table.add_column("kind")
    table.add_column("gist", max_width=58, overflow="ellipsis")
    table.add_column("pointer", max_width=44, overflow="ellipsis")
    table.add_column("flags")
    for h in result.hits:
        flags = " ".join(f for f, on in (
            ("stale", h.stale), ("chal", h.challenger), ("dream", h.provenance == "dream"),
        ) if on)
        gist = h.content.splitlines()[0] if h.content else ""
        ptr = h.pointer.get("file", h.pointer.get("day", "?"))
        anchor = h.pointer.get("anchor", "")
        if anchor and anchor not in ("doc",):
            ptr = f"{ptr}#{anchor}"
        table.add_row(h.id, f"{h.score:.2f}", h.kind, gist, ptr, flags)
    console.print(table)
    console.print(f"  [dim]Dereference: uv run vape recall --deref {result.hits[0].id}[/dim]")
