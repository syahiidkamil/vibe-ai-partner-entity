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
    """The full tier report: configured vs actual, the ladder, staleness,
    usage skew, and the capture-coverage tripwires."""
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

    _ladder(root)
    _freshness(root, core)
    _skew(core)
    _coverage(root)


def _ladder(root) -> None:
    """Every rung, probed not assumed."""
    import os
    import shutil as _shutil
    from importlib.metadata import entry_points

    from engine.memory.factory import PLACEHOLDER_KEYS, load_env

    load_env(root)
    installed = {ep.name for ep in entry_points(group="vibe.retrieval.providers")}

    def probe_vec() -> bool:
        try:
            import sqlite_vec  # noqa: F401
            return True
        except ImportError:
            return False

    def probe_pg() -> str:
        url = os.environ.get("DATABASE_URL", "")
        if not url:
            return "DATABASE_URL not set"
        try:
            import psycopg
            with psycopg.connect(url, connect_timeout=3):
                return "reachable"
        except ImportError:
            return "psycopg not installed"
        except Exception as e:
            return f"unreachable ({str(e)[:40].strip()})"

    key = os.environ.get("GEMINI_API_KEY", "") not in PLACEHOLDER_KEYS
    qmd = _shutil.which("qmd")

    console.print("  the ladder:")
    console.print(f"    files floor      always available")
    console.print(f"    sqlite fts       {'installed' if 'sqlite' in installed else 'uv sync --extra retrieval-sqlite'}")
    console.print(
        f"    sqlite vectors   sqlite-vec {'ok' if probe_vec() else 'missing (uv sync --extra retrieval-sqlite-vec)'}"
        f" · GEMINI_API_KEY {'ok' if key else 'missing (vape/.env)'}")
    console.print(
        f"    pgvector         {'installed' if 'pgvector' in installed else 'uv sync --extra retrieval-pgvector'}"
        f" · postgres {probe_pg()}")
    console.print(
        f"    qmd              {'binary ' + qmd if qmd else 'binary not on PATH (github.com/tobi/qmd, Node >= 22)'}")


def _freshness(root, core) -> None:
    if core is None:
        return
    from engine.memory import derive
    from engine.memory.interface import rel_posix

    last = core.meta_get("last_sweep_at") or "never"
    manifest = core.manifest_all()
    pending = 0
    for path in derive.all_sources(root):
        try:
            st = path.stat()
        except OSError:
            continue
        row = manifest.get(rel_posix(path, root))
        if row is None or row.mtime != st.st_mtime or row.size != st.st_size:
            pending += 1
    console.print(
        f"  freshness: last sweep {last} · queue {core.queue_depth()}"
        f" · files pending sweep {pending}")


def _skew(core) -> None:
    if core is None:
        return
    d = core.usage_distribution()
    console.print(
        f"  usage skew: tracked {d['tracked']} · head share {d['head_share']:.0%}"
        f" · never recalled {d['never_recalled']}"
        f" · recalled-never-dereferenced {len(d['recalled_never_dereferenced'])}")


def _coverage(root) -> None:
    """Capture tripwires (doc 12 C8): a day whose streams disagree is a day
    something silently failed to capture — today-me found one the hard way."""
    storage = root / "vape" / "entity" / "storage"
    if not storage.is_dir():
        return
    days: dict[str, set[str]] = {}
    for f in storage.glob("2*/*/*.toon"):
        parts = f.stem.rsplit("_", 1)
        if len(parts) == 2:
            days.setdefault(parts[0], set()).add(parts[1])
    gaps = []
    for day, streams in sorted(days.items()):
        if "chats" not in streams and streams & {"qualia", "bookmarks"}:
            gaps.append(f"{day} has {'+'.join(sorted(streams))} but NO chats")
    if gaps:
        console.print("  [yellow]capture gaps:[/yellow]")
        for g in gaps[:5]:
            console.print(f"    [yellow]{g}[/yellow]")
    else:
        console.print("  capture coverage: no stream gaps")


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
