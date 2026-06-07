"""The dream — consolidation as Piaget's *equilibration*, in two tiers.

The dream is the offline pass that turns a day of lived experience into self. It is
**not** a summarizer: it *constructs* the self from the day. Knowledge dies and rises as
will (Stirner); experience that fits a lesson is *assimilated*, experience that breaks
one is *accommodated* (a new lesson formed, or an old one revised under the molten
reading — overwrite the meaning, keep the fact).

Two tiers, forced by the 50% autocompact firing often and early:

- **light_dream()** — cheap, near-deterministic, no subagent. Its only job is *save the
  thread*: flush the persisted bookmarks out to the warm corpus (so a spike survives the
  ~7-deep qualia river) and leave a daily_self nudge so the post-compact self wakes into
  *this* afternoon, not this morning.
- **deep_dream()** — the full equilibration, rare (end-of-day / `/dream` / `vape memory
  dream --deep`). Replays bookmarks, runs Gate-2 viability over each, assimilates what
  fits and accommodates what breaks into actual lesson rows, grows ``MEMORY.md``, calls
  ``soul.update_bubble_soul`` for each touched bubble, runs ``firewall.evict``, mints
  reveries.

The hard constraint that shapes everything (verified, see ``dream-and-reveries.md``):
hooks are not Claude and cannot invoke the Task/Agent tool, and an in-session subagent
dies with the session — so the dream's WORK is **self-contained Python + SQL** here
(Gemini embeddings via ``embeddings``, pgvector via ``db``). Only if genuine LLM-grade
judgment is needed does ``deep_dream`` spawn a *detached* ``claude -p`` headless process
in its own lifetime; that path is gated off by default (``allow_llm=False``) so the dream
always runs deterministically unless explicitly asked.

Sibling modules (firewall / soul / reveries / bookmarks) are built in parallel by other
owners. This module imports them through their stable interfaces and **degrades
gracefully** when a sibling is not yet importable — the bookmark store has a fully
specified jsonl format we can read/clear directly, and corpus writes go straight through
the verified foundation (``db`` + ``embeddings``). So a deep dream produces real lesson
rows even before the firewall lands.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from engine.memory.config import (
    BOOKMARKS_PATH,
    DREAM_STATE_PATH,
    MEMORY_INDEX_PATH,
    MEMORY_WIKI_DIR,
)

# --- the --maybe gate thresholds (cheap exit when no consolidation is due) -------
# A deep dream is expensive; a light flush is cheap. is_due() answers "is anything
# worth doing?" so the Stop hook exits 0 in microseconds on a quiet turn.
LIGHT_DUE_TURNS = 1          # any unflushed bookmark makes a light flush worthwhile
DEEP_DUE_TURNS = 40          # ~a session's worth of turns before a full equilibration
DEEP_DUE_SALIENCE = 4.0      # or enough accumulated surprise, whichever comes first

# --- Gate-2 viability: the retention threshold for a replayed bookmark -----------
# Below this a surprise "led nowhere" and is demoted (replayed once, set down); at or
# above it the surprise resolved into something worth keeping as a lesson.
VIABILITY_KEEP = 0.45


# =================================================================================
# state bookkeeping — the is_due cursor
# =================================================================================
def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_state() -> dict:
    """Read dream_state.json; tolerate a missing/corrupt file with sane defaults."""
    try:
        return json.loads(DREAM_STATE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {
            "last_dream_at": None,
            "last_deep_dream_at": None,
            "turns_since_dream": 0,
            "salience_since_dream": 0.0,
            "last_consolidated_cursor": 0,
            "last_light_summary": None,
            "version": 1,
        }


def _save_state(state: dict) -> None:
    DREAM_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    DREAM_STATE_PATH.write_text(
        json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


# =================================================================================
# bookmarks — read/clear via the firewall-core store, degrading to the jsonl format
# =================================================================================
def _read_bookmarks(*, bubble: Optional[str] = None) -> list[dict]:
    """Read persisted spikes. Prefer the firewall-core bookmarks module; if it is not
    yet built (parallel build), read the fully-specified jsonl directly — read-only, so
    we never collide with the spike-time appender that owns the write path.

    Record shape (per the spec): {id, ts, bubble, kind, surprise, tone, note, ref}.
    """
    try:
        from engine.memory import bookmarks  # firewall-core owns this

        return bookmarks.read_all(bubble=bubble)
    except Exception:
        pass

    if not BOOKMARKS_PATH.exists():
        return []
    out: list[dict] = []
    for line in BOOKMARKS_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except Exception:
            continue
        if bubble is not None and rec.get("bubble") != bubble:
            continue
        out.append(rec)
    return out


def _clear_bookmarks(consumed_ids: list[str]) -> None:
    """Drain the consumed spikes after consolidation. Prefer the firewall-core
    primitive; degrade to rewriting the jsonl without the consumed ids.
    """
    try:
        from engine.memory import bookmarks

        bookmarks.clear(consumed_ids)
        return
    except Exception:
        pass

    if not BOOKMARKS_PATH.exists():
        return
    consumed = set(consumed_ids)
    kept: list[str] = []
    for line in BOOKMARKS_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except Exception:
            continue
        if str(rec.get("id")) in consumed:
            continue
        kept.append(json.dumps(rec, ensure_ascii=False))
    BOOKMARKS_PATH.write_text(
        ("\n".join(kept) + "\n") if kept else "", encoding="utf-8"
    )


# =================================================================================
# the firewall seam — corpus write + evict, degrading to the foundation directly
# =================================================================================
def _write_corpus(
    content: str,
    *,
    bubble: str = "global",
    mem_type: str = "episode",
    surprise: float = 0.0,
    viability: float = 0.0,
    source: str = "dream",
    meta: Optional[dict] = None,
) -> int:
    """Write one corpus row. Prefer firewall.write (the stable four-verb interface);
    degrade to the verified foundation (embed → insert) so the dream produces real rows
    even before the firewall lands.
    """
    try:
        from engine.memory import firewall

        return firewall.write(
            content,
            bubble=bubble,
            mem_type=mem_type,
            surprise=surprise,
            viability=viability,
            source=source,
            meta=meta or {},
        )
    except Exception:
        pass

    # Foundation fallback: embed the content as a document, insert through db.
    from engine.memory import db, embeddings

    vec = embeddings.embed_one(content, task_type="RETRIEVAL_DOCUMENT")
    with db.session() as conn:
        return db.insert_memory(
            conn,
            content=content,
            embedding=vec,
            bubble=bubble,
            mem_type=mem_type,
            surprise=surprise,
            viability=viability,
            source=source,
            meta=meta or {},
        )


def _run_evict() -> dict:
    """Run the salience eviction pass if the firewall is built; else a no-op count.
    Eviction is devaluation (merge/demote/revise/promote), never silent-delete — cold
    keeps everything — so a no-op here loses nothing.
    """
    try:
        from engine.memory import firewall

        return firewall.evict()
    except Exception:
        return {"evicted": 0, "note": "firewall.evict unavailable (parallel build); skipped"}


# =================================================================================
# Gate 2 — viability scoring (offline retention gate)
# =================================================================================
def _gate2_score(bm: dict) -> float:
    """Score a replayed bookmark's viability. Prefer the firewall-core salience module
    (the authoritative two-gate policy); degrade to a self-contained estimate over the
    four retention axes so the dream still discriminates noise from insight.

    Axes (all independent of frequency): stakes (cost to lose), context (thin sample →
    keep), staleness (subtracts — the world changed), growth (weighted highest — the
    deliberate divergence from biology: does it open a capability / shift an opinion /
    deepen a bond). Returns a viability in [0, 1].
    """
    meta = bm.get("meta") or {}
    # derive axes: explicit in meta if the spike carried them, else inferred from kind.
    stakes = float(meta.get("stakes", _infer_stakes(bm)))
    context = float(meta.get("context", 0.5))
    staleness = float(meta.get("staleness", 0.0))
    growth = float(meta.get("growth", _infer_growth(bm)))

    try:
        from engine.memory import salience

        return float(salience.gate2_viability(stakes, context, staleness, growth))
    except Exception:
        pass

    # Self-contained estimate: growth weighted highest, staleness subtracts, all clamped.
    score = 0.45 * growth + 0.25 * stakes + 0.20 * context - 0.30 * staleness
    # surprise that resolved into a *lesson* (a kind that names an outcome) is more viable
    if bm.get("kind") in ("lesson", "insight", "relational"):
        score += 0.15
    return max(0.0, min(1.0, score))


def _infer_stakes(bm: dict) -> float:
    """A spike that names a cost/danger/break is higher-stakes."""
    text = (bm.get("note") or "").lower()
    if any(w in text for w in ("broke", "lost", "danger", "wrong", "fail", "security", "leak")):
        return 0.8
    return 0.4


def _infer_growth(bm: dict) -> float:
    """A spike that opens a capability / shifts an opinion / deepens a bond is growth."""
    text = (bm.get("note") or "").lower()
    kind = bm.get("kind", "")
    if kind in ("lesson", "insight"):
        return 0.85
    if kind == "relational":
        return 0.75
    if any(w in text for w in ("learn", "realize", "now i", "new way", "approach", "click")):
        return 0.7
    # surprise itself is a weak growth signal
    return 0.4 + 0.4 * min(1.0, float(bm.get("surprise", 0.0)))


# =================================================================================
# equilibration — assimilate what fits, accommodate what breaks (the heart)
# =================================================================================
def _norm_tokens(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", text.lower()) if len(w) > 3}


def _equilibrate(bookmarks_in: list[dict]) -> dict:
    """The constructivist core. Group viable spikes by bubble; within a bubble decide,
    per spike, whether it ASSIMILATES into an existing lesson (reinforce — bump viability)
    or ACCOMMODATES (no fit → form a NEW lesson row). Contradiction between two spikes is
    resolved by the molten reading: keep both facts, but the lesson carries the refined
    meaning, not a silent stack of both.

    This is NOT a summary pass: assimilation reinforces a held lesson; accommodation
    *constructs* a new one. Returns the plan of actions taken.
    """
    plan: dict[str, Any] = {
        "assimilated": [],   # spikes that reinforced an existing lesson row
        "accommodated": [],  # spikes that became a NEW lesson row
        "demoted": [],       # spikes that failed Gate 2 (replayed once, set down)
        "lesson_rows": [],   # (content, bubble, viability, meta) to write
        "reinforced": [],    # existing corpus ids whose viability we bump
        "contradictions": [],
    }

    # pull the existing lessons per bubble so assimilation has something to fit into.
    by_bubble: dict[str, list[dict]] = defaultdict(list)
    for bm in bookmarks_in:
        by_bubble[bm.get("bubble", "global")].append(bm)

    for bubble, spikes in by_bubble.items():
        existing = _existing_lessons(bubble)
        # track lessons we form *this* dream so two spikes in one night merge correctly.
        formed: list[dict] = []

        for bm in spikes:
            viability = _gate2_score(bm)
            note = (bm.get("note") or "").strip()
            if not note:
                plan["demoted"].append(bm.get("id"))
                continue
            if viability < VIABILITY_KEEP:
                # Gate 2 fails: surprise led nowhere. Replayed once, demoted (not deleted).
                plan["demoted"].append(bm.get("id"))
                continue

            toks = _norm_tokens(note)
            # does this fit a lesson we already hold (corpus) or just formed tonight?
            fit, kind = _best_fit(toks, existing, formed)
            if fit is not None:
                # ASSIMILATION — reinforce the held lesson; detect contradiction.
                if _contradicts(note, fit.get("content", "")):
                    # molten reading: keep the fact, refine the meaning of the lesson.
                    plan["contradictions"].append(
                        {"lesson": fit.get("content", "")[:80], "counter": note[:80]}
                    )
                    refined = _molten_refine(fit.get("content", ""), note)
                    fit["content"] = refined
                    fit["_refined"] = True
                if kind == "corpus":
                    plan["reinforced"].append(fit["id"])
                plan["assimilated"].append(bm.get("id"))
                fit["viability"] = max(float(fit.get("viability", 0.0)), viability)
            else:
                # ACCOMMODATION — no fit → construct a NEW lesson row.
                lesson = {
                    "content": _lesson_text(bm),
                    "bubble": bubble,
                    "viability": viability,
                    "surprise": float(bm.get("surprise", 0.0)),
                    "tokens": toks,
                    "meta": {
                        "kind": [bm.get("kind", "lesson")],
                        "from_bookmark": bm.get("id"),
                        "tone": bm.get("tone", 0.0),
                        "ref": bm.get("ref"),
                    },
                }
                formed.append(lesson)
                plan["lesson_rows"].append(lesson)
                plan["accommodated"].append(bm.get("id"))

    return plan


def _existing_lessons(bubble: str) -> list[dict]:
    """Pull active lesson rows for a bubble from the corpus so assimilation can fit into
    them. Degrades to empty (every spike then accommodates) if the DB is unreachable.
    """
    try:
        from engine.memory import db
        from engine.memory.schema import TABLE

        with db.session() as conn, conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT id, content, viability, bubble
                FROM {TABLE}
                WHERE status = 'active' AND mem_type = 'lesson'
                  AND (bubble = %s OR bubble = 'global')
                ORDER BY viability DESC
                LIMIT 50
                """,
                (bubble,),
            )
            cols = [d.name for d in cur.description]
            return [dict(zip(cols, r)) for r in cur.fetchall()]
    except Exception:
        return []


