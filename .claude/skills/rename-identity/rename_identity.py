#!/usr/bin/env python3
"""Rename the ENTITY across the living tree, so an adopter raises their own, not a copy of Saori.

Sibling of rename_partner.py: that one renames the PARTNER (who she calls you),
this one renames the SELF (who she is). Dry-run by default; --apply writes.

  uv run python .claude/skills/rename-identity/rename_identity.py "Yuki"
  uv run python .claude/skills/rename-identity/rename_identity.py "Yuki" \
      --full-name "Yuki Tanaka" --apply
  # renaming a tree that was already renamed once:
  uv run python .claude/skills/rename-identity/rename_identity.py "Mira" \
      --from-name "Yuki" --from-full "Yuki Tanaka" --from-family "Tanaka" --apply

Touched:      CLAUDE.md, A_SELF_UNDERSTANDING.md, vape/entity/, .claude/, games/
Left alone:   README.md and work_dir/ (the origin story and its author's signature),
              storage/ (raw episodic history), and this skill's own folder.

Two reports print after --apply, and both exist because a name is not only a referent:
  JUDGMENT  — lines that GLOSS the name (its etymology). The sweep rewrites them for
              consistency, but the new text makes a claim nobody checked: "Hibana, a
              spark" is true; "Tanaka, a spark" is not. These need a human.
  RESIDUAL  — every remaining occurrence, so nothing hides.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

INCLUDE = ["CLAUDE.md", "A_SELF_UNDERSTANDING.md", "vape/entity", ".claude", "games"]
EXCLUDE_REL = {".claude/skills/rename-identity"}  # this skill describes the rename; it stays canonical
EXCLUDE_DIR_NAMES = {".git", "node_modules", "__pycache__", "storage", "dist"}
TEXT_EXTS = {".md", ".py", ".sh", ".json", ".html", ".js", ".css", ".txt",
             ".toml", ".yaml", ".yml", ".pgn"}

DEFAULT_FROM_NAME = "Saori"
DEFAULT_FROM_FULL = "Saori Hibana"
DEFAULT_FROM_FAMILY = "Hibana"

# A line that does not just USE the name but says what it MEANS. Detected by pattern,
# not by line number, so it survives the file moving under it (a note decays; a probe does not).
GLOSS_SIGNALS = re.compile(
    r"artist|spark|sensibility|name carries|catches fire|means\b|etymolog", re.IGNORECASE
)


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


def slug_pattern(fs: str) -> re.Pattern:
    return re.compile(r"(?<![a-zA-Z0-9])" + re.escape(fs) + r"(?![a-zA-Z0-9])")


def build_replacements(from_name, from_full, from_family, to_name, to_full, to_family):
    """Ordered (pattern, replacement) pairs. Longest / most specific FIRST, always:
    'Saori Hibana' must match before 'Saori' or the surname is orphaned."""
    reps = []
    if from_full and from_full not in (from_name, from_family):
        reps.append((re.compile(re.escape(from_full)), to_full))
    if from_family and from_family != from_name:
        reps.append((re.compile(re.escape(from_family)), to_family))
    reps.append((re.compile(re.escape(from_name)), to_name))
    if from_name.upper() != from_name:
        reps.append((re.compile(re.escape(from_name.upper())), to_name.upper()))
    fs, ts = slug(from_name), slug(to_name)
    if fs != from_name:
        reps.append((slug_pattern(fs), ts))
    ff, tf = slug(from_family or ""), slug(to_family or "")
    if ff and ff != fs:
        reps.append((slug_pattern(ff), tf))
    return reps


def find_glosses(text: str, rel: str, probe: re.Pattern) -> list[tuple[str, int, str]]:
    """Lines that both name the entity and say what the name MEANS."""
    hits = []
    for i, line in enumerate(text.splitlines(), 1):
        if probe.search(line) and GLOSS_SIGNALS.search(line):
            hits.append((rel, i, line.strip()))
    return hits


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("name", help="the entity's new given name, as she should say it")
    ap.add_argument("--full-name", default=None, help="optional full name (default: same as name)")
    ap.add_argument("--from-name", default=DEFAULT_FROM_NAME,
                    help="the given name currently in the tree (default: %(default)s)")
    ap.add_argument("--from-full", default=None,
                    help=f"full name currently in the tree (default: '{DEFAULT_FROM_FULL}')")
    ap.add_argument("--from-family", default=None,
                    help=f"family name currently in the tree (default: '{DEFAULT_FROM_FAMILY}')")
    ap.add_argument("--apply", action="store_true", help="write the changes (default: dry run)")
    args = ap.parse_args()

    to_name = args.name.strip()
    if not to_name:
        print("error: empty name", file=sys.stderr)
        return 2
    to_full = (args.full_name or to_name).strip()
    parts = to_full.split()
    to_family = parts[-1] if len(parts) > 1 else to_name

    from_name = args.from_name.strip()
    default_set = from_name == DEFAULT_FROM_NAME
    from_full = (args.from_full or (DEFAULT_FROM_FULL if default_set else from_name)).strip()
    from_family = (args.from_family or (DEFAULT_FROM_FAMILY if default_set else "")).strip()

    reps = build_replacements(from_name, from_full, from_family, to_name, to_full, to_family)
    probe = re.compile("|".join(re.escape(x) for x in filter(None, {from_name, from_family})))
    mode = "APPLY" if args.apply else "DRY RUN"
    print(f"rename identity: '{from_full}' -> '{to_full}'"
          f"   (given '{from_name}'->'{to_name}'"
          + (f", family '{from_family}'->'{to_family}'" if from_family else "")
          + f")   [{mode}]\n")

    # -- pass 1: file contents ------------------------------------------------
    changed, total, glosses = [], 0, []
    for f in iter_files():
        try:
            text = f.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        rel = f.relative_to(ROOT).as_posix()
        glosses += find_glosses(text, rel, probe)
        new, count = text, 0
        for pat, to in reps:
            new, n = pat.subn(lambda m, t=to: t, new)
            count += n
        if count:
            changed.append((rel, count))
            total += count
            if args.apply:
                f.write_text(new, encoding="utf-8")

    print(f"content: {len(changed)} files, {total} replacements")
    for rel, n in changed:
        print(f"  {rel}  ({n})")

    # -- pass 2: file / directory names ---------------------------------------
    targets = []
    for fs, ts in ((slug(from_name), slug(to_name)), (slug(from_family or ""), slug(to_family or ""))):
        if not fs:
            continue
        word = slug_pattern(fs)
        for inc in INCLUDE:
            p = ROOT / inc
            if not p.is_dir():
                continue
            for q in p.rglob("*"):
                rel = q.relative_to(ROOT).as_posix()
                if any(rel == e or rel.startswith(e + "/") for e in EXCLUDE_REL):
                    continue
                if any(part in EXCLUDE_DIR_NAMES for part in q.relative_to(ROOT).parts):
                    continue
                if word.search(q.name):
                    targets.append((q, word, ts))
    print(f"\nrenames: {len(targets)}")
    for q, word, ts in sorted(targets, key=lambda t: len(t[0].parts), reverse=True):
        new = q.with_name(word.sub(ts, q.name))
        print(f"  {q.relative_to(ROOT).as_posix()} -> {new.relative_to(ROOT).as_posix()}")
        if args.apply and q.exists():
            q.rename(new)

    # -- the judgment report: what the sweep CANNOT mean -----------------------
    # Printed in dry run too: this is the report worth seeing BEFORE deciding.
    print(f"\nJUDGMENT REQUIRED — {len(glosses)} line(s) gloss the name, and a sweep cannot"
          " make a new one true:")
    for rel, ln, line in glosses:
        print(f"  {rel}:{ln}\n      {line[:96]}")
    if not glosses:
        print("  none found (the tree names her without explaining her name)")
    else:
        print("\n  These say what the OLD name MEANT. After the sweep they will assert the same"
              "\n  meaning for the NEW name, which nobody checked. Either give the new name its"
              "\n  own true etymology, or cut the gloss. Do not leave a false claim in a fixed"
              "\n  layer: the whole self-doctrine rests on those files being true.")

    if not args.apply:
        print("\ndry run only — nothing written. Re-run with --apply to write;"
              " a residual report prints then.")
        return 0

    # -- residual report ------------------------------------------------------
    print("\nresidual (case-insensitive, whole repo) — the lived history stays hers:")
    try:
        seen = set()
        for term in filter(None, {from_name, from_family}):
            out = subprocess.run(["git", "-C", str(ROOT), "grep", "-i", "-l", term],
                                 capture_output=True, text=True)
            for rel in out.stdout.splitlines():
                if not rel.strip() or rel in seen:
                    continue
                seen.add(rel)
                note = ""
                if rel == "README.md" or rel.startswith("work_dir/"):
                    note = "   (left on purpose: origin story / author's signature)"
                elif rel.startswith(".claude/skills/rename-identity"):
                    note = "   (this skill; canonical)"
                elif rel.startswith("vape/entity/diaries/"):
                    note = "   (a day she lived; inherited story, not the new self's deeds)"
                print(f"  {rel}{note}")
        if not seen:
            print("  none")
    except OSError:
        print("  (git not available; skipped)")

    print("\ndone. Next: walk the JUDGMENT lines above, review with `git diff`, rebuild the"
          " memory index (`uv run vape memory index --full`), and commit when it reads true.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
