"""The retrieval socket — Protocols + DTOs.

Plugins (vibe.retrieval.providers entry points) import ONLY this module.
The axiom that shapes every contract here: files are the source of truth; the
index is a derived, rebuildable cache. A backend is the index-card drawer,
never the librarian — it finds, it never judges and it never writes file-ward.

Backends return per-leg ranked candidates (Hit.leg_rank per Hit.source); rank
fusion, the usage term, challenger mixing, and read-time verification all live
in the firewall, so every backend stays dumb and every rank policy lives in
one place (ranking.py).
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Protocol, runtime_checkable

INDEXER_VERSION = 1

# space values
SPACE_MEMORY = "memory"   # curated/derived gist rows (the two-hop's first hop)
SPACE_FILE = "file"       # mechanical chunks of the markdown itself

# provenance values — sweep may never overwrite dream surfaces (doc 12 C2)
PROV_DREAM = "dream"
PROV_SWEEP = "sweep"


def memory_id(space: str, source_path: str, anchor: str) -> str:
    """Deterministic row ID: stable across re-index and across backends, so
    usage counters (core store) rejoin their rows after any rebuild."""
    raw = "\x00".join((space, source_path, anchor)).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def content_hash(data: bytes | str) -> str:
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


@dataclass
class Surface:
    """One embeddable text per row per surface name (gist · trigger ·
    hyde_question · abstract). content_hash gates re-embeds."""
    name: str
    text: str
    content_hash: str


@dataclass
class Memory:
    id: str
    kind: str                      # case | note | schema | person | event | chunk | ...
    space: str                     # SPACE_MEMORY | SPACE_FILE
    content: str                   # the gist / chunk text (the FTS surface)
    pointer: dict                  # {"file": rel, "anchor": ...} or {"day": "YYYY-MM-DD", "span": ["HH:MM","HH:MM"]}
    source_path: str               # repo-relative, ALWAYS posix forward slashes
    source_hash: str               # sha256 of the source file bytes at derive time
    provenance: str = PROV_SWEEP
    topic: str | None = None
    bubble: str | None = None
    created_at: datetime | None = None
    meta: dict = field(default_factory=dict)
    surfaces: list[Surface] = field(default_factory=list)


@dataclass
class Query:
    text: str
    space: str = SPACE_MEMORY
    surface: str | None = None     # match a specific embedded surface (situation->trigger, ...)
    kind: str | None = None
    topic: str | None = None
    bubble: str | None = None
    since: datetime | None = None
    k: int = 8
    candidates: int = 50           # per-leg candidate depth a backend must return


@dataclass
class Hit:
    memory: Memory
    source: str                    # 'fts' | 'vector' | 'keys' | 'grep'
    leg_rank: int                  # 1-based rank within its leg
    raw_score: float | None = None
    stale: bool = False            # set by the firewall's read-time verification


@dataclass
class Capabilities:
    name: str
    fts: bool
    vector: bool
    spaces: set[str]
    concurrent_writers: bool
    persistent: bool               # False for the files floor (nothing stored)


@dataclass
class IndexReport:
    upserted: int = 0
    embedded: int = 0
    skipped: int = 0
    evicted: int = 0
    errors: list[str] = field(default_factory=list)

    def merged(self, other: "IndexReport") -> "IndexReport":
        return IndexReport(
            self.upserted + other.upserted,
            self.embedded + other.embedded,
            self.skipped + other.skipped,
            self.evicted + other.evicted,
            self.errors + other.errors,
        )


@runtime_checkable
class Embedder(Protocol):
    dim: int
    model: str

    def embed(self, texts: list[str], task: str) -> list[list[float]]: ...


@runtime_checkable
class RetrievalBackend(Protocol):
    """Constructor convention: Backend(root_dir: Path, config: dict, embedder: Embedder | None)."""

    def capabilities(self) -> Capabilities: ...

    def migrate(self) -> None: ...

    def schema(self) -> str: ...

    def index(self, rows: list[Memory]) -> IndexReport: ...

    def search(self, q: Query) -> list[Hit]: ...

    def evict(self, ids: list[str]) -> None: ...


def rel_posix(path: Path, root: Path) -> str:
    """Repo-relative posix string — the only path form stored or hashed."""
    return path.relative_to(root).as_posix()