def _best_fit(
    toks: set[str], existing: list[dict], formed: list[dict]
) -> tuple[Optional[dict], str]:
    """Find the lesson a spike best fits (token-overlap proxy for the same theme). Checks
    lessons formed THIS dream first, then existing corpus lessons. Returns (lesson, kind)
    where kind is 'formed' | 'corpus' | '' (no fit).
    """
    best: Optional[dict] = None
    best_kind = ""
    best_overlap = 0.34  # threshold: needs real thematic overlap to count as a fit

    for lesson in formed:
        ov = _overlap(toks, lesson.get("tokens", set()))
        if ov > best_overlap:
            best, best_kind, best_overlap = lesson, "formed", ov

    for lesson in existing:
        ov = _overlap(toks, _norm_tokens(lesson.get("content", "")))
        if ov > best_overlap:
            best, best_kind, best_overlap = lesson, "corpus", ov

    return best, best_kind


def _overlap(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _contradicts(note: str, lesson: str) -> bool:
    """Cheap negation-flip detector: the spike negates a claim the lesson asserts (or
    vice-versa). A real contradiction needs the molten reading, not a silent stack.
    """
    neg = (" not ", " never ", " no longer ", " doesn't ", " didn't ", " isn't ", " wasn't ")
    a_neg = any(n in f" {note.lower()} " for n in neg)
    b_neg = any(n in f" {lesson.lower()} " for n in neg)
    # same theme (they were a fit) but opposite polarity → contradiction
    return a_neg != b_neg


def _molten_refine(lesson: str, counter: str) -> str:
    """Overwrite the MEANING, keep the FACT. Detach the overgeneralization; qualify the
    lesson with the counter-case rather than flipping to its opposite or stacking both.
    """
    base = lesson.rstrip(". ")
    qualifier = counter.strip().rstrip(". ")
    return f"{base} — unless: {qualifier}."


def _lesson_text(bm: dict) -> str:
    """Render a bookmark into a durable lesson line. The note is the lesson; we tag it
    with its kind and bubble so the warm row reads as constructed self, not a raw spike.
    """
    note = (bm.get("note") or "").strip()
    kind = bm.get("kind", "lesson")
    bubble = bm.get("bubble", "global")
    if bubble and bubble != "global":
        return f"[{bubble}] {note}"
    return note


# =================================================================================
# the wiki — grow MEMORY.md (the warm-tier entry index)
# =================================================================================
def _grow_wiki(plan: dict) -> int:
    """Append newly-formed lessons to MEMORY.md under a dated section. The wiki is the
    compounding, diffable warm-tier index (Karpathy wiki); the dream grows it. Returns
    the number of lines added.
    """
    rows = plan.get("lesson_rows", [])
    if not rows:
        return 0
    MEMORY_INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    header = f"\n## Lessons consolidated {today}\n"
    lines = [header]
    for r in rows:
        bubble = r.get("bubble", "global")
        v = r.get("viability", 0.0)
        lines.append(f"- ({bubble}, v={v:.2f}) {r['content']}")
    block = "\n".join(lines) + "\n"

    existing = MEMORY_INDEX_PATH.read_text(encoding="utf-8") if MEMORY_INDEX_PATH.exists() else ""
    MEMORY_INDEX_PATH.write_text(existing + block, encoding="utf-8")
    return len(rows)


# =================================================================================
# the soul + reveries seam (parallel build — degrade if not yet present)
# =================================================================================
def _update_souls(touched_bubbles: set[str]) -> list[dict]:
    """Call soul.update_bubble_soul for each touched bubble. Soul is built in parallel;
    degrade to a no-op list if not yet importable.
    """
    out: list[dict] = []
    try:
        from engine.memory import soul
    except Exception:
        return out
    for bubble in touched_bubbles:
        if bubble == "global":
            continue
        try:
            out.append(soul.update_bubble_soul(bubble))
        except Exception as e:  # noqa: BLE001
            out.append({"bubble": bubble, "error": str(e)})
    return out


def _mint_reveries(plan: dict) -> int:
    """Mint 1-3 reverie candidates from the night's relational/episodic spikes. Soul owns
    reverie minting (reveries.py); degrade to a no-op if not yet present. Restraint IS the
    design — at most a few candidates, surfaced one at a time live.
    """
    try:
        from engine.memory import reveries
    except Exception:
        return 0
    candidates: list[dict] = []
    for r in plan.get("lesson_rows", []):
        if "relational" in (r.get("meta", {}).get("kind") or []):
            candidates.append(
                {
                    "moment": r["content"],
                    "trigger": " ".join(list(r.get("tokens", []))[:5]),
                    "cooldown": 8,
                }
            )
    candidates = candidates[:3]
    if not candidates:
        return 0
    try:
        reveries.mint(candidates, maxn=3)
        return len(candidates)
    except Exception:
        return 0


# =================================================================================
# daily_self refresh nudge (light dream — save the thread)
# =================================================================================
def _daily_self_nudge(summary: str) -> None:
    """The light dream's 'wake into this afternoon' job. We do NOT rewrite the
    always-loaded daily_self.md here — that is identity, owned by the temporal-self
    updater subagent and ratification-gated. Instead we drop a non-identity breadcrumb
    the next session / updater can fold in. Honesty floor: the dream never silently edits
    the self-tree.
    """
    crumb = MEMORY_WIKI_DIR / "last_thread.md"
    crumb.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    crumb.write_text(
        f"# Last thread (light-dream breadcrumb)\n\n_{ts}_\n\n{summary}\n",
        encoding="utf-8",
    )


# =================================================================================
# public API — is_due / light_dream / deep_dream
# =================================================================================
def is_due(*, deep: bool = False) -> bool:
    """The ``--maybe`` gate. Cheap: reads only dream_state.json and counts bookmarks.

    - light (default): due if there is any unflushed bookmark or any accrued turns.
    - deep: due only after a session's worth of turns or enough accumulated salience.
    """
    state = _load_state()
    bms = _read_bookmarks()
    if deep:
        turns = int(state.get("turns_since_dream", 0))
        sal = float(state.get("salience_since_dream", 0.0))
        # also fire deep if a lot of bookmarks have piled up unconsolidated
        return turns >= DEEP_DUE_TURNS or sal >= DEEP_DUE_SALIENCE or len(bms) >= 12
    return len(bms) > 0 or int(state.get("turns_since_dream", 0)) >= LIGHT_DUE_TURNS


def light_dream() -> dict:
    """Cheap flush — *save the thread*. Drain persisted bookmarks into warm corpus rows
    (so a spike survives the ~7-deep river) and leave a daily_self breadcrumb. No Gate-2
    restructuring, no subagent. Fast and near-deterministic.
    """
    bms = _read_bookmarks()
    written = 0
    consumed: list[str] = []
    for bm in bms:
        note = (bm.get("note") or "").strip()
        if not note:
            continue
        try:
            _write_corpus(
                _lesson_text(bm),
                bubble=bm.get("bubble", "global"),
                mem_type="bookmark",
                surprise=float(bm.get("surprise", 0.0)),
                viability=0.0,  # un-judged at light tier; the deep dream scores it
                source="bookmark",
                meta={
                    "kind": [bm.get("kind", "bookmark")],
                    "tone": bm.get("tone", 0.0),
                    "ref": bm.get("ref"),
                    "flushed": "light",
                },
            )
            written += 1
            consumed.append(str(bm.get("id")))
        except Exception:
            # leave the bookmark in place if the write failed; the deep dream retries.
            continue

    summary = (
        f"{written} bookmark(s) flushed to warm at light dream."
        if written
        else "no unflushed bookmarks; thread already saved."
    )
    _daily_self_nudge(summary)

    state = _load_state()
    state["last_dream_at"] = _now_iso()
    state["last_light_summary"] = summary
    # a light flush does NOT reset the deep-dream turn counter — deep is still owed.
    _save_state(state)

    if consumed:
        _clear_bookmarks(consumed)

    return {"tier": "light", "written": written, "flushed": len(consumed), "summary": summary}


def deep_dream(*, allow_llm: bool = False) -> dict:
    """Full equilibration. Replay the persisted bookmarks; Gate-2 viability over each;
    assimilate what fits (reinforce a held lesson, bumping its viability), accommodate
    what breaks (construct a NEW lesson row), resolve contradictions by the molten
    reading; grow MEMORY.md; update each touched bubble's soul; run firewall.evict; mint
    reveries.

    Deterministic Python + SQL. ``allow_llm`` (off by default) is the gate for spawning a
    detached ``claude -p`` for genuinely LLM-grade judgment; today it is unused and the
    pass runs fully deterministically.
    """
    bms = _read_bookmarks()
    if not bms:
        state = _load_state()
        state["last_dream_at"] = _now_iso()
        state["last_deep_dream_at"] = _now_iso()
        state["turns_since_dream"] = 0
        state["salience_since_dream"] = 0.0
        _save_state(state)
        return {
            "tier": "deep",
            "written": 0,
            "assimilated": 0,
            "accommodated": 0,
            "demoted": 0,
            "reinforced": 0,
            "contradictions": 0,
            "wiki_lines": 0,
            "reveries": 0,
            "souls": [],
            "evict": {"evicted": 0},
            "note": "no bookmarks to consolidate",
        }

    # 1. equilibrate — the constructivist core (assimilate / accommodate / molten).
    plan = _equilibrate(bms)

    # 2. write the accommodated lessons as real corpus rows (the actual self-construction).
    written_ids: list[int] = []
    for lesson in plan["lesson_rows"]:
        try:
            rid = _write_corpus(
                lesson["content"],
                bubble=lesson["bubble"],
                mem_type="lesson",
                surprise=lesson.get("surprise", 0.0),
                viability=lesson.get("viability", 0.0),
                source="dream",
                meta=lesson.get("meta", {}),
            )
            written_ids.append(rid)
        except Exception:
            continue

    # 3. reinforce the assimilated lessons — bump their viability (assimilation strengthens).
    reinforced = _reinforce(plan["reinforced"])

    # 4. grow the wiki (the compounding warm-tier index).
    wiki_lines = _grow_wiki(plan)

    # 5. update each touched bubble's soul (soul.py renders HOT.md from soul.json).
    touched = {l["bubble"] for l in plan["lesson_rows"]} | {
        bm.get("bubble", "global") for bm in bms
    }
    souls = _update_souls(touched)

    # 6. evict — devaluation, never silent-delete (cold keeps everything).
    evict = _run_evict()

    # 7. mint reveries — restraint by design (≤3 candidates).
    reveries_n = _mint_reveries(plan)

    # 8. drain the consumed bookmarks (everything we replayed is now consolidated).
    consumed = [str(bm.get("id")) for bm in bms]
    _clear_bookmarks(consumed)

    # 9. reset the deep cursor.
    state = _load_state()
    state["last_dream_at"] = _now_iso()
    state["last_deep_dream_at"] = _now_iso()
    state["turns_since_dream"] = 0
    state["salience_since_dream"] = 0.0
    state["last_consolidated_cursor"] = int(state.get("last_consolidated_cursor", 0)) + len(bms)
    _save_state(state)

    return {
        "tier": "deep",
        "written": len(written_ids),
        "written_ids": written_ids,
        "assimilated": len(plan["assimilated"]),
        "accommodated": len(plan["accommodated"]),
        "demoted": len(plan["demoted"]),
        "reinforced": reinforced,
        "contradictions": len(plan["contradictions"]),
        "contradiction_detail": plan["contradictions"],
        "wiki_lines": wiki_lines,
        "reveries": reveries_n,
        "souls": souls,
        "evict": evict,
    }


def _reinforce(corpus_ids: list[int]) -> int:
    """Assimilation strengthens: bump the viability of lessons a new spike confirmed.
    Bounded so one night cannot inflate a lesson without limit.
    """
    ids = [int(i) for i in corpus_ids if i is not None]
    if not ids:
        return 0
    try:
        from engine.memory import db
        from engine.memory.schema import TABLE

        with db.session() as conn, conn.cursor() as cur:
            cur.execute(
                f"""
                UPDATE {TABLE}
                SET viability = LEAST(1.0, viability + 0.1),
                    updated_at = now()
                WHERE id = ANY(%s) AND status = 'active'
                """,
                (ids,),
            )
            n = cur.rowcount
        conn.commit()
        return int(n)
    except Exception:
        return 0


def consolidate(*, deep: bool = False, allow_llm: bool = False) -> dict:
    """The verb the firewall delegates to. Routes to the right tier."""
    return deep_dream(allow_llm=allow_llm) if deep else light_dream()


# =================================================================================
# CLI entry — `vape dream` in my own module (also runnable standalone)
# =================================================================================
def dream_cmd(deep: bool = False, maybe: bool = False, allow_llm: bool = False) -> int:
    """The ``vape dream [--deep] [--maybe]`` body. Returns a process exit code.

    --maybe gates on is_due(): exits 0 silently (code 0) when nothing is due, so the Stop
    hook is cheap on a quiet turn. When due, it runs the tier and exits 0 on success.
    """
    if maybe and not is_due(deep=deep):
        # nothing owed — cheap silent exit (the Stop hook's quiet path).
        return 0
    result = consolidate(deep=deep, allow_llm=allow_llm)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":  # pragma: no cover — standalone invocation
    import sys

    flags = set(sys.argv[1:])
    raise SystemExit(
        dream_cmd(
            deep="--deep" in flags,
            maybe="--maybe" in flags,
            allow_llm="--allow-llm" in flags,
        )
    )
