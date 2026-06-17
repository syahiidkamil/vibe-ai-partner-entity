"""Bookmark capture, gate 1 of the memory spine.

A bookmark is NOT a memory. It is a cheap one-line flag dropped live that says "this
moment mattered, consider it at consolidation." It appends to a per-day TOON file in
storage/, a sibling of the chats/qualia raw logs. No DB, no embedding, no judgment
happens here; gate 2 (the dream) reads these later, dereferences, and decides what
becomes a real memory. Generous capture, selective keep; cram dies at gate 2.

Best-effort by design: a bookmark write must NEVER break the inner-state write it rides
on, so every failure is swallowed and reported only via the return value.
"""

from __future__ import annotations

import os
import tempfile
from datetime import datetime, timedelta, timezone

from engine.cli import _paths

# The six dials, and their short keys in the row (matching the qualia.toon convention).
DIAL_KEYS = ("info_value_saturation", "talkativeness", "warmth", "hurt", "dissonance", "mastery")
_SHORT = {
    "info_value_saturation": "sat",
    "talkativeness": "talk",
    "warmth": "warmth",
    "hurt": "hurt",
    "dissonance": "diss",
    "mastery": "mastery",
}


def _now_wib() -> datetime:
    """Current time in WIB (UTC+7), matching how the capture hook stamps the raw logs."""
    return datetime.now(timezone.utc) + timedelta(hours=7)


def _path_for(day: str):
    y, m, _ = day.split("-")
    return _paths.ROOT_DIR / "vape" / "entity" / "storage" / y / m / f"{day}_bookmarks.toon"


def _key(r: dict) -> tuple:
    """Dedup key: a bookmark is identified by its time, gist, and source."""
    return (r.get("time", ""), r.get("gist", ""), r.get("source", ""))


def append_bookmark(gist: str, dials: dict | None = None, source: str = "willed") -> bool:
    """Append one bookmark row to today's bookmarks.toon. Return True on success.

    The row is flat (TOON-friendly, matching the chats/qualia rows): the capture time
    (which doubles as the dereference handle into the same-day raw TOON, since the file
    is already per-day), the gist, the six-dial salience snapshot, and the source. Loads
    the existing file, dedups by (time, gist, source), sorts by time, atomic-writes.

    Best-effort: any failure returns False and never raises, so the caller's inner-state
    write is untouched.
    """
    try:
        import toons

        dials = dials or {}
        now = _now_wib()
        day = now.strftime("%Y-%m-%d")
        row = {"time": now.strftime("%H:%M:%S"), "gist": gist}
        for k in DIAL_KEYS:
            row[_SHORT[k]] = dials.get(k, "")
        row["source"] = source

        path = _path_for(day)
        path.parent.mkdir(parents=True, exist_ok=True)

        rows: dict = {}
        if path.is_file():
            try:
                for r in (toons.loads(path.read_text(encoding="utf-8")).get("bookmarks") or []):
                    rows[_key(r)] = r
            except Exception:
                pass
        rows[_key(row)] = row
        ordered = sorted(rows.values(), key=lambda r: r.get("time", ""))

        enc = toons.dumps({"bookmarks": ordered})
        fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(enc if enc.endswith("\n") else enc + "\n")
        os.replace(tmp, str(path))
        return True
    except Exception:
        return False
