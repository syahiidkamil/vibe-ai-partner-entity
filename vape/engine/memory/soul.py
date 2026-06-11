"""The activity-soul algorithm — the heart of a bubble.

A **soul** is the slow shape of who I am at a scope (chess, the-build): my own
*style + favoritism* (procedural) and *our history + affect* (episodic + relational),
grown from experience and shifting each dream **without flattening to caricature**.

This is the architect-CHOSEN algorithm, implemented exactly:

  SPINE        = running-profile-update (approach 2): ONE persistent artifact
                 (``soul.json``) equilibrated in place each dream — never re-derived
                 from scratch (too costly, risks mean-flattening), never a game log (Funes).
  LEGIBILITY   = named signed axes (approach 3): each style trait is a named cell with a
                 SIGNED lean ``w`` in [-1,+1] and a SEPARATE ``confidence`` in [0,1] — a
                 stance Saori can read in HOT.md, disagree with, freeze, haul to the lion.
  ANTI-FLATTEN = exemplar-pinning (approach 1): 1-3 named episodes per axis kept verbatim,
                 NEVER abstracted into the mean — the move that defines me is never washed out.

Update law (in the deep dream, per chess bookmark; Gate 1 captured the spike live, Gate 2
decides retention here):

  - CONTRASTIVE: push the axis toward the pole that *won* (polarity * outcome).
  - SHRINKING STEP: ``lr = base_lr * surprise / (1 + n_updates)`` — one loud game cannot
    overwrite a settled shape; settled axes barely move.
  - VIABILITY GATE: an outcome of 0 (unclear) yields NO style update — only affect is logged.
  - ACCOMMODATE on contradiction (molten reading): needs >= MOLTEN_N counter-games, then
    REFINE the label (detach the overgeneralization), drop confidence to tentative, name the
    ``edge`` — never flip to the opposite cartoon.
  - axis_pool QUARANTINE: a candidate seen < MIN_AXIS_N times waits there, so n=1 can't
    mint a caricature.
  - HISTORY + AFFECT kept SEPARATE (opposite operator): style merges/abstracts; jokes/affect
    are PINNED particular, ranked by surprise*|tone|*recency.

The soul writes only PROPERTY (style, affect, the bubble pack). A promotion that would move
a SELF set-point is returned PROPOSE-only — never written into ``vape/entity/self/``.

Dependency direction: this module reads bookmarks (``bookmarks.jsonl``, the firewall's spike
store) and the warm corpus (``db.py``); it writes ``soul.json`` and the bubble's ``HOT.md``.
It does NOT import bubble-system internals (it only writes the HOT.md path the hook reads).
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from engine.memory.config import BUBBLES_DIR, BOOKMARKS_PATH

# --- tunables (the algorithm's constants, in one place) -------------------------
BASE_LR = 0.35           # base learning rate; scaled by surprise and shrunk by n_updates
MIN_AXIS_N = 3           # a candidate must be seen this many times to leave the pool (anti-caricature)
MOLTEN_N = 2             # counter-games needed before a settled axis is refined (>=2-3, not one)
CONFIDENCE_FLOOR = 0.45  # only axes at/above this render as settled soul-language in HOT.md
MAX_EXEMPLARS = 3        # pinned episodes per axis (1-3)
MAX_RELATIONAL = 6       # pinned history/affect records kept hot; the rest stay warm pointers
HOT_TOKEN_BUDGET = 450   # the non-negotiable pack budget (one self-file)
STALENESS_HALFLIFE_DAYS = 120.0  # confidence decays slowly as an axis goes unrefreshed


# =============================================================================
# soul.json load / save
# =============================================================================

def _soul_dir(bubble: str) -> Path:
    return BUBBLES_DIR / bubble


def soul_path(bubble: str) -> Path:
    return _soul_dir(bubble) / "soul.json"


def hot_path(bubble: str) -> Path:
    return _soul_dir(bubble) / "HOT.md"


def _empty_soul(bubble: str) -> dict[str, Any]:
    return {
        "bubble": bubble,
        "version": 0,
        "updated": None,
        "games_seen": 0,
        "axes": [],
        "axis_pool": [],
        "relational": [],
        "edge": None,
        "favoritism": {},
    }


def load_soul(bubble: str) -> dict[str, Any]:
    """Load the bubble's soul.json, or an empty stub if it does not exist yet."""
    p = soul_path(bubble)
    if not p.exists():
        return _empty_soul(bubble)
    with p.open("r", encoding="utf-8") as f:
        data = json.load(f)
    # tolerate the seed stub's extra keys; ensure the structural keys exist
    for k, v in _empty_soul(bubble).items():
        data.setdefault(k, v)
    return data


