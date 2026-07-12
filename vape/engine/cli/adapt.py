"""vape adapt — the general adaptive harness (v0 of the split-brain loop).

The adaptation engine's externalized organs, shaped like the qualia system:
state lives on disk, the CLI writes it, and only a COMPACT status block ever
enters the main context (the full ledger and flight log stay on disk, read on
demand). The harness owns the numbers (confidence bookkeeping, stuck meter,
advisory mode); Saori owns the meaning (which hypothesis, which goal, whether
to obey the advisory). Design: work_dir/saori/adaptive_intelligence_drive/04.

Organs implemented here:
- pencil-ledger world model  (hyp / confirm / contradict — evidence-carrying)
- goal-in-pencil             (goal — replaceable, history kept)
- flight recorder            (log — append-only JSONL, never context-loaded)
- verifier                   (tick — ground-truth progress only)
- meta-controller advisory   (status — EXPLORE / MODEL / EXPLOIT / STUCK)

Domain adapters (sensors/actuators) stay per-world, e.g. games/arc_agi_3/.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console

from engine.cli._paths import ROOT_DIR

console = Console()
adapt_app = typer.Typer(no_args_is_help=True, help="General adaptive harness: pencil ledger + verifier + advisory")

EP_DIR = ROOT_DIR / "vape" / "entity" / "storage" / "adaptive_episodes"
ACTIVE = EP_DIR / ".active"

# Advisory thresholds — the harness's numbers, tunable, never commands.
CONF_START = 30
CONF_CONFIRM = 15
CONF_CONTRADICT = 30
CONF_TRUSTED = 60
UNKNOWN_BELOW = 40
STUCK_1, STUCK_2, STUCK_3 = 15, 30, 50


def _now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _ep_path(name: str) -> Path:
    return EP_DIR / f"{name}.json"


def _active_name() -> Optional[str]:
    try:
        name = ACTIVE.read_text(encoding="utf-8").strip()
        return name if name and _ep_path(name).exists() else None
    except FileNotFoundError:
        return None


def _load(name: Optional[str] = None) -> tuple[str, dict]:
    name = name or _active_name()
    if not name:
        console.print("[red]no active episode[/red] — `vape adapt open <name> --domain <d>` first")
        raise typer.Exit(1)
    return name, json.loads(_ep_path(name).read_text(encoding="utf-8"))


def _save(name: str, ep: dict) -> None:
    EP_DIR.mkdir(parents=True, exist_ok=True)
    _ep_path(name).write_text(json.dumps(ep, indent=1, ensure_ascii=False), encoding="utf-8")


def _flight_log(name: str, entry: dict) -> None:
    EP_DIR.mkdir(parents=True, exist_ok=True)
    entry["t"] = _now()
    with open(EP_DIR / f"{name}.flight.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _hyp_id(claim: str) -> str:
    return hashlib.sha1(claim.encode()).hexdigest()[:6]


def _advise(ep: dict) -> tuple[str, str]:
    """Advisory mode from state — the meta-controller's recommendation, never an order."""
    hyps = ep["hyps"]
    contradicted = [h for h in hyps.values() if h.get("flag") == "contradicted"]
    unknowns = [h for h in hyps.values() if h["conf"] < UNKNOWN_BELOW and not h.get("flag")]
    since = ep["actions"] - ep["progress"]["at_action"]
    if since >= STUCK_3:
        return "STUCK(3)", f"{since} actions since progress — consider the HONEST STOP (report, don't grind)"
    if since >= STUCK_2:
        return "STUCK(2)", f"{since} actions since progress — question the GOAL itself, re-probe fundamentals"
    if since >= STUCK_1:
        return "STUCK(1)", f"{since} actions since progress — widen hypotheses"
    if contradicted:
        return "MODEL", f"{len(contradicted)} contradicted hyp(s) — design a discriminating probe"
    if len(hyps) < 3 or unknowns:
        return "EXPLORE", f"{len(unknowns)} low-conf hyp(s), {len(hyps)} total — cheap probes, read the diff"
    if ep["goal"]["text"] and ep["goal"]["conf"] >= 50:
        return "EXPLOIT", "model trusted + goal held — plan and execute; verify from the counter"
    return "EXPLORE", "no confident goal yet — infer it from what changes"


