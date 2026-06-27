"""Build parsed/strategy/resolved_effects.json for MCGG v302.2.

Deepens the EFFECT layer:
  - synergies: parse every per-tier value-formula token into structured form, derive the
    effect *shape* from the tokens, and attach best-match localization description candidates.
  - formula DSL: the grammar is documented in FORMULA_DSL.md; this evaluates what it can and
    marks the rest unresolved (the raw value N lives in MCEffect_S1/S2 keyed by composite
    effect ids that the client resolves in battle logic, not as flat int32 keys -> unreachable
    from this static dump; verified by exhaustive int32 search).
  - heroSkills: hero -> active skillId (from MCHero_S6.m_SkillList[0]) + best-match skill
    description candidate from localization (hash-keyed text, so band/subject heuristic only).
  - leftoverTables: MCRoundRandomEquip decoded (round/season -> equip drop pools + weights).

Run: uv run python3 work_dir/saori/mcgg/build_resolved_effects.py
"""
import sys, os, json, struct, re
from collections import defaultdict, Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import mulong_parse as mp

BASE = os.path.join(ROOT, "vape/entity/storage/magic-chess-gogo/game-client-from-bluestack")
DEC = os.path.join(BASE, "readable/decoded")
PARSED = os.path.join(BASE, "parsed")
OUT = os.path.join(PARSED, "strategy")
os.makedirs(OUT, exist_ok=True)

loc = {int(k): v for k, v in json.load(open(os.path.join(PARSED, "localization_en.json"))).items()}
rs_rows = json.load(open(os.path.join(PARSED, "RelationSkill_MC_S6.json")))
ds = json.load(open(os.path.join(PARSED, "dataset_live_s6.json")))
synergy_name = {s["relId"]: s["name"] for s in ds["synergies"]}
synergy_axis = {s["relId"]: s["axis"] for s in ds["synergies"]}
hero_rows = json.load(open(os.path.join(PARSED, "MCHero_S6.json")))
# hero id->name from the friend-derived dataset (already verified present in v302.2 loc)
hero_name = {h["id"]: h["name"] for h in ds["heroes"]}


# ---------------------------------------------------------------- formula DSL parse
EXPR_DESC = {
    "N*0.01": "raw x 0.01 (raw stored x100; e.g. 1000 -> 10)",
    "N*0.1": "raw x 0.1 (raw stored x10)",
    "N*100": "raw x 100 (raw stored as fraction; e.g. 0.2 -> 20)",
    "N": "raw value as-is",
    "N*0.001": "raw x 0.001",
    "N*0.000001": "raw x 1e-6",
    "N*0.01+100": "raw x 0.01 + 100 (a multiplier: 100% + bonus%)",
    "0": "constant 0 (placeholder / disabled slot)",
}
UNIT_DESC = {"%": "percent", "@": "flat (absolute)", "0": "unitless / raw"}
TYPE_DESC = {
    "2": "MCEffect value lookup (effect id -> param column)",
    "3": "trigger-chance lookup (TriggerJudge: proc probability)",
    "105010": "dynamic param (count-based, e.g. per-stack / per-hero)",
    "105011": "dynamic param (count-based, e.g. per-stack / per-hero)",
}


def parse_token(tok):
    """One m_NumDescribe entry -> structured dict.
    Bracketed [type|effectId|param|unit|expr(|extra)] = an effect lookup (value templated).
    A bare number = a literal constant (RESOLVED value, e.g. '1', '999'=unlimited)."""
    if tok.startswith("[") and tok.endswith("]"):
        parts = tok[1:-1].split("|")
        if len(parts) < 5:
            return None
        d = {"kind": "effect", "type": parts[0], "effectId": parts[1], "param": parts[2],
             "unit": parts[3], "expr": parts[4], "raw": tok, "resolved": None}
        if len(parts) > 5:
            d["extra"] = parts[5]
        return d
    if re.fullmatch(r"-?\d+(\.\d+)?", tok):
        return {"kind": "literal", "value": float(tok) if "." in tok else int(tok),
                "raw": tok, "resolved": float(tok) if "." in tok else int(tok)}
    return None


def shape_phrase(p):
    """Human phrase for one parsed token's effect shape."""
    if p["kind"] == "literal":
        return "literal %s (resolved)" % p["value"]
    unit = UNIT_DESC.get(p["unit"], p["unit"])
    if p["type"] == "3":
        return "a trigger chance (%s)" % unit
    if p["type"] in ("105010", "105011"):
        return "a count-scaled value (%s, dynamic per stack/hero)" % unit
    return "a %s value" % unit


# ---------------------------------------------------------------- effect-text candidates
EXCLUDE = ["final round", "Progress", "Arena match", "skin", "Check out", "Activate ",
           "Practice", "Are you sure", "Confirm to", "MVP", "Ranked"]