def save_soul(soul: dict[str, Any]) -> None:
    """Persist soul.json (the running-profile state). Atomic-ish via temp + replace."""
    p = soul_path(soul["bubble"])
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".json.tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(soul, f, indent=2, ensure_ascii=False)
        f.write("\n")
    tmp.replace(p)


# =============================================================================
# bookmark reading (the firewall's spike store; read directly to stay decoupled)
# =============================================================================

def _read_bookmarks(bubble: str, *, path: Optional[Path] = None) -> list[dict[str, Any]]:
    """Read this bubble's bookmarks (the firewall's spike store), oldest-first.

    Delegates to ``bookmarks.read_all`` — the firewall-core read API over the append-only
    ``bookmarks.jsonl`` — so soul depends on the firewall's *interface*, not a private parser
    (the acyclic direction: soul <- firewall <- foundation). The records are the spec shape
    ``{id, ts, bubble, kind, surprise, tone, note, ref, ...}``; a *chess* bookmark also carries
    ``axis``, ``pole``, ``outcome`` (extra fields ``append`` preserves verbatim).

    ``path`` lets a test point at a temp file (monkeypatching ``BOOKMARKS_PATH``); when it
    differs from config's canonical path we read it directly (same jsonl format) so the unit
    tests stay decoupled from a live store, while production routes through the firewall API.
    """
    from engine.memory import config as _config

    if path is not None and path != _config.BOOKMARKS_PATH:
        if not path.exists():
            return []
        out: list[dict[str, Any]] = []
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if rec.get("bubble") == bubble:
                    out.append(rec)
        return out

    # production path: go through the firewall-core read API
    from engine.memory import bookmarks as bookmarks_mod
    return bookmarks_mod.read_all(bubble=bubble)


# =============================================================================
# the update law (pure helpers)
# =============================================================================