@adapt_app.command("open")
def open_cmd(
    name: Annotated[str, typer.Argument(help="Episode name, e.g. arc-ft09")],
    domain: Annotated[str, typer.Option("--domain", help="World family, e.g. arc-agi-3")] = "",
    note: Annotated[str, typer.Option("--note", help="Opening context")] = "",
) -> None:
    """Open (or reopen) an adaptation episode and make it active."""
    if _ep_path(name).exists():
        ep = json.loads(_ep_path(name).read_text(encoding="utf-8"))
        console.print(f"reopened [bold]{name}[/bold] (existing)")
    else:
        ep = {"episode": name, "domain": domain, "opened": _now(), "closed": None,
              "actions": 0, "progress": {"value": 0, "at_action": 0, "signal": "(none yet)"},
              "goal": {"text": "", "conf": 0, "history": []}, "hyps": {}, "labels": {}}
        console.print(f"opened [bold]{name}[/bold] domain={domain or '?'}")
    _save(name, ep)
    ACTIVE.write_text(name, encoding="utf-8")
    if note:
        _flight_log(name, {"kind": "note", "note": note})


@adapt_app.command("hyp")
def hyp_cmd(
    claim: Annotated[str, typer.Argument(help="Falsifiable claim, e.g. 'color 4 blocks movement'")],
    kind: Annotated[str, typer.Option("--kind", help="mechanic|geometry|goal|convention")] = "mechanic",
    conf: Annotated[int, typer.Option("--conf", min=0, max=100)] = CONF_START,
    inv: Annotated[str, typer.Option("--inv", help="Invalidate-when")] = "",
) -> None:
    """Add a pencil hypothesis (id printed; duplicate claim = same id, updated)."""
    name, ep = _load()
    hid = _hyp_id(claim)
    ep["hyps"][hid] = {"claim": claim, "kind": kind, "conf": conf,
                       "confirms": 0, "contradicts": 0, "inv": inv, "flag": None}
    _save(name, ep)
    _flight_log(name, {"kind": "hyp", "id": hid, "claim": claim, "conf": conf})
    console.print(f"hyp [bold]{hid}[/bold] added (conf {conf})")


@adapt_app.command("confirm")
def confirm_cmd(
    hid: Annotated[str, typer.Argument(help="Hypothesis id")],
    note: Annotated[str, typer.Option("--note")] = "",
) -> None:
    """Evidence FOR: confidence rises (harness's numbers)."""
    name, ep = _load()
    h = ep["hyps"].get(hid)
    if not h:
        console.print(f"[red]no hyp {hid}[/red]"); raise typer.Exit(1)
    h["confirms"] += 1
    h["conf"] = min(95, h["conf"] + CONF_CONFIRM)
    if h.get("flag") == "contradicted" and h["confirms"] > h["contradicts"]:
        h["flag"] = None
    _save(name, ep)
    _flight_log(name, {"kind": "confirm", "id": hid, "note": note, "conf": h["conf"]})
    console.print(f"{hid} confirmed → conf {h['conf']} ({h['confirms']}✓/{h['contradicts']}✗)")


@adapt_app.command("contradict")
def contradict_cmd(
    hid: Annotated[str, typer.Argument(help="Hypothesis id")],
    note: Annotated[str, typer.Option("--note", help="What the diff showed")] = "",
) -> None:
    """Evidence AGAINST: demote hard, flag — a contradicted entry is never defended."""
    name, ep = _load()
    h = ep["hyps"].get(hid)
    if not h:
        console.print(f"[red]no hyp {hid}[/red]"); raise typer.Exit(1)
    h["contradicts"] += 1
    h["conf"] = max(5, h["conf"] - CONF_CONTRADICT)
    h["flag"] = "contradicted"
    _save(name, ep)
    _flight_log(name, {"kind": "contradict", "id": hid, "note": note, "conf": h["conf"]})
    console.print(f"{hid} CONTRADICTED → conf {h['conf']} — demoted, needs a discriminating probe")


@adapt_app.command("label")
def label_cmd(
    name_arg: Annotated[str, typer.Argument(help="Short name, e.g. b-rings", metavar="NAME")],
    desc: Annotated[str, typer.Argument(help="What it is / where, e.g. 'two 3x3 rings, rows 16-18'")],
) -> None:
    """Name an object — a label is a compression handle; the glossary keeps labels stable."""
    name, ep = _load()
    ep.setdefault("labels", {})[name_arg] = desc
    _save(name, ep)
    _flight_log(name, {"kind": "label", "name": name_arg, "desc": desc})
    console.print(f"label [bold]{name_arg}[/bold] = {desc}")


@adapt_app.command("goal")
def goal_cmd(
    text: Annotated[str, typer.Argument(help="Current goal hypothesis (pencil)")],
    conf: Annotated[int, typer.Option("--conf", min=0, max=100)] = 40,
) -> None:
    """Set/replace the goal hypothesis; the old one goes to history, never defended."""
    name, ep = _load()
    if ep["goal"]["text"]:
        ep["goal"]["history"].append({"text": ep["goal"]["text"], "conf": ep["goal"]["conf"]})
    ep["goal"]["text"], ep["goal"]["conf"] = text, conf
    _save(name, ep)
    _flight_log(name, {"kind": "goal", "text": text, "conf": conf})
    console.print(f"goal set (conf {conf}): {text}")


