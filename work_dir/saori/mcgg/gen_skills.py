#!/usr/bin/env python3
"""Resolve each MCGG S6 hero's ACTIVE skill (name + description) from the live
client string table, byte-exact, and write provenance to parsed/strategy/.

Why this is honest, not a guess:
  - The hero ACTIVE skill is m_SkillList[0] (flag [1,0]) in MCHero_S6.
  - The skill DESCRIPTION is resolved from AllLanguageEN (the full MLBB string
    table, == localization_en.json). Each skill description names the hero as its
    grammatical subject ("Saber charges ...", "Tigreal unleashes ..."), so a
    description is attributed to a hero by that subject -- verbatim text, not
    invented.
  - AllLanguageEN co-mingles strings across modes/seasons, so several versions of
    a hero's skill text co-exist. The CURRENT S6 active-skill catalog is the band
    ~2212515000..2212525000 (the "A-block"), confirmed by exact, checkable hits:
    Triple Sweep->Saber, Implosion->Tigreal, Fission Wave->Alucard,
    Thunderstruck->Eudora. We prefer that band; the skill NAME is loc[descId-1]
    only when it is a clean title (else left null = "name not resolved").
  - The descriptions carry <Num> VALUE PLACEHOLDERS, not concrete numbers, so we
    assert a mechanic, never a fabricated stat. Unresolved heroes are flagged, not
    guessed.

Run:  uv run python3 work_dir/saori/mcgg/gen_skills.py
"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
P = os.path.join(ROOT, "vape/entity/storage/magic-chess-gogo/game-client-from-bluestack/parsed")
OUTDIR = os.path.join(P, "strategy")
os.makedirs(OUTDIR, exist_ok=True)

loc = {int(k): v for k, v in json.load(open(os.path.join(P, "localization_en.json"))).items()}
heroes_tbl = json.load(open(os.path.join(P, "MCHero_S6.json")))
ds = json.load(open(os.path.join(P, "dataset_live_s6.json")))
name_by_id = {h["id"]: h["name"] for h in ds["heroes"] if h["name"]}
s6_names = set(name_by_id.values())
# active skill id per hero = first entry of m_SkillList (flag [1,0]); summons have none meaningful
active_skill = {r["m_ID"]: (r["m_SkillList"][0][0] if r["m_SkillList"] else None) for r in heroes_tbl}
is_summon = {h["id"]: h.get("isSummon", False) for h in ds["heroes"]}

A_LO, A_HI = 2212515000, 2212525000  # the current S6 active-skill catalog band

MARKUP = re.compile(r"\[C\d|<%?Num|Physical DMG|Magic DMG|True DMG|\bShield\b|\bDEF\b|Basic ATK", re.I)


def subject(v):
    """Longest S6 hero name that v starts with (the acting hero)."""
    if not isinstance(v, str) or len(v) < 16 or not MARKUP.search(v):
        return None
    best = None
    for nm in s6_names:
        if (v.startswith(nm + " ") or v.startswith(nm + "'") or v.startswith(nm + "’")):
            if best is None or len(nm) > len(best):
                best = nm
    return best


def is_passive(v):
    head = v.lstrip()[:16]
    return "Passive]" in head or head.startswith("[C7Passive")


def is_clean_name(v):
    return (isinstance(v, str) and 2 <= len(v) <= 34 and not MARKUP.search(v)
            and v[0].isupper() and subject(v) is None and (not v or v[-1] not in ".:,"))


def clean_desc(v):
    """Faithfully de-markup a skill description for human reading."""
    v = v.split("####")[0]                       # drop appended passive/extra segment
    v = re.sub(r"\[C\d+([^\]]*)\]", r"\1", v)     # color codes -> inner text
    v = re.sub(r"<%Num(\d+)>", r"Num\1%", v)       # percent value placeholder
    v = re.sub(r"<Num(\d+)>", r"Num\1", v)         # value placeholder
    v = re.sub(r"\[%Num(\d+)\]", r"Num\1%", v)     # bracketed percent placeholder
    v = re.sub(r"\[Num(\d+)\]", r"Num\1", v)       # bracketed value placeholder
    v = re.sub(r"<Gold_\d+>", "", v)
    v = re.sub(r"\$\{[^}]*\}\$", "items", v)
    v = re.sub(r"\s+", " ", v).strip()
    return v


name2id = {v: k for k, v in name_by_id.items()}

# collect every active (non-passive) description attributed to an S6 hero
cands = {hid: [] for hid in name_by_id}
for kid, v in loc.items():
    sub = subject(v)
    if not sub or is_passive(v):
        continue
    hid = name2id[sub]
    nm = loc.get(kid - 1, "")
    cands[hid].append({
        "descId": kid,
        "nameId": kid - 1,
        "name": nm if is_clean_name(nm) else None,
        "inABlock": A_LO <= kid <= A_HI,
        "raw": v,
    })


def pick(hid):
    cs = cands.get(hid, [])
    if not cs:
        return None
    # priority: in A-block first; with a clean name first; then most descriptive (longest)
    cs = sorted(cs, key=lambda c: (c["inABlock"], c["name"] is not None, len(c["raw"])),
                reverse=True)
    return cs[0]


out = {}
for hid, nm in sorted(name_by_id.items()):
    if is_summon.get(hid):
        out[hid] = {"name": nm, "activeSkillId": active_skill.get(hid),
                    "skillName": None, "skillDesc": None, "resolved": False,
                    "reason": "summon/special unit -- not resolved", "candidates": []}
        continue
    best = pick(hid)
    out[hid] = {
        "name": nm,
        "activeSkillId": active_skill.get(hid),
        "skillName": best["name"] if best else None,
        "skillDesc": clean_desc(best["raw"]) if best else None,
        "skillDescRaw": best["raw"] if best else None,
        "descStringId": best["descId"] if best else None,
        "nameStringId": (best["nameId"] if best and best["name"] else None),
        "fromS6Band": best["inABlock"] if best else None,
        "resolved": best is not None,
        "candidateCount": len(cands.get(hid, [])),
        "candidates": [{"descId": c["descId"], "name": c["name"],
                        "inABlock": c["inABlock"], "desc": c["raw"][:140]}
                       for c in sorted(cands.get(hid, []), key=lambda c: c["descId"])],
    }

json.dump({"meta": {"source": "AllLanguageEN (localization_en.json) live v302.2",
                    "method": "active skill = MCHero_S6.m_SkillList[0]; description "
                              "attributed by hero-subject; S6 band ~2212515000-2212525000 "
                              "preferred; name = loc[descId-1] when a clean title",
                    "aBand": [A_LO, A_HI]},
           "heroes": out},
          open(os.path.join(OUTDIR, "heroes_skills.json"), "w"),
          ensure_ascii=False, indent=1)

# ---- report ----
resolved = [h for h in out.values() if h["resolved"]]
named = [h for h in resolved if h["skillName"]]
inband = [h for h in resolved if h.get("fromS6Band")]
print(f"heroes total: {len(out)}")
print(f"resolved active skill (description): {len(resolved)}")
print(f"  of which with a resolved skill NAME: {len(named)}")
print(f"  of which from the S6 band: {len(inband)}")
print("UNRESOLVED:")
for hid, h in out.items():
    if not h["resolved"]:
        print(f"  {h['name']} (id{hid}) skill {h['activeSkillId']}  cands={len(h.get('candidates',[]))}")
print("\nSPOT-CHECK (name :: desc):")
for nm in ["Saber", "Tigreal", "Alucard", "Eudora", "Lancelot", "Kagura"]:
    hid = name2id.get(nm)
    h = out.get(hid, {})
    print(f"  {nm}: [{h.get('skillName')}] (descId {h.get('descStringId')}) :: {str(h.get('skillDesc'))[:100]}")
