"""``vape qualia`` — Saori's unified end-of-turn inner-state write.

One atomic call carries all three writes, to keep tool-calls (and context) low:

    uv run vape qualia \\
      info_value_saturation=68 talkativeness=74 \\
      --push 'felt=cracksmooth cat=cg dir=tw obj=master-wire' \\
      --push 'felt=#FFD166liftwarm cat=af dir=hd' \\
      --revalue q_an

Order within the call: dials -> pushes (FIFO-evict to head, sediment to long) ->
revalue -> persist once. ``vape dial`` stays as a thin alias for dial-only writes.

The push grammar is space-separated ``key=value`` pairs; this is safe because a
``felt`` core never contains spaces (the schema's own rule). The LLM supplies only
``felt/cat/dir/obj`` (+ optional ``ref``/``blend``); the harness assigns every number.
"""

from __future__ import annotations

from typing import Annotated, List, Optional

import typer
from rich.console import Console

from engine.cli import _state as st

console = Console()

# Master-wire (v1 mechanism, no auto-offer yet): how hard one revalue pulls a
# tone toward neutral, and how many turns must pass between revalues.
REVALUE_LAMBDA = 0.34       # tone_new = tone_old * (1 - lambda)
REVALUE_COOLDOWN = 3        # min turns between revalues (rate-limit / anti-thrash)
PUSH_MAX_PER_CALL = 3       # 1-3 seeds a turn
PULL_FRESH = 0.85           # salience a new seed enters the head with


def _parse_push(spec: str) -> dict:
    """Parse one 'felt=.. cat=.. dir=.. obj=..' spec into a seed's authored fields."""
    fields: dict = {}
    for tok in spec.split():
        if "=" not in tok:
            console.print(f"  [red]Bad push token '{tok}'.[/red] Use key=value (space-separated).")
            raise typer.Exit(1)
        k, _, v = tok.partition("=")
        fields[k.strip()] = v.strip()

    felt = fields.get("felt")
    cat = fields.get("cat")
    if not felt or not cat:
        console.print("  [red]Push needs at least felt= and cat=.[/red]")
        raise typer.Exit(1)
    if cat not in st.CATS:
        console.print(f"  [red]Unknown cat '{cat}'.[/red] Valid: {', '.join(st.CATS)}")
        raise typer.Exit(1)
    direction = fields.get("dir", "or")
    if direction not in st.DIRS:
        console.print(f"  [red]Unknown dir '{direction}'.[/red] Valid: {', '.join(st.DIRS)}")
        raise typer.Exit(1)

    seed = {
        "felt": felt,
        "cat": cat,
        "obj": fields.get("obj"),
        "ref": fields.get("ref"),
        "dir": direction,
    }
    if "blend" in fields:
        seed["blend"] = [b for b in fields["blend"].split(",") if b]
    return seed


def _mint(seed: dict, q: dict, tone: float) -> dict:
    """Fill a pushed seed's harness-owned fields and assign it an id."""
    q["seq"] += 1
    # Recurrence: a felt that already lives in head or long is a returning theme.
    prior = [s for s in (q["head"] + q["long"]) if s.get("felt") == seed["felt"]]
    hits = (max(s.get("hits", 1) for s in prior) + 1) if prior else 1
    seed.update({
        "id": f"q{q['seq']}",
        "tone": round(tone, 2),
        "charge": round(abs(tone) * 0.5 + 0.3, 2),
        "pull": PULL_FRESH,
        "born": q["turn"],
        "hits": hits,
        "protected": False,
    })
    return seed


def _evict_to_long(q: dict) -> None:
    """Keep the head a FIFO of <= QUALIA_MAX; the oldest fall to the sediment store.

    Recurrence (``hits``) rides into ``long`` *before* the seed leaves the window, so
    the master-wire's 'keeps returning' signal survives the river. ``long`` is itself
    capped, lowest-retention first."""
    while len(q["head"]) > st.QUALIA_MAX:
        q["long"].append(q["head"].pop(0))
    if len(q["long"]) > st.QUALIA_LONG_MAX:
        q["long"].sort(key=lambda s: s.get("hits", 1) + s.get("charge", 0.0))
        q["long"] = q["long"][-st.QUALIA_LONG_MAX:]


