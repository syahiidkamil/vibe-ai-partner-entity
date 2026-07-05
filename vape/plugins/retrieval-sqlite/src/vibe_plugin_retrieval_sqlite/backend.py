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
        self._vec_ok = False
        self._sqlite_vec = None   # set by _probe_vec on success

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
        self._probe_vec()
        self._conn.commit()

    def _probe_vec(self) -> None:
        """Vectors need BOTH the loadable extension AND an embedder — probed,
        never assumed (some Python builds compile out extension loading)."""
        self._vec_ok = False
        if self.embedder is None or getattr(self.embedder, "dim", 0) <= 0:
            return
        try:
            import sqlite_vec
            self._conn.enable_load_extension(True)
            sqlite_vec.load(self._conn)
            self._conn.enable_load_extension(False)
            self._conn.execute(
                "CREATE VIRTUAL TABLE IF NOT EXISTS vec_embeddings"
                f" USING vec0(embedding float[{self.embedder.dim}])"
            )
            self._sqlite_vec = sqlite_vec
            self._vec_ok = True
        except Exception:
            self._vec_ok = False

    def reset(self) -> None:
        self._conn.executescript(ddl.DROP_ALL)
        try:
            self._conn.execute("DROP TABLE IF EXISTS vec_embeddings")
        except sqlite3.OperationalError:
            pass   # extension not loaded this session; table can't exist either
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
        if self._vec_ok:
            rep.embedded = self._embed_pending(rows)
            self._gc_vectors()
        self._conn.commit()
        return rep

    def _embed_pending(self, rows: list[Memory]) -> int:
        """Hash-gated gist embedding, memory-space rows only (the distilled
        surface; file-space chunks stay FTS-only — volatile and plentiful,
        doc 04's cost discipline). Re-embeds ONLY when the gist text changed."""
        model = self.embedder.model
        todo: list[Memory] = []
        for r in rows:
            if r.space != "memory" or not r.content.strip():
                continue
            h = content_hash(r.content)
            row = self._conn.execute(
                "SELECT content_hash FROM embeddings"
                " WHERE memory_id=? AND surface='gist' AND model=?",
                (r.id, model)).fetchone()
            if row and row[0] == h:
                continue
            todo.append(r)
        if not todo:
            return 0
        done = 0
        CHUNK = 100
        for start in range(0, len(todo), CHUNK):
            chunk = todo[start:start + CHUNK]
            vectors = self.embedder.embed([r.content for r in chunk], task="document")
            # strict: a count mismatch must EXPLODE here, never truncate silently
            # (the zip that hid the one-embedding-per-batch bug, 2026-07-05)
            for r, vec in zip(chunk, vectors, strict=True):
                cur = self._conn.execute(
                    "INSERT INTO embeddings(memory_id, surface, text, model, dim, content_hash)"
                    " VALUES(?,?,?,?,?,?)"
                    " ON CONFLICT(memory_id, surface, model) DO UPDATE SET"
                    " text=excluded.text, dim=excluded.dim, content_hash=excluded.content_hash"
                    " RETURNING id",
                    (r.id, "gist", r.content, model, self.embedder.dim, content_hash(r.content)),
                )
                emb_id = cur.fetchone()[0]
                self._conn.execute("DELETE FROM vec_embeddings WHERE rowid=?", (emb_id,))
                self._conn.execute(
                    "INSERT INTO vec_embeddings(rowid, embedding) VALUES(?,?)",
                    (emb_id, self._sqlite_vec.serialize_float32(vec)),
                )
            # commit per chunk: a quota abort keeps its progress; the next run
            # resumes from the hash gate instead of starting over
            self._conn.commit()
            done += len(chunk)
        return done

    def _gc_vectors(self) -> None:
        """vec0 has no foreign keys: sweep vectors whose embeddings row died
        (cascade from a memories delete)."""
        self._conn.execute(
            "DELETE FROM vec_embeddings WHERE rowid NOT IN (SELECT id FROM embeddings)")

    def backfill(self) -> int:
        """Embed stored rows that lack a current-model gist vector — the
        self-reconcile that makes 'add the key later, just re-run index' true,
        and the tracked path a model swap re-embeds through. File-level change
        detection can't see this: embedding state is row-level, in-store."""
        if not self._vec_ok:
            return 0
        cur = self._conn.execute(
            "SELECT m.id, m.kind, m.space, m.content, m.topic, m.bubble, m.created_at,"
            " m.pointer, m.meta, m.provenance, m.source_path, m.source_hash"
            " FROM memories m LEFT JOIN embeddings e"
            "   ON e.memory_id = m.id AND e.surface='gist' AND e.model=?"
            " WHERE m.space='memory' AND m.content != '' AND e.id IS NULL",
            (self.embedder.model,),
        )
        rows = [_row_to_memory(r) for r in cur.fetchall()]
        if not rows:
            return 0
        n = self._embed_pending(rows)
        self._gc_vectors()
        self._conn.commit()
        return n

    def evict(self, ids: list[str]) -> None:
        self._conn.executemany("DELETE FROM memories WHERE id=?", [(i,) for i in ids])
        self._conn.commit()

    def evict_sources(self, source_paths: list[str]) -> None:
        self._conn.executemany(
            "DELETE FROM memories WHERE source_path=?", [(p,) for p in source_paths])
        self._conn.commit()

    # -- search -------------------------------------------------------------------

    def search(self, q: Query) -> list[Hit]:
        hits = self._search_fts(q)
        hits.extend(self._search_vector(q))
        return hits

    def _search_fts(self, q: Query) -> list[Hit]:
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

    def _search_vector(self, q: Query) -> list[Hit]:
        """KNN over the gist surface, filtered to ONE (surface, model) pair —
        vectors from different models are never compared. vec0 cannot filter
        joined columns, so over-fetch then filter in the join."""
        if not self._vec_ok or q.space != "memory":
            return []
        qvec = self.embedder.embed([q.text], task="query")[0]
        if not qvec:
            return []
        knn = self._conn.execute(
            "SELECT rowid, distance FROM vec_embeddings"
            " WHERE embedding MATCH ? AND k = ?",
            (self._sqlite_vec.serialize_float32(qvec), q.candidates * 4),
        ).fetchall()
        if not knn:
            return []
        by_emb = {r[0]: r[1] for r in knn}
        marks = ",".join("?" * len(by_emb))
        cur = self._conn.execute(
            "SELECT m.id, m.kind, m.space, m.content, m.topic, m.bubble, m.created_at,"
            " m.pointer, m.meta, m.provenance, m.source_path, m.source_hash, e.id"
            " FROM embeddings e JOIN memories m ON m.id = e.memory_id"
            f" WHERE e.id IN ({marks}) AND e.surface='gist' AND e.model=?",
            [*by_emb.keys(), self.embedder.model],
        )
        rows = []
        for row in cur.fetchall():
            m = _row_to_memory(row)
            if q.kind and m.kind != q.kind:
                continue
            if q.topic and m.topic != q.topic:
                continue
            if q.bubble and m.bubble != q.bubble:
                continue
            if q.since and (m.created_at is None or m.created_at < q.since):
                continue
            rows.append((by_emb[row[12]], m))
        rows.sort(key=lambda t: t[0])
        return [
            Hit(memory=m, source="vector", leg_rank=i, raw_score=dist)
            for i, (dist, m) in enumerate(rows[: q.candidates], start=1)
        ]


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