# MLBB MOBA-mode tells: these strings are from the main MOBA, not the MCGG auto-chess synergy.
MOBA_TELL = ["Buff:", "Buff -", "BUFF-", "BUFF--", "Phy.ATK", "Phy.Def", "Mag.ATK", "Mag.Def",
             "Battle Spell", "Emblem", "Lv.", "minion", "jungle", "Jungle", "Set Bonus"]


def text_candidates(name, has_chance):
    """Best localization description strings that name this synergy as the effect subject."""
    cands = []
    if not name:
        return cands
    for sid, t in loc.items():
        if name not in t:
            continue
        if "<Num" not in t and "<%Num" not in t:
            continue
        if any(w in t for w in EXCLUDE) or any(w in t for w in MOBA_TELL):
            continue
        if len(t) > 220:
            continue
        score = 0
        # strongest: the auto-chess synergy-panel form "[C7<Name>] ..." or "<Name> Hero(es)"
        if t.strip().startswith("[C7" + name) or t.strip().startswith("[C9" + name):
            score += 4
        if name + " Hero" in t or name + " Heroes" in t:
            score += 3
        elif t.strip().startswith(name):
            score += 2
        if "Synergy" in t:
            score += 1
        if has_chance and ("chance" in t):
            score += 1
        cands.append((score, len(t), sid, t))
    cands.sort(key=lambda x: (-x[0], x[1]))
    return [{"stringId": sid, "text": t, "score": sc} for sc, ln, sid, t in cands[:3]]


# ---------------------------------------------------------------- build synergies
tiers_by_rel = defaultdict(list)
for r in rs_rows:
    tiers_by_rel[r["m_relationId"]].append(r)

syn_out = []
text_resolved = 0
for rel in sorted(tiers_by_rel):
    name = synergy_name.get(rel)
    rows = sorted(tiers_by_rel[rel], key=lambda x: x["m_NeedCnt"])
    def is_chance(p):
        return p and p["kind"] == "effect" and p["type"] == "3"
    has_chance = any(
        is_chance(parse_token(t))
        for r in rows for t in r["m_NumDescribe"] if t and t != "0"
    )
    cands = text_candidates(name, has_chance)
    if cands and cands[0]["score"] >= 3:
        text_resolved += 1
    tier_out = []
    for r in rows:
        parsed = [parse_token(t) for t in r["m_NumDescribe"] if t and t != "0"]
        parsed = [p for p in parsed if p]
        shape = "; ".join("Num%d=%s" % (i + 1, shape_phrase(p)) for i, p in enumerate(parsed))
        # literals are resolved; effect-lookups stay templated
        resolved = {"Num%d" % (i + 1): p["value"] for i, p in enumerate(parsed)
                    if p["kind"] == "literal"}
        tier_out.append({
            "need": r["m_NeedCnt"],
            "skillLv": r["m_skillLv"],
            "skillId": r["m_SkillId"],
            "dps": r["m_DPSValue"],
            "rawFormulas": [t for t in r["m_NumDescribe"] if t and t != "0"],
            "parsedFormulas": parsed,
            "effectShape": shape,
            "resolvedValues": resolved or None,  # literals only; effect-lookup N unreachable
        })
    syn_out.append({
        "relId": rel,
        "name": name,
        "axis": synergy_axis.get(rel),
        "effectTextCandidates": cands,
        "effectTextCandidatesNote": "best-match localization strings naming this synergy; "
                                    "mapping to relId/tier NOT verified (text is hash-keyed). "
                                    "score>=3 = synergy named as the effect subject.",
        "tiers": tier_out,
    })

# ---------------------------------------------------------------- hero skills
# active skill = MCHero_S6.m_SkillList[0][0]; description text is hash-keyed -> best loc candidate.
hero_skills = []
hs_resolved = 0
for h in hero_rows:
    hid = h["m_ID"]
    nm = hero_name.get(hid)
    skills = [s[0] for s in h.get("m_SkillList", []) if s]
    active = skills[0] if skills else None
    # candidate: strings naming the hero, skill-like (has placeholder, mentions the hero acting)
    cands = []
    if nm:
        for sid, t in loc.items():
            if nm not in t:
                continue
            if "<Num" not in t and "<%Num" not in t and "[C" not in t:
                continue
            if any(w in t for w in EXCLUDE) or any(w in t for w in MOBA_TELL):
                continue
            if len(t) > 260:
                continue
            score = 0
            if t.strip().startswith(nm) or (nm + " ") in t[:30]:
                score += 3
            if any(w in t for w in ["deal", "DMG", "Skill", "Mana", "Shield", "cast"]):
                score += 1
            cands.append((score, len(t), sid, t))
        cands.sort(key=lambda x: (-x[0], x[1]))
    top = [{"stringId": sid, "text": t, "score": sc} for sc, ln, sid, t in cands[:2]]
    if top and top[0]["score"] >= 4:
        hs_resolved += 1
    hero_skills.append({
        "heroId": hid, "name": nm, "cost": h.get("m_Quality"),
        "activeSkillId": active, "allSkillIds": skills,
        "skillTextCandidates": top,
    })

