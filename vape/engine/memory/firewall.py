"""The firewall — the organ-side API over any RetrievalBackend.

Owns everything a backend must never own: rank fusion + the usage whisper +
challenger mixing (ranking.py), read-time verification (a hit is checked
against its source before I lean on it — stale is flagged, never silent),
usage counting (best-effort, never fails a recall), and dereference (the
two-hop's second hop).

Recall stays read-pure: a dirty reindex queue is reported, never auto-swept.
"""
from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from . import ranking
from .interface import (
    SPACE_FILE,
    SPACE_MEMORY,
    Capabilities,
    Query,
    RetrievalBackend,
    content_hash,
)

SPACE_ALL = "all"


@dataclass
class RecallHit:
    id: str
    score: float
    relevance: float
    strength: float
    challenger: bool
    stale: bool
    kind: str
    space: str
    topic: str | None
    bubble: str | None
    provenance: str
    content: str
    pointer: dict
    source_path: str
    sources: list[str]


@dataclass
class RecallResult:
    query: str
    backend: str
    capabilities: Capabilities
    explore: bool
    space: str
    hits: list[RecallHit] = field(default_factory=list)

    def to_json(self) -> dict:
        return {
            "query": self.query,
            "backend": self.backend,
            "capabilities": {
                "fts": self.capabilities.fts,
                "vector": self.capabilities.vector,
                "spaces": sorted(self.capabilities.spaces),
            },
            "explore": self.explore,
            "space": self.space,
            "hits": [vars(h) for h in self.hits],
        }


