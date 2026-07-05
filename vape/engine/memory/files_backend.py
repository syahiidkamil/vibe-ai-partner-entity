"""FilesBackend — the T0 floor. Always available, zero dependencies, nothing stored.

Two legs, mirroring how the floor is actually lived:
  - 'keys' — the living-keys file (`key -> path`, `cue -> memory` lines), the
    working-memory keyring matched first;
  - 'grep' — a pure-Python token-overlap scan over rows derived on the fly
    from the warm tree (cases H3 blocks, notes bullets, H1+first-paragraph
    docs) and, for file-space, heading-anchored sections of memory/ + self/ +
    diaries.

Pure Python on purpose: no grep/rg subprocess, so the floor is identical on
macOS, Linux, and Windows, and works on a box with no coreutils at all.
source_hash is computed from the bytes just read, so read-time verification
is trivially fresh here — the floor cannot go stale.
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

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

# top-level memory/ folder -> row kind (memory-space)
KIND_BY_FOLDER = {
    "cases": "case",
    "notes": "note",
    "schemata": "schema",
    "people": "person",
    "events": "event",
    "dreams": "dream",
    "decisions": "decision",
    "bubbles": "bubble",
    "interests": "interest",
    "growth": "lesson",
    "adaptation_efforts": "adaptation",
    "suffering": "suffering",
    "synchronicity": "synchronicity",
    "personal": "personal",
}

# never derived from, either space (in_context is always loaded; archive is
# out of every default search path by doctrine; storage is the raw substrate)
EXCLUDED_MEMORY_DIRS = {"in_context", "archive", "proposals"}

_TOKEN_RE = re.compile(r"[a-z0-9]+")
_STOP = {
    "the", "a", "an", "of", "to", "in", "on", "and", "or", "for", "is", "are",
    "was", "i", "my", "me", "it", "at", "do", "how", "what", "when", "with",
}
_DATE_RE = re.compile(r"(\d{4})[-_](\d{2})[-_](\d{2})")


def _tokens(text: str) -> set[str]:
    return {t for t in _TOKEN_RE.findall(text.lower()) if t not in _STOP}


def _created_at(path: Path) -> datetime | None:
    m = _DATE_RE.search(path.stem)
    if not m:
        return None
    try:
        return datetime(int(m[1]), int(m[2]), int(m[3]), tzinfo=timezone.utc)
    except ValueError:
        return None


class FilesBackend:
    """Constructor convention: FilesBackend(root_dir, config, embedder=None)."""

    def __init__(self, root_dir: Path, config: dict | None = None, embedder=None):
        self.root = Path(root_dir)
        self.entity = self.root / "vape" / "entity"
        self.memory_dir = self.entity / "memory"
        self.living_keys = self.memory_dir / "in_context" / "living_keys_and_index_to_memories.md"

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

    def migrate(self) -> None:  # nothing to create
        return

    def schema(self) -> str:
        return "files floor — no store; rows derived per query from the markdown tree"

    def index(self, rows: list[Memory]) -> IndexReport:
        # the floor holds no store; indexing is a no-op by design
        return IndexReport(skipped=len(rows))

    def evict(self, ids: list[str]) -> None:
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

        hits: list[Hit] = []
        keys_scored, grep_scored = [], []
        for r in rows:
            score = self._overlap(qtok, r)
            if score <= 0:
                continue
            (keys_scored if r.kind == "key" else grep_scored).append((score, r))
        for leg_name, scored in (("keys", keys_scored), ("grep", grep_scored)):
            scored.sort(key=lambda t: t[0], reverse=True)
            for rank, (score, r) in enumerate(scored[: q.candidates], start=1):
                hits.append(Hit(memory=r, source=leg_name, leg_rank=rank, raw_score=score))
        return hits

    # -- derivation (on the fly; nothing cached) ---------------------------

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
        if space == SPACE_FILE:
            return self._file_space_rows()
        return self._memory_space_rows()

    def _memory_space_rows(self) -> list[Memory]:
        rows: list[Memory] = list(self._keys_rows())
        if not self.memory_dir.is_dir():
            return rows
        for path in sorted(self.memory_dir.rglob("*.md")):
            top = rel_posix(path, self.memory_dir).split("/", 1)[0]
            if top in EXCLUDED_MEMORY_DIRS or path.name == "CLAUDE.md":
                continue
            try:
                raw = path.read_bytes()
            except OSError:
                continue
            text = raw.decode("utf-8", errors="replace")
            src = rel_posix(path, self.root)
            h = content_hash(raw)
            kind = KIND_BY_FOLDER.get(top, "doc")
            if top == "cases":
                rows.extend(self._case_rows(src, h, text, path))
            elif top == "notes":
                rows.extend(self._note_rows(src, h, text, path))
            else:
                rows.append(self._doc_row(src, h, text, path, kind, top))
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

    def _case_rows(self, src: str, h: str, text: str, path: Path) -> list[Memory]:
        rows = []
        blocks = re.split(r"^### ", text, flags=re.M)[1:]
        for block in blocks:
            lines = block.splitlines()
            header = lines[0].strip()
            slug = header.split("·")[0].replace("id:", "").strip()
            meta_lines = [ln.strip() for ln in lines[1:4] if ln.strip().startswith("`")]
            rows.append(Memory(
                id=memory_id(SPACE_MEMORY, src, slug),
                kind="case", space=SPACE_MEMORY,
                content="\n".join([header, *meta_lines]),
                pointer={"file": src, "anchor": slug},
                source_path=src, source_hash=h, created_at=_created_at(path),
            ))
        return rows

    def _note_rows(self, src: str, h: str, text: str, path: Path) -> list[Memory]:
        rows, ordinal = [], 0
        for line in text.splitlines():
            if not line.startswith("- "):
                continue
            ordinal += 1
            rows.append(Memory(
                id=memory_id(SPACE_MEMORY, src, f"bullet:{ordinal}"),
                kind="note", space=SPACE_MEMORY, content=line[2:].strip(),
                pointer={"file": src, "anchor": f"bullet:{ordinal}"},
                source_path=src, source_hash=h, created_at=_created_at(path),
            ))
        return rows

    def _doc_row(self, src: str, h: str, text: str, path: Path, kind: str, top: str) -> Memory:
        lines = text.splitlines()
        title = next((ln.lstrip("# ").strip() for ln in lines if ln.startswith("#")), path.stem)
        para: list[str] = []
        for ln in lines:
            if ln.startswith("#"):
                continue
            if ln.strip():
                para.append(ln.strip())
            elif para:
                break
        parts = rel_posix(path, self.memory_dir).split("/")
        topic = parts[1] if top == "schemata" and len(parts) > 2 else None
        bubble = parts[1] if top == "bubbles" and len(parts) > 2 else None
        return Memory(
            id=memory_id(SPACE_MEMORY, src, "doc"),
            kind=kind, space=SPACE_MEMORY,
            content="\n".join([title, *para[:4]]),
            pointer={"file": src, "anchor": "doc"},
            source_path=src, source_hash=h, created_at=_created_at(path),
            topic=topic, bubble=bubble,
        )

    def _file_space_rows(self) -> list[Memory]:
        rows: list[Memory] = []
        roots = [self.memory_dir, self.entity / "self", self.entity / "diaries"]
        for base in roots:
            if not base.is_dir():
                continue
            for path in sorted(base.rglob("*.md")):
                if base is self.memory_dir:
                    top = rel_posix(path, self.memory_dir).split("/", 1)[0]
                    if top in {"archive"}:
                        continue
                try:
                    raw = path.read_bytes()
                except OSError:
                    continue
                text = raw.decode("utf-8", errors="replace")
                src = rel_posix(path, self.root)
                h = content_hash(raw)
                rows.extend(self._heading_chunks(src, h, text, path))
        return rows

    def _heading_chunks(self, src: str, h: str, text: str, path: Path) -> list[Memory]:
        rows = []
        current: list[str] = []
        heading = path.stem
        for line in text.splitlines():
            if line.startswith("#"):
                if current:
                    rows.append(self._chunk_row(src, h, heading, current, path))
                heading = line.lstrip("# ").strip() or path.stem
                current = []
            else:
                current.append(line)
        if current:
            rows.append(self._chunk_row(src, h, heading, current, path))
        return rows

    def _chunk_row(self, src: str, h: str, heading: str, body: list[str], path: Path) -> Memory:
        text = "\n".join([heading] + [ln for ln in body if ln.strip()][:6])
        return Memory(
            id=memory_id(SPACE_FILE, src, heading),
            kind="chunk", space=SPACE_FILE, content=text,
            pointer={"file": src, "anchor": heading},
            source_path=src, source_hash=h, created_at=_created_at(path),
        )