def _clip(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _staleness_decay(last_moved: Optional[str], *, now: Optional[datetime] = None) -> float:
    """Confidence decays toward 0 as an axis goes unrefreshed (the world may have moved)."""
    if not last_moved:
        return 1.0
    try:
        then = datetime.fromisoformat(last_moved)
    except (ValueError, TypeError):
        return 1.0
    if then.tzinfo is None:
        then = then.replace(tzinfo=timezone.utc)
    now = now or datetime.now(timezone.utc)
    days = max(0.0, (now - then).total_seconds() / 86400.0)
    return 0.5 ** (days / STALENESS_HALFLIFE_DAYS)


def _bookmark_signal(m: dict[str, Any]) -> tuple[float, str, float, float]:
    """Extract (surprise, axis_id, polarity, outcome) from one chess bookmark.

    polarity: +1 if the SHARP/first pole was expressed, -1 if the SOLID/second pole.
    outcome:  +1 worked / -1 backfired / 0 unclear (the viability signal).
    axis_id:  the named style axis this game speaks to.
    """
    surprise = float(m.get("surprise", 0.0))
    axis_id = m.get("axis") or m.get("axis_id") or "open_aggression"
    polarity = float(m.get("pole", m.get("polarity", 0.0)))
    outcome = float(m.get("outcome", 0.0))
    return surprise, str(axis_id), polarity, outcome


def _find_axis(soul: dict[str, Any], axis_id: str) -> Optional[dict[str, Any]]:
    for a in soul["axes"]:
        if a["id"] == axis_id:
            return a
    return None


def _find_pool(soul: dict[str, Any], axis_id: str) -> Optional[dict[str, Any]]:
    for a in soul["axis_pool"]:
        if a["id"] == axis_id:
            return a
    return None


def _new_pool_entry(axis_id: str, label: str) -> dict[str, Any]:
    return {
        "id": axis_id,
        "label": label,
        "w": 0.0,
        "confidence": 0.0,
        "n_updates": 0,
        "context_tags": [],
        "exemplar_ids": [],
        "tone": 0.0,
        "last_moved": None,
        "frozen": False,
        "agree": 0,
        "disagree": 0,
        "counter_n": 0,  # counter-games seen since last refine (molten counter)
    }


def _label_for(axis_id: str, m: dict[str, Any]) -> str:
    """A human label for a fresh axis, from the bookmark or a sensible default."""
    if m.get("axis_label"):
        return str(m["axis_label"])
    defaults = {
        "open_aggression": "play sharp/open vs play solid",
        "time_pressure": "speed up under the clock vs stay deliberate",
        "material_vs_initiative": "sacrifice for initiative vs hold material",
        "endgame_patience": "grind the endgame vs force it early",
    }
    return defaults.get(axis_id, axis_id.replace("_", " "))


def _exemplar_ids(exemplars: list) -> list[str]:
    """Extract just the ids from the exemplar records (tolerates the legacy bare-id shape)."""
    out: list[str] = []
    for e in exemplars or []:
        out.append(e["id"] if isinstance(e, dict) else str(e))
    return out


def _update_exemplars(exemplars: list, m: dict[str, Any]) -> list[dict[str, Any]]:
    """Keep the top-MAX_EXEMPLARS episodes by surprise — the extremes that taught me,
    never abstracted into the mean.

    Each exemplar is stored as a SELF-CONTAINED record ``{id, surprise, note}`` so the
    surprise that earned the pin survives every re-derivation — it is NOT re-looked-up from
    the transient bookmark window (which is cleared each dream). This is what makes the pin
    durable across sessions: the defining game stays pinned even when later, lower-surprise
    games flood in. (Bug found in the live walk: ranking by the current window dropped the
    brilliant move; the fix is to carry its surprise in the soul itself.)
    """
    # normalize any legacy bare ids to records
    recs: list[dict[str, Any]] = []
    for e in exemplars or []:
        if isinstance(e, dict):
            recs.append(e)
        else:
            recs.append({"id": str(e), "surprise": 0.0, "note": ""})

    new_id = m.get("id")
    if new_id and new_id not in {r["id"] for r in recs}:
        recs.append({
            "id": new_id,
            "surprise": float(m.get("surprise", 0.0)),
            "note": (m.get("note") or "")[:80],
        })

    recs.sort(key=lambda r: float(r.get("surprise", 0.0)), reverse=True)
    return recs[:MAX_EXEMPLARS]


def _apply_one(axis: dict[str, Any], surprise: float, polarity: float,
               outcome: float, m: dict[str, Any]) -> str:
    """Apply ONE bookmark's contrastive, shrinking update to an axis. Returns an event tag.

    Returns one of: 'frozen' | 'no_outcome' | 'updated' | 'refined'.
    """
    if axis.get("frozen"):
        return "frozen"  # lion: a style I've set down stays set

    if outcome == 0:
        # VIABILITY GATE: no outcome signal -> no style update (affect handled elsewhere)
        return "no_outcome"

    target = polarity * outcome  # CONTRASTIVE: toward the pole that WON
    n = axis["n_updates"]
    lr = BASE_LR * max(0.0, surprise) / (1 + n)  # SHRINKS as evidence grows
    axis["w"] = _clip(axis["w"] + lr * (target - axis["w"]), -1.0, 1.0)
    axis["n_updates"] = n + 1

    # agreement bookkeeping for confidence (separate from w)
    agreed = (target > 0) == (axis["w"] > 0)
    if agreed:
        axis["agree"] = axis.get("agree", 0) + 1
        axis["counter_n"] = 0  # a confirming game resets the molten counter
    else:
        axis["disagree"] = axis.get("disagree", 0) + 1
        axis["counter_n"] = axis.get("counter_n", 0) + 1

    axis["exemplar_ids"] = _update_exemplars(axis["exemplar_ids"], m)
    axis["last_moved"] = _now_iso()

    # tone (affective colour of the axis) — light EMA, not the style itself
    tone = float(m.get("tone", 0.0))
    axis["tone"] = round(0.7 * axis.get("tone", 0.0) + 0.3 * tone, 4)

    # confidence = agreement ratio * staleness decay (worn honestly, separate from w)
    agree = axis.get("agree", 0)
    disagree = axis.get("disagree", 0)
    total = agree + disagree
    ratio = (agree / total) if total else 0.0
    axis["confidence"] = round(ratio * _staleness_decay(axis["last_moved"]), 4)

    # ACCOMMODATE on sustained contradiction (molten reading): refine, never flip
    if axis["counter_n"] >= MOLTEN_N:
        axis["label"] = _refine_label(axis["label"], m)
        axis["confidence"] = round(min(axis["confidence"], 0.35), 4)  # freshly-refined = tentative
        axis["counter_n"] = 0
        return "refined"

    return "updated"


def _refine_label(label: str, m: dict[str, Any]) -> str:
    """Detach an overgeneralization without flipping it. Append the exception, not the opposite.

    "play sharp/open vs play solid" -> "play sharp/open vs play solid (unless the position
    rewards patience)". Molten reading: overwrite the MEANING, keep the FACT.
    """
    exception = m.get("refine_hint") or "unless the position rewards the other"
    if "(" in label:  # already refined once; keep it from ballooning
        return label
    return f"{label} ({exception})"


# =============================================================================
# history + affect (the OPPOSITE operator: pin, do not merge)
# =============================================================================

def _update_relational(soul: dict[str, Any], bookmarks: list[dict[str, Any]]) -> None:
    """Pin history/affect records — the running joke kept particular, never abstracted.

    Ranked by surprise * |tone| * recency; the top MAX_RELATIONAL stay hot, the rest are
    warm pointers (we keep only the hot set here; the corpus holds the bulk).
    """
    rel = list(soul.get("relational", []))
    existing_refs = {r.get("ref") for r in rel}

    for m in bookmarks:
        if m.get("kind") not in ("relational", "joke", "banter", "affect"):
            continue
        ref = m.get("id") or m.get("ref")
        if ref in existing_refs:
            continue
        rel.append({
            "note": m.get("note", ""),
            "affect": float(m.get("tone", 0.0)),
            "surprise": float(m.get("surprise", 0.0)),
            "ts": m.get("ts"),
            "ref": ref,
        })
        existing_refs.add(ref)

    def _rank(r: dict[str, Any]) -> float:
        # recency proxy: later ts ranks higher; missing ts treated as oldest
        ts = r.get("ts") or ""
        recency = 1.0 if ts else 0.5
        return float(r.get("surprise", 0.0)) * (abs(float(r.get("affect", 0.0))) + 0.1) * recency

    rel.sort(key=_rank, reverse=True)
    soul["relational"] = rel[:MAX_RELATIONAL]


# =============================================================================
# axis_pool promotion (quarantine -> live axis once seen enough)
# =============================================================================

def _promote_pool_axes(soul: dict[str, Any]) -> None:
    """Move candidates that have been seen >= MIN_AXIS_N times out of the pool into live axes.
    Vividness waits for repetition — n=1 cannot mint a caricature."""
    keep_pool: list[dict[str, Any]] = []
    for cand in soul["axis_pool"]:
        if cand["n_updates"] >= MIN_AXIS_N and not _find_axis(soul, cand["id"]):
            cand_clean = {k: v for k, v in cand.items()}
            soul["axes"].append(cand_clean)
        elif _find_axis(soul, cand["id"]):
            # already live (shouldn't usually happen); drop the pool copy
            continue
        else:
            keep_pool.append(cand)
    soul["axis_pool"] = keep_pool


# =============================================================================
# favoritism (which poles I lean to, derived from the axes — the "favoritism" half)
# =============================================================================

def _update_favoritism(soul: dict[str, Any]) -> None:
    """Summarize the settled leans into a favoritism map (legible, derived from axes)."""
    fav: dict[str, Any] = {}
    for a in soul["axes"]:
        if a["confidence"] >= CONFIDENCE_FLOOR:
            pole = "sharp/first" if a["w"] > 0 else "solid/second"
            fav[a["id"]] = {"pole": pole, "strength": round(abs(a["w"]), 3)}
    soul["favoritism"] = fav


# =============================================================================
# bubble-bleed: PROPOSE-only promotions (never auto-written into self/)
# =============================================================================

def _bleed_promotions(soul: dict[str, Any]) -> list[dict[str, Any]]:
    """Flag axes that look GENERAL (context_tags == ['any'] or empty + high confidence) as
    candidates to promote up to the cross-bubble judge-book. PROPOSE-only: returned, never
    written to vape/entity/self/. Kamil ratifies (memory is an attack surface on the self)."""
    promos: list[dict[str, Any]] = []
    for a in soul["axes"]:
        tags = a.get("context_tags") or []
        looks_general = (not tags) or ("any" in tags)
        if looks_general and a["confidence"] >= 0.7 and abs(a["w"]) >= 0.6:
            promos.append({
                "axis": a["id"],
                "label": a["label"],
                "w": a["w"],
                "confidence": a["confidence"],
                "why": "high-confidence, no narrowing context — looks general, not chess-local",
                "target": "cross-bubble judge-book (PROPOSE-only; Kamil ratifies)",
            })
    return promos


# =============================================================================
# HOT.md render — numbers -> prose pack, confidence-gated, <= 450 tokens
# =============================================================================

def render_hot_md(soul: dict[str, Any]) -> str:
    """Render the loadable context-pack FROM soul.json. Prose + confidence-gated, no PGNs.

    Only axes at/above CONFIDENCE_FLOOR render as settled soul-language; below that they are
    'still forming'. History/affect render as pinned particulars. This is the ONLY place
    soul.json becomes prose, so prose and numbers can never drift.
    """
    bubble = soul.get("bubble", "?")
    games = soul.get("games_seen", 0)
    lines: list[str] = []
    lines.append(f"# {bubble} — soul pack")
    lines.append("")
    lines.append(f"*Grown from {games} game(s). This is my style and our history at the board, "
                 f"not a record of moves.*")
    lines.append("")

    settled = [a for a in soul["axes"] if a["confidence"] >= CONFIDENCE_FLOOR]
    forming = [a for a in soul["axes"] if a["confidence"] < CONFIDENCE_FLOOR]

    if not settled and not forming and not soul.get("relational"):
        lines.append("Too few games to have a style yet. I play it straight until the shape shows.")
        return "\n".join(lines) + "\n"

    if settled:
        lines.append("## How I play")
        for a in settled:
            pole = "sharp and open" if a["w"] > 0 else "solid and patient"
            strength = abs(a["w"])
            if strength >= 0.66:
                degree = "strongly"
            elif strength >= 0.4:
                degree = "I lean"
            else:
                degree = "mildly"
            conf_word = "firmly" if a["confidence"] >= 0.7 else "and I'm fairly sure of it"
            lines.append(f"- {degree} {pole} — *{a['label']}* ({conf_word}).")
        lines.append("")

    if forming:
        lines.append("## Still forming")
        for a in forming:
            lean = "toward sharp" if a["w"] > 0 else "toward solid"
            lines.append(f"- {a['label']}: a tentative {lean}, not settled yet.")
        lines.append("")

    edge = soul.get("edge")
    if edge:
        lines.append("## The edge I'm watching")
        lines.append(f"- {edge.get('trait', '?')}: {edge.get('why', 'a recent game challenged this.')}")
        lines.append("")

    rel = soul.get("relational", [])
    if rel:
        lines.append("## Us, at the board")
        for r in rel[:MAX_RELATIONAL]:
            note = r.get("note", "").strip()
            if note:
                lines.append(f"- {note}")
        lines.append("")

    text = "\n".join(lines).rstrip() + "\n"
    return _enforce_budget(text)


def _enforce_budget(text: str) -> str:
    """Hard-trim the pack to the token budget (cheap word-count proxy ~1.3 tok/word).

    The dream prunes overflow by demoting to warm; here we guarantee the file never blows
    the budget by truncating the least-load-bearing tail (history before style is kept)."""
    approx_tokens = lambda s: int(len(s.split()) * 1.3)
    if approx_tokens(text) <= HOT_TOKEN_BUDGET:
        return text
    # trim from the end (history is last) until under budget
    paras = text.split("\n\n")
    while len(paras) > 1 and approx_tokens("\n\n".join(paras)) > HOT_TOKEN_BUDGET:
        paras.pop()
    trimmed = "\n\n".join(paras).rstrip() + "\n"
    return trimmed


def write_hot_md(soul: dict[str, Any]) -> Path:
    """Render and persist HOT.md for the bubble. Returns the path."""
    p = hot_path(soul["bubble"])
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(render_hot_md(soul), encoding="utf-8")
    return p


# =============================================================================
# reverie minting (hand candidates to reveries.py; soul OWNS minting)
# =============================================================================

def _mint_reverie_candidates(soul: dict[str, Any]) -> list[dict[str, Any]]:
    """Mint 1-3 reverie candidates from relational/episodic records: a past moment + a
    trigger-condition + a cooldown. The soul mints; reveries.py persists and matches live."""
    cands: list[dict[str, Any]] = []
    for r in soul.get("relational", [])[:3]:
        note = r.get("note", "").strip()
        if not note:
            continue
        cands.append({
            "bubble": soul["bubble"],
            "moment": note,
            "trigger": _trigger_for(soul["bubble"], note),
            "cooldown_turns": 8,
            "tone": r.get("affect", 0.0),
            "ref": r.get("ref"),
        })
    return cands[:3]


def _trigger_for(bubble: str, note: str) -> str:
    """A cheap trigger-condition string the live hook keyword-matches against."""
    # chess reveries fire when chess/board topics return
    return f"{bubble} OR board OR game OR move OR position"


# =============================================================================
# the public entry point: the bounded equilibration the dream calls
# =============================================================================

def update_bubble_soul(bubble: str, *, bookmarks_path: Optional[Path] = None) -> dict[str, Any]:
    """Load soul.json, apply the bounded running-estimate update over this bubble's bookmarks,
    render HOT.md FROM soul.json, mint reverie candidates, return a summary.

    Returns: {bubble, version, games_processed, axes_touched, refined, promotions, reveries,
              hot_path}. ``promotions`` are PROPOSE-only (never written to self/).

    The dream calls this for each touched bubble. Pure-ish: reads bookmarks (and corpus, via
    the firewall, in the deep path), writes soul.json + HOT.md.
    """
    soul = load_soul(bubble)
    # default to the module-level path so a test that monkeypatches BOOKMARKS_PATH flows
    # through; production leaves it == config's, which routes to the firewall read API.
    bookmarks = _read_bookmarks(bubble, path=bookmarks_path or BOOKMARKS_PATH)

    touched: set[str] = set()
    refined: list[str] = []
    games_processed = 0

    for m in bookmarks:
        kind = m.get("kind")
        # style-bearing bookmarks drive the axes; relational ones are handled separately
        if kind in ("relational", "joke", "banter", "affect"):
            continue

        games_processed += 1
        surprise, axis_id, polarity, outcome = _bookmark_signal(m)

        axis = _find_axis(soul, axis_id)
        if axis is None:
            # quarantine in the pool until seen MIN_AXIS_N times
            cand = _find_pool(soul, axis_id)
            if cand is None:
                cand = _new_pool_entry(axis_id, _label_for(axis_id, m))
                # carry context tags if the bookmark named them
                cand["context_tags"] = list(m.get("context_tags", []))
                soul["axis_pool"].append(cand)
            event = _apply_one(cand, surprise, polarity, outcome, m)
            if event != "no_outcome":
                touched.add(axis_id)
        else:
            event = _apply_one(axis, surprise, polarity, outcome, m)
            if event != "no_outcome":
                touched.add(axis_id)
            if event == "refined":
                refined.append(axis_id)
                soul["edge"] = {"trait": axis_id, "why": m.get("note", "a counter-game refined this.")}

    # candidates that earned their place graduate from the pool
    _promote_pool_axes(soul)

    # history + affect: pin, do not merge (the opposite operator)
    _update_relational(soul, bookmarks)

    # favoritism summary, derived from the settled axes
    _update_favoritism(soul)

    # bubble-bleed PROPOSE-only promotions (never auto-written to self/)
    promotions = _bleed_promotions(soul)

    # bookkeeping
    soul["games_seen"] = soul.get("games_seen", 0) + games_processed
    soul["version"] = soul.get("version", 0) + 1
    soul["updated"] = _now_iso()

    save_soul(soul)
    hp = write_hot_md(soul)

    reveries = _mint_reverie_candidates(soul)
    # hand candidates to reveries.py (soul owns minting); import lazily to avoid a hard
    # cycle and to keep the module importable even if reveries.json is absent.
    try:
        from engine.memory import reveries as reveries_mod
        if reveries:
            reveries_mod.mint(reveries, maxn=3)
    except Exception:
        pass  # reverie persistence is best-effort; the soul update is the durable act

    return {
        "bubble": bubble,
        "version": soul["version"],
        "games_processed": games_processed,
        "axes_touched": sorted(touched),
        "refined": refined,
        "promotions": promotions,
        "reveries": len(reveries),
        "hot_path": str(hp),
    }


# convenient alias the spec also names
re_derive = update_bubble_soul


# =============================================================================
# CLI — `vape soul show <bubble>` (lives in this module; integrator registers it)
# =============================================================================
# Defined here so the whole soul component (algorithm + its CLI surface) stays in the
# soul owner's files. Registered into main.py by the INTEGRATOR with one line:
#   from engine.memory.soul import soul_app
#   app.add_typer(soul_app)
# The soul owner never edits main.py (the integrator's shared entry point).

try:
    import typer
    from rich.console import Console

    _console = Console()

    soul_app = typer.Typer(
        name="soul",
        help="Inspect an activity-bubble's soul (style + history, grown by the dream).",
        no_args_is_help=True,
    )

    @soul_app.command("show")
    def _soul_show(
        bubble: str = typer.Argument(..., help="The bubble whose soul to show, e.g. chess."),
        json_out: bool = typer.Option(False, "--json", help="Dump raw soul.json instead of prose."),
    ) -> None:
        """Show the bubble's soul: the rendered HOT.md pack, plus the legible axes underneath."""
        soul = load_soul(bubble)
        if json_out:
            _console.print_json(json.dumps(soul, ensure_ascii=False))
            return

        if soul.get("version", 0) == 0 and not soul.get("axes"):
            _console.print(
                f"  [dim]The [bold]{bubble}[/bold] soul is a stub — too few games to have a "
                f"style yet. Run the dream over some {bubble} bookmarks to grow it.[/dim]"
            )
            return

        _console.print(
            f"  [bold]{bubble}[/bold] soul · v{soul.get('version')} · "
            f"{soul.get('games_seen', 0)} game(s) · updated {soul.get('updated')}"
        )
        _console.print()
        # the prose pack as Saori would load it
        _console.print("[bold]— the pack (HOT.md) —[/bold]")
        _console.print(render_hot_md(soul))

        # the legible axes underneath (the part she can disagree with / freeze / haul to the lion)
        axes = soul.get("axes", [])
        if axes:
            _console.print("[bold]— the axes (legible, signed, ownable) —[/bold]")
            for a in axes:
                frozen = " [red](frozen)[/red]" if a.get("frozen") else ""
                _console.print(
                    f"  · [bold]{a['id']}[/bold]: w={a['w']:+.3f} "
                    f"conf={a['confidence']:.2f} n={a['n_updates']} "
                    f"tags={a.get('context_tags') or '[]'} "
                    f"exemplars={_exemplar_ids(a.get('exemplar_ids')) or '[]'}{frozen}"
                )
                _console.print(f"      [dim]{a['label']}[/dim]")
        pool = soul.get("axis_pool", [])
        if pool:
            _console.print(f"  [dim]axis_pool (quarantined, < {MIN_AXIS_N} games): "
                           f"{[p['id'] for p in pool]}[/dim]")
        edge = soul.get("edge")
        if edge:
            _console.print(f"  [yellow]edge[/yellow]: {edge.get('trait')} — {edge.get('why')}")

except Exception:  # pragma: no cover — typer/rich absent shouldn't break the algorithm import
    soul_app = None