class Firewall:
    def __init__(
        self,
        backend: RetrievalBackend,
        root_dir: Path,
        floor: RetrievalBackend | None = None,
        core_store=None,           # CoreStore (S2+); None on the bare floor
    ):
        self.backend = backend
        self.floor = floor
        self.core = core_store
        self.root = Path(root_dir)
        self.cache_dir = self.root / "vape" / "entity" / "storage" / "index"

    # -- recall ------------------------------------------------------------

    def recall(
        self,
        text: str,
        space: str = SPACE_MEMORY,
        kind: str | None = None,
        topic: str | None = None,
        bubble: str | None = None,
        k: int = 8,
        explore: bool = False,
    ) -> RecallResult:
        caps = self.backend.capabilities()
        spaces = [SPACE_MEMORY, SPACE_FILE] if space == SPACE_ALL else [space]
        candidates = 100 if explore else 50

        legs = []
        for sp in spaces:
            target = self.backend if sp in caps.spaces else (self.floor or self.backend)
            legs.extend(target.search(Query(
                text=text, space=sp, kind=kind, topic=topic, bubble=bubble,
                k=k, candidates=candidates,
            )))

        usage = self._usage_rows({h.memory.id for h in legs})
        scored = ranking.fuse(legs, usage, k=k, explore=explore)

        result = RecallResult(
            query=text, backend=caps.name, capabilities=caps,
            explore=explore, space=space,
        )
        now = datetime.now(timezone.utc).isoformat()
        for s in scored:
            m = s.hit.memory
            stale = self._verify(m.source_path, m.source_hash)
            result.hits.append(RecallHit(
                id=m.id, score=round(s.score, 4), relevance=round(s.relevance, 4),
                strength=round(s.strength, 4), challenger=s.challenger, stale=stale,
                kind=m.kind, space=m.space, topic=m.topic, bubble=m.bubble,
                provenance=m.provenance, content=m.content, pointer=m.pointer,
                source_path=m.source_path, sources=sorted(set(s.sources)),
            ))
            if stale:
                self._enqueue_reindex(m.source_path)
        self._count_recalled([h.id for h in result.hits], now)
        self._write_cache(result)
        return result

    # -- read-time verification (doc 12 loop 3) ------------------------------

    def _verify(self, source_path: str, recorded_hash: str) -> bool:
        """True = STALE. mtime may shortlist elsewhere; here only content asserts."""
        target = self.root / Path(source_path)
        if not target.is_file():
            return True
        try:
            return content_hash(target.read_bytes()) != recorded_hash
        except OSError:
            return True

    def _enqueue_reindex(self, source_path: str) -> None:
        if self.core is not None:
            try:
                self.core.enqueue_reindex(source_path, reason="stale-hit")
            except Exception:
                pass

    # -- usage (best-effort; the _bookmark.py swallow pattern) ---------------

    def _usage_rows(self, ids: set[str]) -> dict[str, ranking.UsageRow]:
        if self.core is None or not ids:
            return {}
        try:
            return self.core.usage_rows(ids)
        except Exception:
            return {}

    def _count_recalled(self, ids: list[str], now_iso: str) -> None:
        if self.core is None or not ids:
            return
        try:
            self.core.bump_recalled(ids, now_iso)
        except Exception:
            pass

    def count_dereferenced(self, mem_id: str) -> None:
        if self.core is None:
            return
        try:
            self.core.bump_dereferenced(mem_id, datetime.now(timezone.utc).isoformat())
        except Exception:
            pass

    # -- deref: the second hop ----------------------------------------------

    def deref(self, mem_id: str) -> tuple[str, dict] | None:
        """Resolve an id from the last recall's cache and return
        (body_text, pointer). CLI stays stateless between invocations."""
        cached = self._read_cache()
        hit = next((h for h in cached if h.get("id") == mem_id), None)
        if hit is None:
            return None
        body = self._read_pointer(hit["pointer"])
        self.count_dereferenced(mem_id)
        return body, hit["pointer"]

    def _read_pointer(self, pointer: dict) -> str:
        if "file" in pointer:
            target = self.root / Path(pointer["file"])
            if not target.is_file():
                return f"(source file missing: {pointer['file']})"
            text = target.read_text(encoding="utf-8", errors="replace")
            return _extract_anchor(text, pointer.get("anchor", ""))
        if "day" in pointer:
            return "(storage-window dereference arrives with the S2 store)"
        return "(unreadable pointer)"

    # -- the last-recall cache (deref resolution without a store) ------------

    def _write_cache(self, result: RecallResult) -> None:
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            payload = json.dumps(
                {"at": datetime.now(timezone.utc).isoformat(),
                 "hits": [vars(h) for h in result.hits]},
                ensure_ascii=False, indent=1)
            fd, tmp = tempfile.mkstemp(dir=str(self.cache_dir), prefix=".tmp")
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(payload)
            os.replace(tmp, str(self.cache_dir / "last_recall.json"))
        except Exception:
            pass

    def _read_cache(self) -> list[dict]:
        try:
            raw = (self.cache_dir / "last_recall.json").read_text(encoding="utf-8")
            return json.loads(raw).get("hits", [])
        except Exception:
            return []


def _extract_anchor(text: str, anchor: str) -> str:
    """Print the anchored slice: a case block, a note bullet, a heading
    section, a living-keys line, or the head of the file."""
    lines = text.splitlines()
    if anchor.startswith("line:"):
        i = int(anchor.split(":", 1)[1])
        return lines[i] if 0 <= i < len(lines) else text[:400]
    if anchor.startswith("bullet:"):
        n, ordinal = int(anchor.split(":", 1)[1]), 0
        for line in lines:
            if line.startswith("- "):
                ordinal += 1
                if ordinal == n:
                    return line[2:].strip()
        return text[:400]
    if anchor and anchor not in ("doc",):
        # case slug (### id: <slug> ...) or a heading section
        out, capturing = [], False
        for line in lines:
            is_head = line.startswith("#")
            if capturing and is_head:
                break
            if not capturing and is_head and anchor in line:
                capturing = True
            if capturing:
                out.append(line)
        if out:
            return "\n".join(out).strip()
    return "\n".join(lines[:60]).strip()