# ---------------------------------------------------------------- leftover: MCRoundRandomEquip
def decode_round_equip():
    data = open(os.path.join(DEC, "MCRoundRandomEquip.bin"), "rb").read()
    rc = struct.unpack_from("<i", data, 21)[0]
    # schema is alignment-ambiguous (8 EOF-clean candidates); all share prefix i,i,A,A,A,A...
    # we walk with one EOF-exact candidate and surface the reliable leading fields.
    schema = list("iiAAAAAiAiAiAiiAi")

    def rd7(o):
        val = 0; sh = 0
        while True:
            b = data[o]; o += 1; val |= (b & 0x7F) << sh
            if not (b & 0x80):
                break
            sh += 7
        return val, o
    o = 29; rows = []
    for _ in range(rc):
        row = []
        for k in schema:
            if k == "i":
                row.append(struct.unpack_from("<i", data, o)[0]); o += 4
            else:
                c, o = rd7(o); row.append(list(struct.unpack_from("<%di" % c, data, o))); o += 4 * c
        rows.append(row)
    clean = (o == len(data))
    out = []
    for row in rows:
        out.append({
            "seasonOrModeId": row[0],   # 1..7 (live-ish) then 10001/10002 (advance server)
            "levelOrRoundBreak": row[1],  # progression breakpoint (e.g. 3,8,13,18,23,29)
            "equipPool": row[2],          # equip ids eligible to drop
            "equipPoolWeights": row[3],   # parallel weights for equipPool
            "equipPool2": row[4],         # secondary pool (basic components 1001+)
            "equipPool2Weights": row[5],
        })
    return clean, out


re_clean, round_equip = decode_round_equip()

# ---------------------------------------------------------------- assemble
result = {
    "meta": {
        "season": "S6", "status": "live", "version": "1.2.88.302.2",
        "source": "Magic Chess GoGo client (BlueStacks pull), v302.2 decoded tables + localization_en.json",
        "builtBy": "work_dir/saori/mcgg/build_resolved_effects.py",
        "dslSpec": "work_dir/saori/mcgg/FORMULA_DSL.md",
        "numericResolution": "PARTIAL/NONE for synergy formulas: the raw value N is stored in "
            "MCEffect_S1/S2 keyed by the token's composite effect id (e.g. 4010104), which the "
            "client resolves in battle/Lua logic, NOT as a flat int32 row key. Verified: sibling "
            "ids (4010402, 4010702, 47230200) do not appear as int32 in ANY decoded table. The "
            "IL2CPP read-program (on the datamine machine) would be required. So per-tier numbers "
            "stay templated; the formula STRUCTURE (stat kind, unit, scaling expr) is fully parsed.",
        "textResolution": "synergy/hero effect display text is a hash-keyed localization lookup "
            "(no in-table stringId, hash not reproducible; the datamine resolved NAMES positionally "
            "by band). So effect text is given as scored localization CANDIDATES, not authoritative.",
        "dslValidation": "the unit/scaling interpretation is validated against the item ground "
            "truth: a percent attr stored as 2000 displays as 20% (AttrbuteDescribe changePara "
            "1e-4 x 100 = x0.01), which is exactly the synergy DSL expr 'N*0.01' (raw stored x100). "
            "So when a synergy effect N is fetched, expr N*0.01 yields the correct percent. "
            "Confirmed on Inspire-class ATK-Speed items: stored 2000/2500/3000/4000 -> 20/25/30/40%.",
    },
    "synergies": syn_out,
    "heroSkills": hero_skills,
    "leftoverTables": {
        "MCRoundRandomEquip": {
            "parsed": True,
            "consumesToEOF": re_clean,
            "schemaConfidence": "prefix-only (cols 0-5 reliable; 8 EOF-clean full schemas exist, "
                                "trailing column layout ambiguous without IL2CPP)",
            "rowKey": "(seasonOrModeId, levelOrRoundBreak)",
            "note": "round/level -> equipment drop pool(s) + weights. seasonOrModeId 1..7 then "
                    "10001/10002 (advance server). A season-specific MCRoundRandomEquip_S6.bin also exists.",
            "rowCount": len(round_equip),
            "rows": round_equip,
        },
    },
}

p = os.path.join(OUT, "resolved_effects.json")
json.dump(result, open(p, "w"), ensure_ascii=False, indent=1)
print("wrote", p, "(%d KB)" % (os.path.getsize(p) // 1024))
print("synergies:", len(syn_out),
      "| with score>=3 text candidate:", text_resolved, "/", len(syn_out))
print("heroSkills:", len(hero_skills), "| with score>=4 text candidate:", hs_resolved, "/", len(hero_skills))
print("MCRoundRandomEquip rows:", len(round_equip), "consumesToEOF:", re_clean)
# DSL token coverage report
all_toks = [t for r in rs_rows for t in r["m_NumDescribe"] if t and t != "0"]
parsed_ok = sum(1 for t in all_toks if parse_token(t))
print("DSL tokens parsed:", parsed_ok, "/", len(all_toks))
