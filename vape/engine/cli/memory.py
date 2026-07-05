"""`vape memory` — tend the retrieval index: index / doctor / schema / stats."""

from __future__ import annotations

from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

console = Console()

memory_app = typer.Typer(help="Tend the memory retrieval index", no_args_is_help=True)


def _parts():
    """(root, cfg, backend, note, core) — shared plumbing for the subcommands."""
    from engine.memory.factory import (
        _root_dir, build_backend, build_core_store, memory_config,
    )
    root = _root_dir()
    cfg = memory_config(root)
    backend, note = build_backend(root, cfg)
    core = build_core_store(root)
    return root, cfg, backend, note, core


@memory_app.command("index")
def index_cmd(
    full: Annotated[bool, typer.Option("--full", help="Drop and rebuild the whole index")] = False,
) -> None:
    """Sweep the markdown tree into the index (drains the reindex queue first)."""
    from engine.memory.indexer import Indexer

    root, cfg, backend, note, core = _parts()
    caps = backend.capabilities()
    if not caps.persistent:
        reason = note or "backend 'files' holds no store"
        console.print(f"  [yellow]Nothing to index:[/yellow] {reason}")
        raise typer.Exit(1)
    if core is None:
        console.print("  [red]Core store unavailable (storage/index/core.db).[/red]")
        raise typer.Exit(1)

    res = Indexer(root, core, backend).sweep(full=full)
    if res.skipped_lock:
        console.print("  [yellow]Another sweep is running — skipping (it will catch up).[/yellow]")
        raise typer.Exit(0)
    r = res.report
    console.print(
        f"  swept [bold]{res.files_seen}[/bold] files · changed {res.files_changed} · "
        f"deleted {res.files_deleted}"
    )
    console.print(
        f"  rows: upserted {r.upserted} · embedded {r.embedded} · evicted {r.evicted}"
        + (f" · [red]errors {len(r.errors)}[/red]" if r.errors else "")
    )
    for e in r.errors[:5]:
        console.print(f"    [red]{e}[/red]")


@memory_app.command("doctor")
def doctor_cmd() -> None:
    """Which tier am I actually on, and what's missing for the next rung."""
    root, cfg, backend, note, core = _parts()
    caps = backend.capabilities()

    console.print(f"  configured: retrieval=[bold]{cfg['retrieval']}[/bold] · embedder={cfg['embedder']}")
    legs = ", ".join(x for x, on in (("fts", caps.fts), ("vector", caps.vector)) if on) or "pure scan"
    console.print(
        f"  actual:     backend=[bold]{caps.name}[/bold] ({legs}) · "
        f"spaces={'+'.join(sorted(caps.spaces))} · persistent={'yes' if caps.persistent else 'no'}"
    )
    if note:
        console.print(f"  [yellow]{note}[/yellow]")

    if core is not None:
        last = core.meta_get("last_sweep_at") or "never"
        console.print(f"  last sweep: {last} · reindex queue: {core.queue_depth()}")
    if caps.name == "files":
        console.print("  [dim]next rung: uv run vape memory index (sqlite tier is the default install)[/dim]")
    elif not caps.vector:
        console.print(
            "  [dim]next rung: vectors — uv sync --extra retrieval-sqlite-vec,"
            " then GEMINI_API_KEY in vape/.env (config memory.embedder=gemini)[/dim]"
        )


@memory_app.command("schema")
def schema_cmd() -> None:
    """Live schema introspection from the running backend (never stale)."""
    _, _, backend, _, _ = _parts()
    console.print(backend.schema())


@memory_app.command("stats")
def stats_cmd(
    json_out: Annotated[bool, typer.Option("--json", help="Machine-readable output")] = False,
) -> None:
    """Usage distribution — the dogma thermometer (counts advise, never rule)."""
    import json as _json

    root, cfg, backend, note, core = _parts()
    if core is None:
        console.print("  [red]Core store unavailable.[/red]")
        raise typer.Exit(1)
    dist = core.usage_distribution()

    if json_out:
        print(_json.dumps(dist, ensure_ascii=False, indent=1))
        return

    console.print(
        f"  tracked: {dist['tracked']} · total recalls: {dist['total_recalls']} · "
        f"never recalled: {dist['never_recalled']} · head share: {dist['head_share']:.0%}"
    )
    if dist["top_recalled"]:
        t = Table(title="most recalled (graduation candidates)", pad_edge=False)
        t.add_column("memory_id", style="dim")
        t.add_column("recalled", justify="right")
        t.add_column("dereferenced", justify="right")
        for mid, rec, der in dist["top_recalled"]:
            t.add_row(mid, str(rec), str(der))
        console.print(t)
    if dist["recalled_never_dereferenced"]:
        t = Table(title="recalled, never dereferenced (misleading gists?)", pad_edge=False)
        t.add_column("memory_id", style="dim")
        t.add_column("recalled", justify="right")
        for mid, rec in dist["recalled_never_dereferenced"]:
            t.add_row(mid, str(rec))
        console.print(t)