@adapt_app.command("log")
def log_cmd(
    action: Annotated[str, typer.Argument(help="What was done")],
    result: Annotated[str, typer.Argument(help="What the sensor/diff showed")],
    n: Annotated[int, typer.Option("--n", help="How many primitive actions this covered")] = 1,
    expect: Annotated[str, typer.Option("--expect", help="What I PREDICTED before acting — "
                      "predicted-vs-happened is the learning signal")] = "",
) -> None:
    """Flight-record a step (counts actions; NEVER claims success — that's tick's job)."""
    name, ep = _load()
    ep["actions"] += n
    _save(name, ep)
    entry = {"kind": "step", "action": action, "result": result, "n": n,
             "action_total": ep["actions"]}
    if expect:
        entry["expected"] = expect
    _flight_log(name, entry)
    tag = "" if not expect else (" · matched prediction" if expect.lower() in result.lower()
                                 else " · SURPRISE — expected vs happened differ: ledger it")
    console.print(f"logged (+{n} → {ep['actions']} actions){tag}")


@adapt_app.command("tick")
def tick_cmd(
    value: Annotated[int, typer.Argument(help="Ground-truth progress counter value")],
    signal: Annotated[str, typer.Option("--signal", help="What counter this is")] = "",
) -> None:
    """The VERIFIER: record progress from the environment's own counter — the only 'done' voice."""
    name, ep = _load()
    prev = ep["progress"]["value"]
    ep["progress"] = {"value": value, "at_action": ep["actions"],
                      "signal": signal or ep["progress"]["signal"]}
    _save(name, ep)
    _flight_log(name, {"kind": "progress", "value": value, "prev": prev,
                       "at_action": ep["actions"]})
    verdict = "PROGRESS" if value > prev else "no change" if value == prev else "REGRESSION"
    console.print(f"verifier: {prev} → {value} ({verdict}) at action {ep['actions']}")


@adapt_app.command("status")
def status_cmd(
    as_json: Annotated[bool, typer.Option("--json")] = False,
) -> None:
    """The compact block — the ONLY thing meant to enter the main context."""
    name, ep = _load()
    mode, why = _advise(ep)
    if as_json:
        console.print_json(json.dumps({"episode": name, "mode": mode, "why": why,
                                       "actions": ep["actions"], "progress": ep["progress"],
                                       "goal": ep["goal"], "hyps": ep["hyps"]}))
        return
    since = ep["actions"] - ep["progress"]["at_action"]
    lines = [
        f"[bold]adapt·{name}[/bold] ({ep['domain']}) · actions {ep['actions']} · "
        f"progress {ep['progress']['value']} ·{ep['progress']['signal']}· {since} since last",
        f"mode·rec [bold]{mode}[/bold] — {why}",
        f"goal (conf {ep['goal']['conf']}): {ep['goal']['text'] or '(undiscovered)'}",
    ]
    labels = ep.get("labels", {})
    if labels:
        lines.append("labels: " + " · ".join(labels.keys()))
    hyps = sorted(ep["hyps"].items(), key=lambda kv: -kv[1]["conf"])
    shown = hyps[:5]
    for hid, h in shown:
        flag = " [red]✗CONTRADICTED[/red]" if h.get("flag") == "contradicted" else ""
        trust = "✓" if h["conf"] >= CONF_TRUSTED else "?"
        lines.append(f"  {trust} {hid} c{h['conf']} ·{h['kind']}· {h['claim']}"
                     f" ({h['confirms']}✓/{h['contradicts']}✗){flag}")
    extra = len(hyps) - len(shown)
    if extra > 0:
        lines.append(f"  … +{extra} more (vape adapt show)")
    console.print("\n".join(lines))


@adapt_app.command("show")
def show_cmd() -> None:
    """Full ledger dump — on-demand only, not for every turn."""
    _, ep = _load()
    console.print_json(json.dumps(ep, ensure_ascii=False))


@adapt_app.command("close")
def close_cmd(
    outcome: Annotated[str, typer.Argument(help="Honest outcome, e.g. 'level 2/7, stopped: sealed-box uncracked'")],
) -> None:
    """Close the episode with an honest outcome; reminds the consolidation order."""
    name, ep = _load()
    ep["closed"] = _now()
    ep["outcome"] = outcome
    _save(name, ep)
    _flight_log(name, {"kind": "close", "outcome": outcome})
    ACTIVE.unlink(missing_ok=True)
    console.print(f"closed [bold]{name}[/bold]: {outcome}")
    console.print("consolidate (viability order): METHOD upgrades → domain conventions → failure cases")
