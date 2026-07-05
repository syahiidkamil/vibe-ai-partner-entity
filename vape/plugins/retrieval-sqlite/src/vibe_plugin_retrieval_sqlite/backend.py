"""SqliteBackend — FTS5 keyword search over the index; sqlite-vec vectors when
both the extension and an embedder are present (S3).

A dumb drawer on purpose: per-leg ranked candidates out, no fusion, no usage,
no judgment. index() is a per-source-file reconcile; reset() drops in-
connection (never deletes the db file — Windows can't unlink open files).
"""
from __future__ import annotations

import json
import re
import sqlite3
from datetime import datetime
from pathlib import Path

from engine.memory.interface import (
    Capabilities,
    Hit,
    IndexReport,
    Memory,
    Query,
    content_hash,
)
from . import ddl

_TOKEN_RE = re.compile(r"[a-zA-Z0-9]+")


class SqliteBackend:
    def __init__(self, root_dir: Path, config: dict | None = None, embedder=None):
        config = config or {}
        self.root = Path(root_dir)
        self.embedder = embedder
        db_path = config.get("dbPath")
        self.db_path = (
            Path(db_path) if db_path
            else self.root / "vape" / "entity" / "storage" / "index" / "index.db"
        )
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.db_path), timeout=3.0)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA busy_timeout=3000")
        self._conn.execute("PRAGMA foreign_keys=ON")
        self._fts_ok = False
        self._vec_ok = False   # S3: sqlite-vec probe lands here

    # -- lifecycle -----------------------------------------------------------

    def migrate(self) -> None:
        self._conn.executescript(ddl.MEMORIES)
        self._conn.executescript(ddl.EMBEDDINGS)
        try:
            self._conn.executescript(ddl.FTS)
            self._fts_ok = True
        except sqlite3.OperationalError as e:
            # exotic Python builds without FTS5: the factory degrades to the
            # floor when neither leg works; be honest, never crash
            raise RuntimeError(f"sqlite build lacks FTS5 ({e})")
        self._conn.commit()

    def reset(self) -> None:
        self._conn.executescript(ddl.DROP_ALL)
        self._conn.commit()
        self._conn.execute("VACUUM")
        self.migrate()

    def capabilities(self) -> Capabilities:
        return Capabilities(
            name="sqlite",
            fts=self._fts_ok,
            vector=self._vec_ok,
            spaces={"memory", "file"},
            concurrent_writers=False,
            persistent=True,
        )

    def schema(self) -> str:
        cur = self._conn.execute(
            "SELECT sql FROM sqlite_master WHERE sql IS NOT NULL ORDER BY name")
        return ";\n\n".join(r[0] for r in cur.fetchall())

    # -- write -----------------------------------------------------------------

    def index(self, rows: list[Memory]) -> IndexReport:
        rep = IndexReport()
        by_source: dict[str, list[Memory]] = {}
        for r in rows:
            by_source.setdefault(r.source_path, []).append(r)
        for source, group in by_source.items():
            ids = [r.id for r in group]
            marks = ",".join("?" * len(ids))
            self._conn.execute(
                f"DELETE FROM memories WHERE source_path=? AND id NOT IN ({marks})",
                [source, *ids],
            )
            for r in group:
                self._conn.execute(
                    "INSERT INTO memories(id, kind, space, content, topic, bubble,"
                    " created_at, pointer, meta, provenance, source_path, source_hash)"
                    " VALUES(?,?,?,?,?,?,?,?,?,?,?,?)"
                    " ON CONFLICT(id) DO UPDATE SET kind=excluded.kind,"
                    " space=excluded.space, content=excluded.content,"
                    " topic=excluded.topic, bubble=excluded.bubble,"
                    " created_at=excluded.created_at, pointer=excluded.pointer,"
                    " meta=excluded.meta, provenance=CASE WHEN memories.provenance='dream'"
                    "   AND excluded.provenance='sweep' THEN 'dream' ELSE excluded.provenance END,"
                    " source_path=excluded.source_path, source_hash=excluded.source_hash",
                    (
                        r.id, r.kind, r.space, r.content, r.topic, r.bubble,
                        r.created_at.isoformat() if r.created_at else None,
                        json.dumps(r.pointer, ensure_ascii=False),
                        json.dumps(r.meta, ensure_ascii=False),
                        r.provenance, r.source_path, r.source_hash,
                    ),
                )
                rep.upserted += 1
        self._conn.commit()
        return rep

    def evict(self, ids: list[str]) -> None:
        self._conn.executemany("DELETE FROM memories WHERE id=?", [(i,) for i in ids])
        self._conn.commit()

    def evict_sources(self, source_paths: list[str]) -> None:
        self._conn.executemany(
            "DELETE FROM memories WHERE source_path=?", [(p,) for p in source_paths])
        self._conn.commit()

    # -- search -------------------------------------------------------------------

    def search(self, q: Query) -> list[Hit]:
        if not self._fts_ok:
            return []
        tokens = _TOKEN_RE.findall(q.text)
        if not tokens:
            return []
        match = " OR ".join(f'"{t}"' for t in tokens)

        where, params = ["m.space = ?"], [q.space]
        if q.kind:
            where.append("m.kind = ?")
            params.append(q.kind)
        if q.topic:
            where.append("m.topic = ?")
            params.append(q.topic)
        if q.bubble:
            where.append("m.bubble = ?")
            params.append(q.bubble)
        if q.since:
            where.append("m.created_at >= ?")
            params.append(q.since.isoformat())

        sql = (
            "SELECT m.id, m.kind, m.space, m.content, m.topic, m.bubble, m.created_at,"
            " m.pointer, m.meta, m.provenance, m.source_path, m.source_hash,"
            " bm25(memories_fts) AS rank"
            " FROM memories_fts f JOIN memories m ON m.rowid = f.rowid"
            f" WHERE memories_fts MATCH ? AND {' AND '.join(where)}"
            " ORDER BY rank LIMIT ?"
        )
        cur = self._conn.execute(sql, [match, *params, q.candidates])
        hits = []
        for leg_rank, row in enumerate(cur.fetchall(), start=1):
            hits.append(Hit(
                memory=_row_to_memory(row), source="fts",
                leg_rank=leg_rank, raw_score=row[12],
            ))
        return hits


def _row_to_memory(row) -> Memory:
    created = None
    if row[6]:
        try:
            created = datetime.fromisoformat(row[6])
        except ValueError:
            created = None
    return Memory(
        id=row[0], kind=row[1], space=row[2], content=row[3],
        topic=row[4], bubble=row[5], created_at=created,
        pointer=json.loads(row[7]), meta=json.loads(row[8]),
        provenance=row[9], source_path=row[10], source_hash=row[11],
    )
