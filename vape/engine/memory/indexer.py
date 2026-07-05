"""The sweeper — reconcile the markdown tree into the backend's index.

Doc 12's freshness discipline, coded:
  - the reindex queue drains FIRST (stale hits enqueued by recall);
  - mtime/size SHORTLIST which files to even hash; only the content hash may
    assert a change (the envelope is not the letter — paid for live, 07-05);
  - deterministic IDs + per-file reconcile make any number of concurrent
    sweeps convergent; the core-store sweep lock makes them polite (skip,
    never block);
  - deleted paths evict their rows; archive/ leaves the index by structure
    (it is never in the source walk at all);
  - --full drops the backend store IN-CONNECTION and re-derives everything;
    usage in the core store survives and rejoins by ID.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from . import derive
from .core_store import CoreStore
from .interface import (
    INDEXER_VERSION,
    IndexReport,
    RetrievalBackend,
    content_hash,
    rel_posix,
)


@dataclass
class SweepResult:
    report: IndexReport = field(default_factory=IndexReport)
    files_seen: int = 0
    files_changed: int = 0
    files_deleted: int = 0
    skipped_lock: bool = False


class Indexer:
    def __init__(self, root: Path, core: CoreStore, backend: RetrievalBackend):
        self.root = Path(root)
        self.core = core
        self.backend = backend

    def sweep(self, full: bool = False) -> SweepResult:
        res = SweepResult()
        if not self.core.try_begin_sweep():
            res.skipped_lock = True
            return res
        try:
            if full:
                self.backend.reset()
                self.core.manifest_clear()

            queued = set(self.core.drain_reindex())
            manifest = self.core.manifest_all()
            now_iso = datetime.now(timezone.utc).isoformat()

            sources = derive.all_sources(self.root)
            seen_paths: set[str] = set()
            res.files_seen = len(sources)

            for path in sorted(sources):
                src = rel_posix(path, self.root)
                seen_paths.add(src)
                try:
                    st = path.stat()
                except OSError:
                    continue
                prior = manifest.get(src)
                # a derivation-logic change (INDEXER_VERSION bump) forces a
                # re-derive even though the file bytes never moved — without
                # this, new derivation rules would silently never apply
                forced = (
                    full or src in queued
                    or (prior is not None and prior.indexer_version != INDEXER_VERSION)
                )
                # mtime/size shortlist: skip the hash when the envelope is
                # identical AND nothing forces a look
                if prior and not forced and prior.mtime == st.st_mtime and prior.size == st.st_size:
                    continue
                raw = path.read_bytes()
                h = content_hash(raw)
                if prior and not forced and prior.content_hash == h:
                    # (version matches here by construction — forced covers the rest)
                    # touched but unchanged (git checkout, editor save) — true up the envelope
                    self.core.manifest_upsert(src, h, st.st_mtime, st.st_size, now_iso)
                    continue
                rows = derive.derive_file(self.root, path)
                rep = self.backend.index(rows)
                res.report = res.report.merged(rep)
                res.files_changed += 1
                self.core.manifest_upsert(src, h, st.st_mtime, st.st_size, now_iso)

            dead = [p for p in manifest if p not in seen_paths]
            if dead:
                self.backend.evict_sources(dead)
                self.core.manifest_delete(dead)
                res.files_deleted = len(dead)
                res.report.evicted += len(dead)

            self.core.meta_set("last_sweep_at", now_iso)
        finally:
            self.core.end_sweep()
        return res
