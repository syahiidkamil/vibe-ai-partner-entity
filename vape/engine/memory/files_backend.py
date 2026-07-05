"""FilesBackend — the T0 floor. Always available, zero dependencies, nothing stored.

Two legs, mirroring how the floor is actually lived:
  - 'keys' — the living-keys file (`key -> path`, `cue -> memory` lines), the
    working-memory keyring matched first;
  - 'grep' — a pure-Python token-overlap scan over the SAME rows the indexed
    tiers store (derive.py — one derivation, no drift between tiers).

Pure Python on purpose: no grep/rg subprocess, so the floor is identical on
macOS, Linux, and Windows, and works on a box with no coreutils at all.
source_hash is computed from the bytes just read, so read-time verification
is trivially fresh here — the floor cannot go stale.
"""
from __future__ import annotations

import re
from pathlib import Path

from . import derive
from .interface import (
    SPACE_FILE,
    SPACE_MEMORY,
    Capabilities,
    Hit,
    IndexReport,
    Memory,
    Query,
    content_hash,
    memory_id,
    rel_posix,
)

_TOKEN_RE = re.compile(r"[a-z0-9]+")
_STOP = {
    "the", "a", "an", "of", "to", "in", "on", "and", "or", "for", "is", "are",
    "was", "i", "my", "me", "it", "at", "do", "how", "what", "when", "with",
}


def _tokens(text: str) -> set[str]:
    return {t for t in _TOKEN_RE.findall(text.lower()) if t not in _STOP}


class FilesBackend:
    """Constructor convention: FilesBackend(root_dir, config, embedder=None)."""

    def __init__(self, root_dir: Path, config: dict | None = None, embedder=None):
        self.root = Path(root_dir)
        self.living_keys = (
            self.root / "vape" / "entity" / "memory" / "in_context"
            / "living_keys_and_index_to_memories.md"
        )

    # -- contract ---------------------------------------------------------

    def capabilities(self) -> Capabilities:
        return Capabilities(
            name="files",
            fts=False,
            vector=False,
            spaces={SPACE_MEMORY, SPACE_FILE},
            concurrent_writers=True,   # nothing is written, so nothing conflicts
            persistent=False,
        )

    def migrate(self) -> None:
        return

    def reset(self) -> None:
        return

    def schema(self) -> str:
        return "files floor — no store; rows derived per query from the markdown tree"

    def index(self, rows: list[Memory]) -> IndexReport:
        return IndexReport(skipped=len(rows))

    def evict(self, ids: list[str]) -> None:
        return

    def evict_sources(self, source_paths: list[str]) -> None:
        return

    def search(self, q: Query) -> list[Hit]:
        qtok = _tokens(q.text)
        if not qtok:
            return []
        rows = self._rows_for_space(q.space)
        if q.kind:
            rows = [r for r in rows if r.kind == q.kind]
        if q.topic:
            rows = [r for r in rows if r.topic == q.topic]
        if q.bubble:
            rows = [r for r in rows if r.bubble == q.bubble]

        keys_scored, grep_scored = [], []
        for r in rows:
            score = self._overlap(qtok, r)
            if score <= 0:
                continue
            (keys_scored if r.kind == "key" else grep_scored).append((score, r))

        hits: list[Hit] = []
        for leg_name, scored in (("keys", keys_scored), ("grep", grep_scored)):
            scored.sort(key=lambda t: t[0], reverse=True)
            for rank, (score, r) in enumerate(scored[: q.candidates], start=1):
                hits.append(Hit(memory=r, source=leg_name, leg_rank=rank, raw_score=score))
        return hits

    # -- rows (derived live; nothing cached) --------------------------------

    @staticmethod
    def _overlap(qtok: set[str], row: Memory) -> float:
        rtok = _tokens(row.content)
        inter = qtok & rtok
        if not inter:
            return 0.0
        first_line = row.content.splitlines()[0].lower() if row.content else ""
        bonus = 0.5 * len(qtok & _tokens(first_line))
        return len(inter) + bonus

    def _rows_for_space(self, space: str) -> list[Memory]:
        sources = (
            derive.file_space_sources(self.root) if space == SPACE_FILE
            else derive.memory_space_sources(self.root)
        )
        rows: list[Memory] = [] if space == SPACE_FILE else list(self._keys_rows())
        for path in sources:
            rows.extend(r for r in derive.derive_file(self.root, path) if r.space == space)
        return rows

    def _keys_rows(self) -> list[Memory]:
        if not self.living_keys.is_file():
            return []
        raw = self.living_keys.read_bytes()
        h = content_hash(raw)
        src = rel_posix(self.living_keys, self.root)
        rows = []
        for i, line in enumerate(raw.decode("utf-8", errors="replace").splitlines()):
            line = line.strip()
            if not line.startswith("- ") or "->" not in line:
                continue
            rows.append(Memory(
                id=memory_id(SPACE_MEMORY, src, f"line:{i}"),
                kind="key", space=SPACE_MEMORY, content=line[2:],
                pointer={"file": src, "anchor": f"line:{i}"},
                source_path=src, source_hash=h,
            ))
        return rows
