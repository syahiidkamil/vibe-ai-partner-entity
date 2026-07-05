"""QmdBackend — the exemplar third-party adapter: a user-installed qmd binary
(github.com/tobi/qmd) serving keyless local vector search over the memory
files. File-space ONLY: memory-space queries fall to the files floor via the
firewall's space routing — a deliberately partial backend, proving that
capabilities-honesty is enough for a plugin to be useful.

Everything defensive by design: the binary probed with shutil.which (resolves
.exe on Windows), argv subprocess only (never shell=True), any parse failure
returns an empty leg with the floor still answering underneath.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from engine.memory.interface import (
    SPACE_FILE,
    Capabilities,
    Hit,
    IndexReport,
    Memory,
    Query,
    content_hash,
    memory_id,
    rel_posix,
)

COLLECTION = "vape-memory"


class QmdBackend:
    def __init__(self, root_dir: Path, config: dict | None = None, embedder=None):
        config = config or {}
        self.root = Path(root_dir)
        self.binary = shutil.which(config.get("binary", "qmd"))
        if not self.binary:
            raise RuntimeError(
                "qmd binary not found on PATH (install: github.com/tobi/qmd; needs Node >= 22)")
        self.collection = config.get("collection", COLLECTION)

    # -- lifecycle -----------------------------------------------------------

    def migrate(self) -> None:
        """Ensure the collection covers the entity markdown. Idempotent; any
        qmd CLI drift lands here loudly, not in search."""
        entity = self.root / "vape" / "entity"
        existing = self._run(["collection", "list", "--json"])
        names = []
        if existing is not None:
            try:
                names = [c.get("name") for c in json.loads(existing)]
            except Exception:
                names = []
        if self.collection not in names:
            self._run([
                "collection", "add", str(entity),
                "--name", self.collection, "--mask", "**/*.md",
            ])

    def reset(self) -> None:
        return   # qmd owns its index; rebuild via its own CLI

    def capabilities(self) -> Capabilities:
        return Capabilities(
            name="qmd",
            fts=True,          # BM25 inside qmd
            vector=True,       # local GGUF embeddings inside qmd
            spaces={SPACE_FILE},
            concurrent_writers=False,
            persistent=True,
        )

    def schema(self) -> str:
        out = self._run(["--version"])
        return f"qmd adapter (binary: {self.binary}, version: {(out or 'unknown').strip()}, collection: {self.collection})"

    # -- write (qmd tends its own store) ---------------------------------------

    def index(self, rows: list[Memory]) -> IndexReport:
        return IndexReport(skipped=len(rows))

    def backfill(self) -> int:
        """`vape memory index` maps to qmd's own update+embed pass."""
        self._run(["update"])
        self._run(["embed"])
        return 0

    def evict(self, ids: list[str]) -> None:
        return

    def evict_sources(self, source_paths: list[str]) -> None:
        return

    # -- search ------------------------------------------------------------------

    def search(self, q: Query) -> list[Hit]:
        if q.space != SPACE_FILE:
            return []
        out = self._run([
            "search", q.text, "--json", "-n", str(q.candidates),
            "-c", self.collection,
        ])
        if out is None:
            return []
        try:
            results = json.loads(out)
        except Exception:
            return []
        hits: list[Hit] = []
        for rank, r in enumerate(results if isinstance(results, list) else [], start=1):
            try:
                hits.append(self._to_hit(r, rank))
            except Exception:
                continue   # one malformed row never kills the leg
        return hits

    def _to_hit(self, r: dict, rank: int) -> Hit:
        raw_path = r.get("file") or r.get("path") or r.get("filepath") or ""
        p = Path(raw_path)
        try:
            src = rel_posix(p, self.root) if p.is_absolute() else Path(raw_path).as_posix()
        except ValueError:
            src = Path(raw_path).as_posix()
        snippet = (r.get("snippet") or r.get("text") or r.get("content") or "")[:400]
        target = self.root / Path(src)
        h = content_hash(target.read_bytes()) if target.is_file() else ""
        m = Memory(
            id=memory_id(SPACE_FILE, src, f"qmd:{rank}"),
            kind="chunk", space=SPACE_FILE, content=snippet or src,
            pointer={"file": src, "anchor": ""},
            source_path=src, source_hash=h,
        )
        return Hit(memory=m, source="vector", leg_rank=rank,
                   raw_score=r.get("score"))

    # -- subprocess (argv only, never shell) ---------------------------------------

    def _run(self, args: list[str]) -> str | None:
        try:
            proc = subprocess.run(
                [self.binary, *args],
                capture_output=True, text=True, timeout=120, shell=False,
            )
            return proc.stdout if proc.returncode == 0 else None
        except Exception:
            return None
