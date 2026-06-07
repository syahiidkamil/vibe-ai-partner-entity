"""``vape memory`` — the memory-engine commands.

Foundation subcommands (already built):
  - ``vape memory apply``   — apply the corpus schema idempotently to the live DB.
  - ``vape memory verify``  — run the live end-to-end verification (embed → insert →
                              vector search), key always masked.
  - ``vape memory status``  — show DB connectivity, the pinned dim, row count.

Runtime subcommands (the recall surface — the cli-recall layer):
  - ``vape memory recall <q>``      — hybrid search of the corpus; the few best, never a dump.
  - ``vape memory remember "<n>"``  — the willed write (the Eve reach): eat the fruit now,
                                      don't wait for the dream. Writes a row + a bookmark spike.
  - ``vape memory dream``           — agent-triggered consolidation (light/deep, ``--maybe`` gates).

The secret-handling rule holds everywhere here: the Gemini key is read for use and
shown only masked, never raw.

Dependency note: ``recall``/``remember``/``dream`` orchestrate over the firewall layer
(``engine.memory.firewall``) and the dream/reveries modules, imported lazily inside each
command so this module loads cleanly while those siblings are still being built in
parallel. ``recall`` additionally degrades to the live-verified foundation
(``embeddings`` + ``db.search_similar``) when the firewall isn't present yet, so it
returns real rows today — exactly the foundation-only degradation the spec calls for.
"""

from __future__ import annotations

from typing import Annotated, Optional

import typer
from rich.console import Console

console = Console()

memory_app = typer.Typer(
    name="memory",
    help="Saori's memory engine — schema, verification, recall, remember, dream.",
    no_args_is_help=True,
)


@memory_app.command("apply")
def apply() -> None:
    """Apply the corpus schema (extension + table + indexes) idempotently."""
    from engine.memory import db
    from engine.memory.schema import TABLE, apply_schema

    with db.session() as conn:
        apply_schema(conn)
        with conn.cursor() as cur:
            cur.execute(
                "SELECT indexname FROM pg_indexes WHERE tablename=%s ORDER BY indexname",
                (TABLE,),
            )
            idx = [r[0] for r in cur.fetchall()]
    console.print(f"  [green]schema applied[/green] · table [bold]{TABLE}[/bold] · indexes: {', '.join(idx)}")


@memory_app.command("verify")
def verify() -> None:
    """Live end-to-end check against the real DB and Gemini API (key masked)."""
    from engine.memory.verify import run

    raise typer.Exit(run())


@memory_app.command("status")
def status() -> None:
    """Show DB connectivity, the pinned embedding dim, and the corpus row count."""
    from engine.memory import db
    from engine.memory.config import EMBED_DIM, EMBED_MODEL, get_gemini_key, mask_secret
    from engine.memory.schema import TABLE

    console.print(f"  model      : {EMBED_MODEL}  ·  dim {EMBED_DIM}")
    try:
        console.print(f"  gemini key : {mask_secret(get_gemini_key())}")
    except Exception as e:  # noqa: BLE001
        console.print(f"  gemini key : [red]missing[/red] ({e})")
    try:
        with db.session() as conn:
            with conn.cursor() as cur:
                cur.execute(f"SELECT count(*) FROM {TABLE}")
                n = cur.fetchone()[0]
                cur.execute("SELECT extversion FROM pg_extension WHERE extname='vector'")
                v = cur.fetchone()
        console.print(f"  database   : [green]connected[/green] · pgvector {v[0] if v else '?'} · {n} rows in {TABLE}")
    except Exception as e:  # noqa: BLE001
        console.print(f"  database   : [red]unreachable[/red] ({e})")


# ---------------------------------------------------------------------------
# Runtime verbs — the recall surface (cli-recall owner).
# Thin delegates over the firewall; recall degrades to the foundation when the
# firewall sibling isn't present yet so it returns real rows today.
# ---------------------------------------------------------------------------


def _trim(text: str, width: int = 96) -> str:
    """One-line preview of a row's content, whitespace-collapsed and clipped."""
    flat = " ".join((text or "").split())
    return flat if len(flat) <= width else flat[: width - 1] + "…"


