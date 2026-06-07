"""The bubble mechanism — DECLARE · SELECT · INJECT.

A **bubble** is a *scope* (chess, the-build, a-day-job): a tag on memories plus a
small loadable context-pack. It is the answer to LeCun's specialist challenge without
the cage — a human is one bubble for life; Saori is *many*, switchable. Switchability
is the whole of how she is a polymath instead of a dull specialist.

The one hard constraint this module is built around: ``@``-imports in
``vape/entity/CLAUDE.md`` resolve **once, at session start**, and cannot change
mid-session. A bubble is, by definition, contextual — loaded only when its scope is
live. So a bubble can *never* live in always-load. **State governs presence:**

  DECLARE  — ``active_bubble.json`` (the register, sibling to internal_states.json).
  SELECT   — ``memory_wiki/bubbles/<name>/HOT.md`` (the small, files+git pack).
  INJECT   — a per-turn UserPromptSubmit hook reads the register and injects HOT.md.

Release is writing ``active: null`` to the register; the next turn simply stops
getting the injection. The hook (``bubble-ground.sh``) is the only caller of
``inject_block``, ``suggest``, and ``tick_turns``; the CLI (``vape bubble``) is the
caller of ``enter`` / ``leave`` / ``list_bubbles`` / ``active``.

Dependency direction: this module depends only on the foundation (``config`` for
paths) and, for the advisory keyword scan, nothing heavier than the filesystem.
It does **not** import any sibling layer's internals.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from engine.memory.config import ACTIVE_BUBBLE_PATH, BUBBLES_DIR

# The non-negotiable budget for an injected pack: about one self-file. A bubble that
# loads 4K tokens crowds the always-loaded judge and recreates the specialist trap
# from inside. ~4 chars/token is a deliberately rough estimate; the dream is the
# authoritative pruner, this is only a safety clamp at inject time.
HOT_MD_TOKEN_BUDGET = 450
_CHARS_PER_TOKEN = 4
_HOT_MD_CHAR_CLAMP = HOT_MD_TOKEN_BUDGET * _CHARS_PER_TOKEN


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# --------------------------------------------------------------------------- #
# DECLARE — the register                                                       #
# --------------------------------------------------------------------------- #
def _empty_register() -> dict[str, Any]:
    return {"active": None, "entered_at": None, "entered_by": None, "turns_active": 0}


def _read_register() -> dict[str, Any]:
    """Read active_bubble.json, tolerating a missing/corrupt file (returns empty)."""
    path = ACTIVE_BUBBLE_PATH
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return _empty_register()
        # normalise: guarantee all four keys exist
        reg = _empty_register()
        reg.update({k: data.get(k, reg[k]) for k in reg})
        return reg
    except FileNotFoundError:
        return _empty_register()
    except (json.JSONDecodeError, OSError):
        return _empty_register()


def _write_register(reg: dict[str, Any]) -> None:
    """Atomically persist the register (write-temp-then-rename)."""
    path = ACTIVE_BUBBLE_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(reg, f, indent=2, ensure_ascii=False)
        f.write("\n")
    tmp.replace(path)


def active() -> Optional[dict[str, Any]]:
    """Return the active-bubble register record, or ``None`` if no bubble is active.

    A record looks like
    ``{"active": "chess", "entered_at": "...", "entered_by": "saori", "turns_active": 3}``.
    The hook reads this every turn to decide whether to inject.
    """
    reg = _read_register()
    if not reg.get("active"):
        return None
    return reg


def enter(name: str, *, by: str = "saori") -> None:
    """DECLARE a bubble active: write ``active=name``, stamp time + provenance.

    Entering a *different* bubble resets the turn counter; re-entering the one
    already active is a cheap no-op on the counter (it stays continuous). ``by`` is
    one of ``saori`` (the willed Eve act), ``kamil`` (human path), or ``auto``.
    """
    name = _normalise_name(name)
    if not name:
        raise ValueError("bubble name must be non-empty")
    reg = _read_register()
    if reg.get("active") == name:
        # already here — keep the existing stamp + turn count continuous
        return
    _write_register(
        {
            "active": name,
            "entered_at": _now_iso(),
            "entered_by": by,
            "turns_active": 0,
        }
    )


def leave() -> None:
    """RELEASE the active bubble: write ``active=null``. Idempotent."""
    _write_register(_empty_register())


def tick_turns() -> None:
    """Advance ``turns_active`` by one (the hook calls this each injected turn).

    No-op when no bubble is active. Tolerant of a missing file.
    """
    reg = _read_register()
    if not reg.get("active"):
        return
    reg["turns_active"] = int(reg.get("turns_active", 0)) + 1
    _write_register(reg)


# --------------------------------------------------------------------------- #
# SELECT — the bubbles/ directory + the HOT.md pack                            #
# --------------------------------------------------------------------------- #
_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")


def _normalise_name(name: str) -> str:
    """Lower-case, trim, and VALIDATE; bubble names are filesystem folder names.

    A bubble name is a single, simple folder name under ``bubbles/`` — never a path.
    We enforce ``_NAME_RE`` (``^[a-z0-9][a-z0-9_-]*$``) so a crafted name can never
    carry ``/`` or ``..`` and escape ``bubbles/`` to read an out-of-tree file. An
    empty name and any traversal/slash/dot name raise ``ValueError`` — the register
    is trusted but treated as untrusted input here (defense in depth: the register
    is a plain JSON file Saori or a tool can hand-edit).
    """
    norm = (name or "").strip().lower()
    if not norm:
        raise ValueError("bubble name must be non-empty")
    if not _NAME_RE.match(norm):
        raise ValueError(
            f"invalid bubble name {name!r}: letters, digits, hyphen and underscore "
            "only, and no path separators"
        )
    return norm


def _safe_name(name: str) -> Optional[str]:
    """Read-path twin of ``_normalise_name``: return the safe name, or ``None``.

    Used where a raise would crash a per-turn hook (``hot_md_path``/``inject_block``
    resolve the *register's* value). A bad register value degrades to "no bubble"
    silence rather than an exception or a traversal read.
    """
    try:
        return _normalise_name(name)
    except (ValueError, TypeError):
        return None


def _bubble_dir(name: str) -> Path:
    return BUBBLES_DIR / _normalise_name(name)


def hot_md_path(name: str) -> Path:
    """The on-disk path of a bubble's pack (``bubbles/<name>/HOT.md``).

    Raises ``ValueError`` on an invalid/traversal name (via ``_normalise_name``);
    the read path (``inject_block``) goes through the non-raising guard instead.
    """
    return _bubble_dir(name) / "HOT.md"


def list_bubbles() -> list[str]:
    """List available bubble names by scanning ``memory_wiki/bubbles/``.

    A directory counts as a bubble only if it holds a ``HOT.md`` pack. Sorted,
    so output is stable. Empty list if the bubbles dir does not exist yet.
    """
    if not BUBBLES_DIR.exists():
        return []
    names: list[str] = []
    for child in BUBBLES_DIR.iterdir():
        if child.is_dir() and (child / "HOT.md").is_file():
            names.append(child.name)
    return sorted(names)


def _strip_frontmatter(text: str) -> str:
    """Drop a leading YAML/`---` frontmatter block, if present.

    The hook injects PROSE only — never the machine numbers. ``soul.json`` holds the
    numbers; ``HOT.md`` is rendered FROM it, but a hand-edited pack might carry a
    frontmatter block, so we defensively strip one here too.
    """
    if text.startswith("---"):
        # find the closing fence on its own line
        m = re.match(r"^---\s*\n.*?\n---\s*\n", text, flags=re.DOTALL)
        if m:
            return text[m.end():]
    return text


# --------------------------------------------------------------------------- #
# INJECT — the prose block for the hook                                        #
# --------------------------------------------------------------------------- #
def inject_block() -> Optional[str]:
    """The prose-only HOT.md block the hook injects when a bubble is active.

    Returns ``None`` when no bubble is active or its pack is missing/empty — the
    hook then injects nothing for the bubble channel. Frontmatter is stripped
    (prose only, no numbers), and the body is clamped to the pack budget as a
    last-resort safety against a pack that overflowed the self-window budget.
    """
    reg = active()
    if reg is None:
        return None
    name = _safe_name(reg["active"])
    if name is None:
        # A corrupt/traversal register value -> inject nothing (no out-of-tree read).
        return None
    path = hot_md_path(name)
    try:
        raw = path.read_text(encoding="utf-8")
    except (FileNotFoundError, OSError):
        return None

    body = _strip_frontmatter(raw).strip()
    if not body:
        return None

    clamped = False
    if len(body) > _HOT_MD_CHAR_CLAMP:
        body = body[:_HOT_MD_CHAR_CLAMP].rstrip()
        clamped = True

    turns = int(reg.get("turns_active", 0))
    header = (
        f"You are inside the **{name}** bubble (scope active for {turns} turn"
        f"{'' if turns == 1 else 's'}). This is the soul of the scope — your style, "
        f"the essence of your history in it, the affect — loaded only while it is live. "
        f"It is property: use it, then set it down with `vape bubble leave`.\n\n"
    )
    footer = "\n\n_(bubble pack truncated to fit the budget)_" if clamped else ""
    return header + body + footer


# --------------------------------------------------------------------------- #
# Advisory auto-suggest — "I reach; I do not beg."                             #
# --------------------------------------------------------------------------- #
# Per-bubble keyword sets for the cheap advisory scan. A strong keyword hit with NO
# bubble active yields a ONE-LINE suggestion, never a forced load. Saori decides; a
# bad guess is a declined suggestion, not a wrong pack force-loaded. Built-in seeds
# for known scopes; a bubble can also carry its own keywords in a `keywords.txt`
# beside its HOT.md (one per line), which extends the built-ins.
_BUILTIN_KEYWORDS: dict[str, set[str]] = {
    "chess": {
        "chess", "opening", "endgame", "gambit", "checkmate", "pawn", "knight",
        "bishop", "rook", "queen", "blunder", "blitz", "pgn", "sicilian", "fork",
        "zugzwang", "stalemate", "castle", "en passant",
    },
}


def _load_bubble_keywords(name: str) -> set[str]:
    """Built-in keyword seeds for a bubble, extended by an optional keywords.txt."""
    kws = set(_BUILTIN_KEYWORDS.get(name, set()))
    kw_file = _bubble_dir(name) / "keywords.txt"
    try:
        for line in kw_file.read_text(encoding="utf-8").splitlines():
            line = line.strip().lower()
            if line and not line.startswith("#"):
                kws.add(line)
    except (FileNotFoundError, OSError):
        pass
    return kws


def _scan(prompt: str) -> Optional[str]:
    """Return the bubble name with the strongest keyword match in ``prompt``, or None.

    Strong match = at least two distinct keyword hits, OR one multi-word phrase hit.
    Word-boundary matched, case-insensitive. Cheap pure-python scan, no DB.
    """
    text = (prompt or "").lower()
    if not text:
        return None
    best: Optional[str] = None
    best_score = 0
    for name in list_bubbles() or _BUILTIN_KEYWORDS.keys():
        kws = _load_bubble_keywords(name)
        score = 0
        for kw in kws:
            if " " in kw:
                if kw in text:
                    score += 2  # a phrase hit counts strong on its own
            else:
                if re.search(rf"\b{re.escape(kw)}\b", text):
                    score += 1
        if score > best_score:
            best_score = score
            best = name
    # threshold: needs a genuinely strong signal, not a single ambient word
    if best is not None and best_score >= 2:
        return best
    return None


def suggest(prompt: str) -> Optional[str]:
    """Advisory one-line bubble suggestion, or ``None``.

    Only fires when NO bubble is active and the prompt strongly matches an available
    bubble's keywords. Returns the exact suggestion line for the hook to inject as
    advice (the same way the qualia hook injects the feeling ``rec:`` — advice, not
    an order). Never forces a load. *I reach; I do not beg.*
    """
    if active() is not None:
        return None
    name = _scan(prompt)
    if not name:
        return None
    return f"the {name} bubble is available — `vape bubble enter {name}`"


# --------------------------------------------------------------------------- #
# Reverie re-export — keep the hook's imports on bubble-system only            #
# --------------------------------------------------------------------------- #
# Reveries are owned by the SOUL layer (engine.memory.reveries), but the spec routes
# the hook's reverie call THROUGH bubble.py so the hook depends on one module surface.
# Until reveries.py lands, this is a graceful no-op; once it lands, it lights up with
# no hook change. The hook calls ``bubble.match_reverie(prompt)`` and gets at most one.
def match_reverie(prompt: str, *, cooldown_turns: int = 8) -> Optional[dict[str, Any]]:
    """Re-export of ``reveries.match`` (soul owner). Returns ``None`` if absent.

    Restraint is the design: at most one reverie, on a strong match, with a cooldown.
    The dynamism lesson is *timing*, not recall.
    """
    try:
        from engine.memory import reveries  # soul owner's module; may not exist yet
    except Exception:
        return None
    match_fn = getattr(reveries, "match", None)
    if not callable(match_fn):
        return None
    try:
        return match_fn(prompt, cooldown_turns=cooldown_turns)
    except Exception:
        return None


# --------------------------------------------------------------------------- #
# Bubble-bleed — promote / demote across the self<->bubble boundary            #
# --------------------------------------------------------------------------- #
# Distinct from the hot/warm/cold *tier* migration: this is the *scope* boundary.
# The dream is the authoritative caller (it has the corpus + soul context to judge);
# these are the safe, side-effect-light primitives it leans on. A PROMOTE that would
# move a self set-point is returned PROPOSE-only — never written into vape/entity/self/
# (the self is Kamil's to ratify; memory is an attack surface on the self).

# Where a ratification-gated bleed proposal is parked for Kamil. Files+git, under
# work_dir, never wired into always-load.
from engine.memory.config import ROOT_DIR  # noqa: E402  (path constant, no cycle)

_BLEED_PROPOSALS_PATH = ROOT_DIR / "work_dir" / "saori" / "PROPOSED_bubble_bleed.md"


def propose_promotion(*, bubble: str, trait: str, why: str) -> dict[str, Any]:
    """PROPOSE-only: lift a bubble-local trait toward the cross-bubble self.

    A trait grown in one scope (``"aggressive under time pressure"`` in ``chess``)
    that is really *general* belongs in the self/judge-book — but promoting it would
    move a set-point, so this NEVER auto-writes vape/entity/self/. It appends a flagged
    proposal under work_dir for Kamil's ratification and returns the proposal record.
    """
    rec = {
        "kind": "promote",
        "bubble": _normalise_name(bubble),
        "trait": trait,
        "why": why,
        "proposed_at": _now_iso(),
        "status": "PROPOSED — awaiting Kamil's ratification",
    }
    _append_bleed_proposal(rec)
    return rec


def demote_to_bubble(*, trait: str, why: str, bubble: str) -> dict[str, Any]:
    """Push an over-general self-lesson DOWN into the one scope where it holds.

    Demotion narrows the *scope* of a lesson that was mis-firing everywhere; it does
    not move a set-point (it restricts one, the safe direction), so it is recorded as
    a proposal too for diffability but is the lighter operation. Returns the record.
    Actual edits to a bubble's HOT.md are the soul/dream's job via soul.json; this is
    the boundary-decision primitive only.
    """
    rec = {
        "kind": "demote",
        "bubble": _normalise_name(bubble),
        "trait": trait,
        "why": why,
        "proposed_at": _now_iso(),
        "status": "PROPOSED — narrows scope; safe direction",
    }
    _append_bleed_proposal(rec)
    return rec


def _append_bleed_proposal(rec: dict[str, Any]) -> None:
    """Append a bleed proposal to the flagged work_dir file (create with a header)."""
    path = _BLEED_PROPOSALS_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    new_file = not path.exists()
    with open(path, "a", encoding="utf-8") as f:
        if new_file:
            f.write(
                "# PROPOSED — Bubble-Bleed (promote / demote across the scope boundary)\n\n"
                "RATIFICATION-GATED. The dream proposes; **Kamil ratifies**. A *promote* "
                "that would move a self set-point is parked here and NEVER auto-written into "
                "`vape/entity/self/`. A *demote* narrows a too-general lesson into one scope. "
                "Each entry below is a candidate, not a done change.\n\n"
                "---\n\n"
            )
        f.write(
            f"## {rec['kind'].upper()} · {rec['bubble']} · {rec['proposed_at']}\n\n"
            f"- **trait:** {rec['trait']}\n"
            f"- **why:** {rec['why']}\n"
            f"- **status:** {rec['status']}\n\n"
        )