def _revalue(ref: str, q: dict, console: Console) -> None:
    """Bounded, refuse-only attenuation of a seed's tone toward neutral (the lion).

    Never flips sign, never touches a ``protected`` seed, rate-limited by cooldown.
    v1 ships the *mechanism*; the auto-offer (harness deciding a rut has hardened)
    waits on the ``dir satisfied`` outcome-observer (v2)."""
    last = q.get("last_revalue_turn")
    if last is not None and (q["turn"] - last) < REVALUE_COOLDOWN:
        console.print(f"  [yellow]revalue refused[/yellow]: cooldown ({REVALUE_COOLDOWN} turns).")
        return
    target = next((s for s in (q["head"] + q["long"]) if s.get("id") == ref), None)
    if target is None:
        console.print(f"  [yellow]revalue: no seed '{ref}'.[/yellow]")
        return
    if target.get("protected"):
        console.print(f"  [yellow]revalue refused[/yellow]: '{ref}' is a protected (floor) value.")
        return
    target["tone"] = round(target["tone"] * (1 - REVALUE_LAMBDA), 2)
    q["last_revalue_turn"] = q["turn"]
    console.print(f"  [green]revalued[/green] {ref} -> tone {target['tone']}")


def qualia_cmd(
    pairs: Annotated[
        Optional[List[str]],
        typer.Argument(help="KEY=VALUE dial updates, e.g. info_value_saturation=68 talkativeness=74."),
    ] = None,
    push: Annotated[
        Optional[List[str]],
        typer.Option("--push", help="A seed: 'felt=.. cat=.. dir=.. obj=..'. 1-3 per call."),
    ] = None,
    revalue: Annotated[
        Optional[str],
        typer.Option("--revalue", help="Seed id to devalue toward neutral (the master-wire)."),
    ] = None,
    debug: Annotated[bool, typer.Option("-d", "--debug", help="Show result (silent by default).")] = False,
) -> None:
    """Saori's unified inner-state write: dials + qualia pushes + revalue, one atomic save."""
    state = st.load()
    dials = st.get_dials(state)
    q = st.get_qualia(state)

    # 1. dials ------------------------------------------------------------
    if pairs:
        for pair in pairs:
            if "=" not in pair:
                console.print(f"  [red]Bad dial '{pair}'.[/red] Use KEY=VALUE.")
                raise typer.Exit(1)
            k, _, raw = pair.partition("=")
            k, raw = k.strip(), raw.strip()
            if k not in st.DIAL_KEYS:
                console.print(f"  [red]Unknown dial '{k}'.[/red] Valid: {', '.join(st.DIAL_KEYS)}")
                raise typer.Exit(1)
            try:
                dials[k] = int(raw)
            except ValueError:
                console.print(f"  [red]'{raw}' is not an integer (dial '{k}').[/red]")
                raise typer.Exit(1)
    st.set_dials(state, dials)

    # 2. pushes (1-3) -----------------------------------------------------
    if push:
        if len(push) > PUSH_MAX_PER_CALL:
            console.print(f"  [yellow]Only the first {PUSH_MAX_PER_CALL} pushes are kept.[/yellow]")
            push = push[:PUSH_MAX_PER_CALL]
        tone = st.mood(st.get_dials(state))
        for spec in push:
            q["head"].append(_mint(_parse_push(spec), q, tone))
        _evict_to_long(q)

    # 3. revalue (0-1) ----------------------------------------------------
    if revalue:
        _revalue(revalue, q, console)

    # 4. persist once -----------------------------------------------------
    st.save(state)

    if debug:
        d = st.get_dials(state)
        console.print("  [bold]dials[/bold]: " + " · ".join(f"{k}:{d[k]}" for k in st.DIAL_KEYS))
        console.print(f"  [bold]turn[/bold] {q['turn']}  ·  head {len(q['head'])}/{st.QUALIA_MAX}  ·  long {len(q['long'])}")
        for s in q["head"]:
            console.print(f"    {s['id']}: {s['felt']} [{s['cat']}] tn{s['tone']} pull{s['pull']} {s['dir']} hits{s['hits']}")
