"""``bookmarks.jsonl`` — the durable spike store that plugs the river-leak.

The qualia river is a FIFO ~7 deep and drops the oldest seed every turn; the deep
dream fires *many* turns later. So a spike that passes Gate 1 must be written to a
durable file **at spike-time**, or it ages out of the river before the dream ever sees
it (``tensions-and-risks.md`` C8). That file is ``bookmarks.jsonl`` — append-only at the
spike, drained (and cleared) by the dream after consolidation.

Each record:
    {id, ts, bubble, kind, surprise, tone, note, ref}

- append-only JSON Lines (one record per line) — crash-safe, no read-modify-write of a
  whole file on the hot path, and trivially greppable in the files-only degradation.
- no DB: this is the *pre*-corpus buffer; the dream is what turns bookmarks into rows.
- ``clear`` removes consumed ids by rewriting the surviving lines (the only non-append
  op, and it runs offline in the dream, never on the spike path).
"""

from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any, Optional

from engine.memory.config import BOOKMARKS_PATH


def _path() -> Path:
    return Path(BOOKMARKS_PATH)


def append(rec: dict[str, Any]) -> dict[str, Any]:
    """Append one bookmark record to ``bookmarks.jsonl`` (creating it + parent if new).

    Fills in ``id`` (a short uuid) and ``ts`` (epoch seconds) if the caller omitted
    them, so every record is uniquely addressable for later ``clear``. Returns the
    completed record. Append-only and flushed — safe to call on the live spike path.
    """
    rec = dict(rec)
    rec.setdefault("id", uuid.uuid4().hex[:12])
    rec.setdefault("ts", time.time())

    p = _path()
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        f.flush()
    return rec


def read_all(*, bubble: Optional[str] = None) -> list[dict[str, Any]]:
    """Read every bookmark, oldest-first (file order). Filter to a bubble if given.

    Malformed lines are skipped rather than crashing the dream (a partial write from a
    crash mid-append should not poison the whole replay). Returns [] if the file is
    absent — the no-spikes-yet case.
    """
    p = _path()
    if not p.exists():
        return []
    out: list[dict[str, Any]] = []
    with p.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if bubble is not None and rec.get("bubble") != bubble:
                continue
            out.append(rec)
    return out


def clear(consumed_ids: list[str]) -> int:
    """Drop the given bookmark ids, keeping the rest (the dream calls this post-replay).

    Rewrites the file with only the surviving lines. If ``consumed_ids`` is empty this
    is a no-op. Passing the ids of *every* current bookmark empties the store. Returns
    the number of records removed. Runs offline (in the dream), never on the spike path.
    """
    if not consumed_ids:
        return 0
    p = _path()
    if not p.exists():
        return 0
    consume = set(consumed_ids)
    survivors: list[str] = []
    removed = 0
    with p.open("r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if not stripped:
                continue
            try:
                rec = json.loads(stripped)
            except json.JSONDecodeError:
                survivors.append(stripped)  # keep unparseable lines, don't lose data
                continue
            if rec.get("id") in consume:
                removed += 1
            else:
                survivors.append(stripped)
    tmp = p.with_suffix(p.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        for s in survivors:
            f.write(s + "\n")
    tmp.replace(p)  # atomic swap
    return removed