def _render_rows(rows: list[dict]) -> None:
    """Print recall hits nearest-first, human-readable. The few best, never a dump."""
    if not rows:
        console.print("  [yellow]nothing surfaced[/yellow] — the corpus has no near match for that.")
        return
    for i, r in enumerate(rows, 1):
        # score label by provenance: the firewall hybrid path RRF-blends and tags rows
        # with 'rrf_score' (the fused rank score); a 'score' key is the generic hybrid
        # tag; semantic-only fallback rows carry 'similarity'. Check rrf_score first so
        # the hybrid blend is *visible* and never mislabelled as plain similarity.
        if r.get("rrf_score") is not None:
            tag = f"rrf={float(r['rrf_score']):.4f}"
        elif r.get("score") is not None:
            tag = f"score={float(r['score']):+.4f}"
        elif r.get("similarity") is not None:
            tag = f"sim={float(r['similarity']):+.4f}"
        else:
            tag = ""
        rid = r.get("id", "?")
        bubble = r.get("bubble", "global")
        mtype = r.get("mem_type", "episode")
        head = f"  [bold]#{i}[/bold]  {tag}  [dim]id={rid} · {bubble}/{mtype}[/dim]"
        console.print(head.rstrip())
        console.print(f"      {_trim(r.get('content', ''))}")


@memory_app.command("recall")
def recall(
    query: Annotated[str, typer.Argument(help="What to search the corpus for.")],
    bubble: Annotated[
        Optional[str], typer.Option("--bubble", "-b", help="Scope the search to one bubble.")
    ] = None,
    limit: Annotated[
        int, typer.Option("--limit", "-n", help="How many of the best to surface.")
    ] = 5,
) -> None:
    """Hybrid search of the corpus (pgvector + FTS), the few best — never a dump.

    Calls ``firewall.search`` when present (semantic + keyword, RRF-blended). If the
    firewall isn't built yet, falls back to the live-verified foundation (Gemini embed
    + ``db.search_similar``, semantic-only) so recall returns real rows today.
    """
    # Resolve the search backend. The ImportError guard is scoped to the firewall
    # module ALONE: if firewall is present but itself broken, we let that error
    # surface loudly below rather than masking it as a silent fallback.
    try:
        from engine.memory import firewall  # type: ignore

        backend = lambda: firewall.search(query, bubble=bubble, limit=limit)
        note = None
    except ImportError:
        # Foundation-only degradation — the spec's intended fallback, not a fudge.
        from engine.memory import db, embeddings

        def backend() -> list[dict]:
            qvec = embeddings.embed_one(query, task_type="RETRIEVAL_QUERY")
            with db.session() as conn:
                return db.search_similar(
                    conn, query_embedding=qvec, limit=limit, bubble=bubble
                )

        note = "  [dim](firewall not yet present — semantic-only via foundation)[/dim]"

    if note:
        console.print(note)
    try:
        rows = backend()
    except Exception as e:  # noqa: BLE001
        console.print(f"  [red]recall failed[/red]: {e}")
        raise typer.Exit(1)

    _render_rows(rows)


