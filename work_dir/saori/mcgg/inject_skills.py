#!/usr/bin/env python3
"""Inject each hero's ACTIVE skill (from parsed/strategy/heroes_skills.json) into
the generated hero markdown, idempotently. Adds one '- **Active skill ...**' bullet
right after the existing '- **Skills:** [...]' bullet in every hero block.

Re-runnable: it strips any prior injected bullet before re-adding, so running it
again (e.g. after a season patch + gen_skills.py) just refreshes the lines.

Run:  uv run python3 work_dir/saori/mcgg/gen_skills.py
      uv run python3 work_dir/saori/mcgg/inject_skills.py
"""
import json, os, re, textwrap

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
HDIR = os.path.join(ROOT, "vape/entity/memory/schemata/magic_chess_gogo/concrete_things/heroes")
SKILLS = json.load(open(os.path.join(
    ROOT, "vape/entity/storage/magic-chess-gogo/game-client-from-bluestack/parsed/"
          "strategy/heroes_skills.json")))["heroes"]
by_id = {int(k): v for k, v in SKILLS.items()}

HEADER = re.compile(r"^### .+?\(id (\d+),")
SKILLS_BULLET = re.compile(r"^- \*\*Skills:\*\*")
INJECTED = re.compile(r"^(- \*\*Active skill|  )")  # our bullet + its wrapped continuations


def skill_lines(hid):
    h = by_id.get(hid)
    if not h:
        return []
    if not h.get("resolved"):
        return ["- **Active skill:** skill text not resolved (summon / special unit)."]
    desc = h["skillDesc"]
    nm = h.get("skillName")
    label = f"**Active skill ({nm}):**" if nm else "**Active skill (name not resolved):**"
    full = f"- {label} {desc}"
    wrapped = textwrap.wrap(full, width=100, subsequent_indent="  ",
                            break_long_words=False, break_on_hyphens=False)
    return wrapped


def process(path):
    lines = open(path).read().split("\n")
    out, i, cur_id, n = [], 0, None, 0
    while i < len(lines):
        ln = lines[i]
        m = HEADER.match(ln)
        if m:
            cur_id = int(m.group(1))
        if SKILLS_BULLET.match(ln) and cur_id is not None:
            out.append(ln)
            i += 1
            # drop any previously injected bullet + continuations
            while i < len(lines) and INJECTED.match(lines[i]):
                i += 1
            new = skill_lines(cur_id)
            if new:
                out.extend(new)
                n += 1
            continue
        out.append(ln)
        i += 1
    open(path, "w").write("\n".join(out))
    return n


total = 0
for f in ["cost_1.md", "cost_2.md", "cost_3.md", "cost_4.md", "cost_5.md", "special_units.md"]:
    p = os.path.join(HDIR, f)
    if os.path.exists(p):
        c = process(p)
        total += c
        print(f"  {f}: injected/updated {c} hero skill blocks")
print("total hero blocks touched:", total)
