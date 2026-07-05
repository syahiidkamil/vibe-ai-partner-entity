"""Row derivation — markdown -> Memory rows, shared by the floor and the sweeper.

One derivation, two consumers: FilesBackend derives per query (nothing
stored), the Indexer derives at sweep time (stored in the plugin index).
Keeping this in one module is what guarantees the floor and every indexed
tier see the SAME rows for the same file.

Rules (doc 12 / the fixture spec):
  memory-space: memory/** except in_context (always loaded), archive (out of
    every default path), proposals (state machine), CLAUDE.md guides.
    cases -> one row per H3 block · notes -> one row per bullet ·
    everything else -> H1 + first paragraph.
  file-space: heading-anchored chunks of memory/** (except archive; yes to
    in_context — the keyring must be findable), self/**, diaries/**.
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

from .interface import (
    SPACE_FILE,
    SPACE_MEMORY,
    Memory,
    content_hash,
    memory_id,
    rel_posix,
)

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

MEMORY_SPACE_EXCLUDED = {"in_context", "archive", "proposals"}
FILE_SPACE_EXCLUDED = {"archive"}

_DATE_RE = re.compile(r"(\d{4})[-_](\d{2})[-_](\d{2})")


def created_at_of(path: Path) -> datetime | None:
    m = _DATE_RE.search(path.stem)
    if not m:
        return None
    try:
        return datetime(int(m[1]), int(m[2]), int(m[3]), tzinfo=timezone.utc)
    except ValueError:
        return None


def entity_dir(root: Path) -> Path:
    return root / "vape" / "entity"


def memory_space_sources(root: Path) -> list[Path]:
    mem = entity_dir(root) / "memory"
    if not mem.is_dir():
        return []
    out = []
    for path in sorted(mem.rglob("*.md")):
        top = rel_posix(path, mem).split("/", 1)[0]
        if top in MEMORY_SPACE_EXCLUDED or path.name == "CLAUDE.md":
            continue
        out.append(path)
    return out


def file_space_sources(root: Path) -> list[Path]:
    ent = entity_dir(root)
    out = []
    mem = ent / "memory"
    if mem.is_dir():
        for path in sorted(mem.rglob("*.md")):
            top = rel_posix(path, mem).split("/", 1)[0]
            if top in FILE_SPACE_EXCLUDED:
                continue
            out.append(path)
    for base in (ent / "self", ent / "diaries"):
        if base.is_dir():
            out.extend(sorted(base.rglob("*.md")))
    return out


def all_sources(root: Path) -> set[Path]:
    return set(memory_space_sources(root)) | set(file_space_sources(root))


def derive_file(root: Path, path: Path) -> list[Memory]:
    """All rows (both spaces) this one file yields. Reads the file once."""
    try:
        raw = path.read_bytes()
    except OSError:
        return []
    text = raw.decode("utf-8", errors="replace")
    src = rel_posix(path, root)
    h = content_hash(raw)
    rows: list[Memory] = []

    mem = entity_dir(root) / "memory"
    in_memory = path.is_relative_to(mem)
    top = rel_posix(path, mem).split("/", 1)[0] if in_memory else None

    if in_memory and top not in MEMORY_SPACE_EXCLUDED and path.name != "CLAUDE.md":
        if top == "cases":
            rows.extend(case_rows(src, h, text, path))
        elif top in ("notes", "events"):
            # dated one-line entries: one row per bullet (a doc row's
            # title+first-para would hide every entry below the fold)
            bullets = note_rows(src, h, text, path, kind=KIND_BY_FOLDER.get(top, "note"))
            rows.extend(bullets if bullets else [doc_row(src, h, text, path, mem, top)])
        else:
            rows.append(doc_row(src, h, text, path, mem, top))

    if not in_memory or top not in FILE_SPACE_EXCLUDED:
        rows.extend(heading_chunks(src, h, text, path))
    return rows


def case_rows(src: str, h: str, text: str, path: Path) -> list[Memory]:
    rows = []
    for block in re.split(r"^### ", text, flags=re.M)[1:]:
        lines = block.splitlines()
        header = lines[0].strip()
        slug = header.split("·")[0].replace("id:", "").strip()
        meta_lines = [ln.strip() for ln in lines[1:4] if ln.strip().startswith("`")]
        rows.append(Memory(
            id=memory_id(SPACE_MEMORY, src, slug),
            kind="case", space=SPACE_MEMORY,
            content="\n".join([header, *meta_lines]),
            pointer={"file": src, "anchor": slug},
            source_path=src, source_hash=h, created_at=created_at_of(path),
        ))
    return rows


def note_rows(src: str, h: str, text: str, path: Path, kind: str = "note") -> list[Memory]:
    """One row per top-level bullet; continuation lines fold into their bullet."""
    rows: list[Memory] = []
    current: list[str] | None = None

    def push() -> None:
        if current:
            n = len(rows) + 1
            rows.append(Memory(
                id=memory_id(SPACE_MEMORY, src, f"bullet:{n}"),
                kind=kind, space=SPACE_MEMORY, content=" ".join(current),
                pointer={"file": src, "anchor": f"bullet:{n}"},
                source_path=src, source_hash=h, created_at=created_at_of(path),
            ))

    for line in text.splitlines():
        if line.startswith("- "):
            push()
            current = [line[2:].strip()]
        elif current is not None and line.startswith("  ") and line.strip():
            current.append(line.strip())
        elif current is not None and not line.strip():
            push()
            current = None
    push()
    return rows


def doc_row(src: str, h: str, text: str, path: Path, mem: Path, top: str) -> Memory:
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
    parts = rel_posix(path, mem).split("/")
    topic = parts[1] if top == "schemata" and len(parts) > 2 else None
    bubble = parts[1] if top == "bubbles" and len(parts) > 2 else None
    return Memory(
        id=memory_id(SPACE_MEMORY, src, "doc"),
        kind=KIND_BY_FOLDER.get(top, "doc"), space=SPACE_MEMORY,
        content="\n".join([title, *para[:4]]),
        pointer={"file": src, "anchor": "doc"},
        source_path=src, source_hash=h, created_at=created_at_of(path),
        topic=topic, bubble=bubble,
    )


def heading_chunks(src: str, h: str, text: str, path: Path) -> list[Memory]:
    rows: list[Memory] = []
    current: list[str] = []
    heading = path.stem
    seen: dict[str, int] = {}

    def push(head: str, body: list[str]) -> None:
        n = seen.get(head, 0)
        seen[head] = n + 1
        anchor = head if n == 0 else f"{head}~{n}"   # disambiguate repeated headings
        chunk = "\n".join([head] + [ln for ln in body if ln.strip()][:6])
        rows.append(Memory(
            id=memory_id(SPACE_FILE, src, anchor),
            kind="chunk", space=SPACE_FILE, content=chunk,
            pointer={"file": src, "anchor": head},
            source_path=src, source_hash=h, created_at=created_at_of(path),
        ))

    for line in text.splitlines():
        if line.startswith("#"):
            if current:
                push(heading, current)
            heading = line.lstrip("# ").strip() or path.stem
            current = []
        else:
            current.append(line)
    if current:
        push(heading, current)
    return rows