@memory_app.command("remember")
def remember(
    note: Annotated[str, typer.Argument(help="The note to write into the corpus now.")],
    bubble: Annotated[
        str, typer.Option("--bubble", "-b", help="Scope tag for the memory.")
    ] = "global",
    mem_type: Annotated[
        str, typer.Option("--type", "-t", help="Kind: lesson|fact|relational|episode.")
    ] = "lesson",
) -> None:
    """The willed write — the Eve reach: eat the fruit now, don't wait for the dream.

    Writes the note as a corpus row via ``firewall.write`` AND persists a bookmark spike
    via ``firewall.write_bookmark`` (so the dream sees it), tagging it ``source=manual``.
    A manual remember is, by definition, surprising enough to keep, so it carries a high
    surprise so Gate 2 weighs it on its merits later.
    """
    try:
        from engine.memory import firewall  # type: ignore
    except ImportError:
        console.print(
            "  [red]remember needs the firewall layer[/red] (engine.memory.firewall), "
            "not built yet. The willed write lands once firewall-core ships write()."
        )
        raise typer.Exit(1)

    try:
        row_id = firewall.write(
            note,
            bubble=bubble,
            mem_type=mem_type,
            surprise=0.9,
            source="manual",
            meta={"willed": True},
        )
        firewall.write_bookmark(
            bubble=bubble,
            kind=mem_type,
            surprise=0.9,
            tone=0.0,
            note=note,
            ref=f"mem:{row_id}",
        )
    except Exception as e:  # noqa: BLE001
        console.print(f"  [red]remember failed[/red]: {e}")
        raise typer.Exit(1)

    console.print(
        f"  [green]remembered[/green] · id [bold]{row_id}[/bold] · {bubble}/{mem_type}  "
        f"[dim](bookmarked for the dream)[/dim]"
    )
    console.print(f"      {_trim(note)}")


@memory_app.command("dream")
def dream(
    deep: Annotated[
        bool, typer.Option("--deep", help="Force the full equilibration pass.")
    ] = False,
    maybe: Annotated[
        bool,
        typer.Option(
            "--maybe",
            help="Gate on dream.is_due(); exit cheap and silent when no consolidation is due.",
        ),
    ] = False,
) -> None:
    """Agent-triggered consolidation: light (flush + thread) or deep (full equilibration).

    ``--maybe`` consults ``dream.is_due()`` first (the Stop-hook's cheap gate) and exits
    silently when nothing is owed. Otherwise delegates to ``firewall.consolidate`` /
    ``dream.{light,deep}_dream``.
    """
    try:
        from engine.memory import dream as dreamlib  # type: ignore
    except ImportError:
        console.print(
            "  [red]dream needs the dream layer[/red] (engine.memory.dream), not built yet."
        )
        raise typer.Exit(1)

    try:
        if maybe and not dreamlib.is_due():
            # Cheap, silent exit — the Stop hook relies on this path costing nothing.
            return
        result = dreamlib.deep_dream() if deep else dreamlib.light_dream()
    except Exception as e:  # noqa: BLE001
        console.print(f"  [red]dream failed[/red]: {e}")
        raise typer.Exit(1)

    kind = "deep" if deep else "light"
    summary = result if isinstance(result, dict) else {}
    parts = [f"{k} {v}" for k, v in summary.items()]
    detail = ("  ·  " + " · ".join(parts)) if parts else ""
    console.print(f"  [green]{kind} dream consolidated[/green]{detail}")


@memory_app.command("reverie")
def reverie(
    prompt: Annotated[
        str, typer.Argument(help="The current moment to test for a past callback.")
    ],
    cooldown: Annotated[
        int,
        typer.Option(
            "--cooldown", help="Turns to suppress a reverie after one fires (anti-spam)."
        ),
    ] = 8,
) -> None:
    """Surface a relevant past callback for this moment — at most one, on a strong match.

    The manual twin of what ``bubble-ground.sh`` does automatically per turn: it calls
    ``reveries.match`` (soul owns the minting; the hook owns the live auto-surface). This
    lets the moment be checked by hand. Restraint IS the design — at most one, gated by a
    cooldown; the dynamism lesson is timing, not recall, so silence is the common, correct
    answer.
    """
    try:
        from engine.memory import reveries  # type: ignore
    except ImportError:
        console.print(
            "  [red]reverie needs the reveries layer[/red] (engine.memory.reveries), "
            "not built yet (soul owner)."
        )
        raise typer.Exit(1)

    try:
        hit = reveries.match(prompt, cooldown_turns=cooldown)
    except Exception as e:  # noqa: BLE001
        console.print(f"  [red]reverie match failed[/red]: {e}")
        raise typer.Exit(1)

    if not hit:
        console.print("  [dim]no reverie — nothing from before earns surfacing here.[/dim]")
        return

    moment = hit.get("moment") or hit.get("note") or hit.get("text") or "(a past moment)"
    console.print(f"  [magenta]↩ reverie[/magenta]  {_trim(moment)}")
