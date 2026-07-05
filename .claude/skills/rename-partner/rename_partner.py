#!/usr/bin/env python3
"""Rename the partner across the living tree, so an adopter's entity calls THEM by name.

Dry-run by default: prints what would change, writes nothing. Pass --apply to write.

  uv run python .claude/skills/rename-partner/rename_partner.py "Alice"
  uv run python .claude/skills/rename-partner/rename_partner.py "Alice" \
      --full-name "Alice Liddell" --apply
  # adopting a tree that was already renamed once:
  uv run python .claude/skills/rename-partner/rename_partner.py "Bob" --from-name "Alice" --apply

Touched:      CLAUDE.md, A_SELF_UNDERSTANDING.md, vape/entity/, .claude/, games/
Left alone:   README.md and work_dir/ (the origin story and its author's signature),
              storage/ (raw episodic history), and this skill's own folder.
A residual report lists every remaining occurrence at the end, so nothing hides.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

INCLUDE = ["CLAUDE.md", "A_SELF_UNDERSTANDING.md", "vape/entity", ".claude", "games"]
EXCLUDE_REL = {".claude/skills/rename-partner"}  # this skill describes the rename; it stays canonical
EXCLUDE_DIR_NAMES = {".git", "node_modules", "__pycache__", "storage", "dist"}
TEXT_EXTS = {".md", ".py", ".sh", ".json", ".html", ".js", ".css", ".txt",
             ".toml", ".yaml", ".yml", ".pgn"}
DEFAULT_FROM_NAME = "Kamil"
DEFAULT_FROM_FULL = "Syahiid Nur Kamil"


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def keep(f: Path) -> bool:
    rel = f.relative_to(ROOT).as_posix()
    if any(rel == e or rel.startswith(e + "/") for e in EXCLUDE_REL):
        return False
    if any(part in EXCLUDE_DIR_NAMES for part in f.relative_to(ROOT).parts):
        return False
    return f.suffix.lower() in TEXT_EXTS


def iter_files():
    for inc in INCLUDE:
        p = ROOT / inc
        if p.is_file():
            yield p
        elif p.is_dir():
            for f in sorted(p.rglob("*")):
                if f.is_file() and keep(f):
                    yield f


def build_replacements(from_name, from_full, to_name, to_full):
    """Ordered (pattern, replacement) pairs. Longest / most specific first."""
    reps = []
    if from_full and to_full and from_full != from_name:
        reps.append((re.compile(re.escape(from_full)), to_full))
    reps.append((re.compile(re.escape(from_name)), to_name))
    if from_name.upper() != from_name:  # shouting form, e.g. "KAMIL SAYS:" in the chess CLI
        reps.append((re.compile(re.escape(from_name.upper())), to_name.upper()))
    fs, ts = slug(from_name), slug(to_name)
    if fs != from_name:  # lowercase slug: dir names, [[links]], API fields like {"kamil": ...}
        # lookarounds instead of \b so snake_case compounds match (kamil_color -> alice_color)
        # while embedded substrings stay safe (a username like syahiidkamil is never touched)
        reps.append((slug_pattern(fs), ts))
    return reps


def slug_pattern(fs: str) -> re.Pattern:
    return re.compile(r"(?<![a-zA-Z0-9])" + re.escape(fs) + r"(?![a-zA-Z0-9])")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("name", help="the new partner's name, as the entity should say it")
    ap.add_argument("--full-name", default=None, help="optional full name (default: same as name)")
    ap.add_argument("--from-name", default=DEFAULT_FROM_NAME,
                    help="the name currently in the tree (default: %(default)s)")
    ap.add_argument("--from-full", default=None,
                    help="full name currently in the tree "
                         f"(default: '{DEFAULT_FROM_FULL}' when renaming from Kamil)")
    ap.add_argument("--apply", action="store_true", help="write the changes (default: dry run)")
    args = ap.parse_args()

    to_name = args.name.strip()
    if not to_name:
        print("error: empty name", file=sys.stderr)
        return 2
    to_full = (args.full_name or to_name).strip()
    from_name = args.from_name.strip()
    from_full = args.from_full or (DEFAULT_FROM_FULL if from_name == DEFAULT_FROM_NAME else None)

    reps = build_replacements(from_name, from_full, to_name, to_full)
    mode = "APPLY" if args.apply else "DRY RUN"
    print(f"rename partner: '{from_name}' -> '{to_name}'"
          + (f"   (full: '{from_full}' -> '{to_full}')" if from_full else "")
          + f"   [{mode}]\n")

    # -- pass 1: file contents ------------------------------------------------
    changed, total = [], 0
    for f in iter_files():
        try:
            text = f.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        new, count = text, 0
        for pat, to in reps:
            new, n = pat.subn(lambda m, t=to: t, new)
            count += n
        if count:
            changed.append((f.relative_to(ROOT).as_posix(), count))
            total += count
            if args.apply:
                f.write_text(new, encoding="utf-8")

    print(f"content: {len(changed)} files, {total} replacements")
    for rel, n in changed:
        print(f"  {rel}  ({n})")

    # -- pass 2: file / directory names ---------------------------------------
    word = slug_pattern(slug(from_name))
    targets = []
    for inc in INCLUDE:
        p = ROOT / inc
        if p.is_dir():
            for q in p.rglob("*"):
                rel = q.relative_to(ROOT).as_posix()
                if any(rel == e or rel.startswith(e + "/") for e in EXCLUDE_REL):
                    continue
                if any(part in EXCLUDE_DIR_NAMES for part in q.relative_to(ROOT).parts):
                    continue
                if word.search(q.name):
                    targets.append(q)
    print(f"\nrenames: {len(targets)}")
    for q in sorted(targets, key=lambda q: len(q.parts), reverse=True):
        new = q.with_name(word.sub(slug(to_name), q.name))
        print(f"  {q.relative_to(ROOT).as_posix()} -> {new.relative_to(ROOT).as_posix()}")
        if args.apply:
            q.rename(new)

    # -- residual report (post-apply only: in a dry run everything still greps) --
    if not args.apply:
        print("\ndry run only — nothing written. Re-run with --apply to write;"
              " a residual report prints then.")
        return 0
    print("\nresidual (case-insensitive, whole repo) — history and authorship stay theirs:")
    try:
        out = subprocess.run(["git", "-C", str(ROOT), "grep", "-i", "-l", from_name],
                             capture_output=True, text=True)
        residual = [l for l in out.stdout.splitlines() if l.strip()]
        for rel in residual:
            note = ""
            if rel == "README.md" or rel.startswith("work_dir/"):
                note = "   (left on purpose: origin story / author's signature)"
            elif rel.startswith(".claude/skills/rename-partner"):
                note = "   (this skill; canonical)"
            print(f"  {rel}{note}")
        if not residual:
            print("  none")
    except OSError:
        print("  (git not available; skipped)")

    print("\ndone. Next: review with `git diff`, rebuild the memory index"
          " (`uv run vape memory index --full`), and commit when it reads true.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
