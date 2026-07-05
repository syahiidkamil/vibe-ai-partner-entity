"""CoreStore — the core-owned sqlite: manifest + usage + reindex queue.

Deliberately a SEPARATE file from any plugin's index store, because the
lifecycles differ: the plugin index is derived-from-files and disposable
(`--full` drops it); usage is LIVED history that no rebuild can re-derive,
and the manifest/queue are the sweeper's working state. Deterministic row IDs
are what let usage rejoin rebuilt rows automatically.

stdlib sqlite3 only; WAL + busy_timeout; every write is best-effort-friendly
(callers wrap in try/except — a locked counter must never fail a recall).
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .interface import INDEXER_VERSION
from .ranking import UsageRow

_DDL = """
CREATE TABLE IF NOT EXISTS manifest (
  path TEXT PRIMARY KEY,
  content_hash TEXT NOT NULL,
  mtime REAL NOT NULL,
  size INTEGER NOT NULL,
  last_indexed_at TEXT NOT NULL,
  indexer_version INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS usage (
  memory_id TEXT PRIMARY KEY,
  recalled INTEGER NOT NULL DEFAULT 0,
  dereferenced INTEGER NOT NULL DEFAULT 0,
  helped INTEGER NOT NULL DEFAULT 0,
  hurt INTEGER NOT NULL DEFAULT 0,
  neutral INTEGER NOT NULL DEFAULT 0,
  last_recalled_at TEXT,
  last_dereferenced_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_usage_recalled ON usage(recalled);
CREATE TABLE IF NOT EXISTS reindex_queue (
  path TEXT PRIMARY KEY,
  reason TEXT NOT NULL,
  enqueued_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT);
"""


@dataclass
class ManifestRow:
    path: str
    content_hash: str
    mtime: float
    size: int
    indexer_version: int


class CoreStore:
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.db_path), timeout=3.0)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA busy_timeout=3000")
        self._conn.executescript(_DDL)
        self._conn.commit()

    def close(self) -> None:
        try:
            self._conn.close()
        except Exception:
            pass

    # -- sweep lock (doc 12 C1: skip, never block a turn) --------------------

    def try_begin_sweep(self) -> bool:
        try:
            self._conn.execute("BEGIN IMMEDIATE")
            return True
        except sqlite3.OperationalError:
            return False

    def end_sweep(self) -> None:
        try:
            self._conn.commit()
        except Exception:
            pass

    # -- manifest ------------------------------------------------------------

    def manifest_all(self) -> dict[str, ManifestRow]:
        cur = self._conn.execute(
            "SELECT path, content_hash, mtime, size, indexer_version FROM manifest")
        return {r[0]: ManifestRow(*r) for r in cur.fetchall()}

    def manifest_upsert(self, path: str, content_hash: str, mtime: float, size: int, now_iso: str) -> None:
        self._conn.execute(
            "INSERT INTO manifest(path, content_hash, mtime, size, last_indexed_at, indexer_version)"
            " VALUES(?,?,?,?,?,?)"
            " ON CONFLICT(path) DO UPDATE SET content_hash=excluded.content_hash,"
            " mtime=excluded.mtime, size=excluded.size,"
            " last_indexed_at=excluded.last_indexed_at, indexer_version=excluded.indexer_version",
            (path, content_hash, mtime, size, now_iso, INDEXER_VERSION),
        )

    def manifest_delete(self, paths: list[str]) -> None:
        self._conn.executemany("DELETE FROM manifest WHERE path=?", [(p,) for p in paths])

    def manifest_clear(self) -> None:
        self._conn.execute("DELETE FROM manifest")

    # -- usage ----------------------------------------------------------------

    def usage_rows(self, ids: set[str]) -> dict[str, UsageRow]:
        if not ids:
            return {}
        marks = ",".join("?" * len(ids))
        cur = self._conn.execute(
            f"SELECT memory_id, recalled, dereferenced, helped, hurt, last_recalled_at"
            f" FROM usage WHERE memory_id IN ({marks})", list(ids))
        out = {}
        for mid, rec, der, helped, hurt, last in cur.fetchall():
            dt = None
            if last:
                try:
                    dt = datetime.fromisoformat(last)
                except ValueError:
                    dt = None
            out[mid] = UsageRow(recalled=rec, dereferenced=der, helped=helped,
                                hurt=hurt, last_recalled_at=dt)
        return out

    def bump_recalled(self, ids: list[str], now_iso: str) -> None:
        self._conn.executemany(
            "INSERT INTO usage(memory_id, recalled, last_recalled_at) VALUES(?,1,?)"
            " ON CONFLICT(memory_id) DO UPDATE SET recalled=recalled+1,"
            " last_recalled_at=excluded.last_recalled_at",
            [(i, now_iso) for i in ids],
        )
        self._conn.commit()

    def bump_dereferenced(self, mem_id: str, now_iso: str) -> None:
        self._conn.execute(
            "INSERT INTO usage(memory_id, dereferenced, last_dereferenced_at) VALUES(?,1,?)"
            " ON CONFLICT(memory_id) DO UPDATE SET dereferenced=dereferenced+1,"
            " last_dereferenced_at=excluded.last_dereferenced_at",
            (mem_id, now_iso),
        )
        self._conn.commit()

    # -- reindex queue ---------------------------------------------------------

    def enqueue_reindex(self, path: str, reason: str) -> None:
        from datetime import timezone
        self._conn.execute(
            "INSERT OR REPLACE INTO reindex_queue(path, reason, enqueued_at) VALUES(?,?,?)",
            (path, reason, datetime.now(timezone.utc).isoformat()),
        )
        self._conn.commit()

    def drain_reindex(self) -> list[str]:
        cur = self._conn.execute("SELECT path FROM reindex_queue")
        paths = [r[0] for r in cur.fetchall()]
        self._conn.execute("DELETE FROM reindex_queue")
        return paths

    def queue_depth(self) -> int:
        return self._conn.execute("SELECT COUNT(*) FROM reindex_queue").fetchone()[0]

    # -- meta -------------------------------------------------------------------

    def meta_set(self, key: str, value: str) -> None:
        self._conn.execute(
            "INSERT OR REPLACE INTO meta(key, value) VALUES(?,?)", (key, value))
        self._conn.commit()

    def meta_get(self, key: str) -> str | None:
        row = self._conn.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
        return row[0] if row else None

    # -- stats (the dogma thermometer's raw numbers) ------------------------------

    def usage_distribution(self) -> dict:
        c = self._conn
        total = c.execute("SELECT COUNT(*) FROM usage").fetchone()[0]
        never = c.execute("SELECT COUNT(*) FROM usage WHERE recalled=0").fetchone()[0]
        top = c.execute(
            "SELECT memory_id, recalled, dereferenced FROM usage"
            " ORDER BY recalled DESC LIMIT 10").fetchall()
        undereferenced = c.execute(
            "SELECT memory_id, recalled FROM usage"
            " WHERE recalled >= 3 AND dereferenced = 0"
            " ORDER BY recalled DESC LIMIT 10").fetchall()
        total_recalls = c.execute("SELECT COALESCE(SUM(recalled),0) FROM usage").fetchone()[0]
        head = c.execute(
            "SELECT COALESCE(SUM(recalled),0) FROM"
            " (SELECT recalled FROM usage ORDER BY recalled DESC LIMIT 10)").fetchone()[0]
        return {
            "tracked": total,
            "never_recalled": never,
            "top_recalled": top,
            "recalled_never_dereferenced": undereferenced,
            "total_recalls": total_recalls,
            "head_share": (head / total_recalls) if total_recalls else 0.0,
        }
