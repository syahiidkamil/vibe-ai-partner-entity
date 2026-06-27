"""Build all parsed/* outputs for MCGG v302.2 from the cracked mulong format.

Writes into  .../game-client-from-bluestack/parsed/ :
  - localization_en.json          {stringId: text} from AllLanguageEN.bin
  - <Table>.json                  per-table clean parses (reference-backed)
  - dataset_live_s6.json          consolidated {meta, heroes, synergies, items}

Run:  uv run python3 work_dir/saori/mcgg/build_outputs.py
"""
import sys, os, json
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import mulong_parse as mp

BASE = os.path.join(ROOT, "vape/entity/storage/magic-chess-gogo/game-client-from-bluestack")
DEC = os.path.join(BASE, "readable/decoded")
FR = os.path.join(ROOT, "vape/entity/storage/magic-chess-gogo/game-client-from-friend")
OUT = os.path.join(BASE, "parsed")
os.makedirs(OUT, exist_ok=True)
VERSION = "1.2.88.302.2"


def reff(name):
    return json.load(open(os.path.join(FR, name)))


def parse_ref(binname, refname):
    """Parse a bin using a schema inferred from the friend's matching JSON."""
    schema = mp.infer_schema(reff(refname))
    res = mp.parse(os.path.join(DEC, binname + ".bin"), schema)
    return res


def write(name, obj):
    p = os.path.join(OUT, name)
    json.dump(obj, open(p, "w"), ensure_ascii=False, indent=1)
    return p, (os.path.getsize(p))


# ---------------------------------------------------------------- localization
print("Parsing localization ...")
loc = mp.parse_localization(os.path.join(DEC, "AllLanguageEN.bin"))
loc_str = {str(k): v for k, v in loc.items()}
p, sz = write("localization_en.json", loc_str)
print(f"  localization_en.json  {len(loc)} entries  ({sz//1024} KB)")

# ---------------------------------------------------------------- per-table
TABLES = [
    ("MCHero", "MCHero.json"),
    ("MCHero_S6", "MCHero_S6.json"),
    ("MCHeroStarlevel_S6", "MCHeroStarlevel_S6.json"),
    ("RelationSkill_MC_S6", "RelationSkill_MC_S6.json"),
    ("RelationSkillTip_MC_S6", "RelationSkillTip_MC_S6.json"),
    ("MCEquipBase", "MCEquipBase.json"),
    ("AttrbuteDescribe_MC", "AttrbuteDescribe_MC.json"),
    ("MCHeroRecommendRelation", "MCHeroRecommendRelation.json"),
]
parsed = {}
print("Parsing tables ...")
for binname, refname in TABLES:
    res = parse_ref(binname, refname)
    parsed[binname] = res
    write(binname + ".json", res["rows"])
    flag = "clean" if res.get("clean") else "CHECK"
    print(f"  {binname:26} ver{res['version']} rows={res['rowcount']:>4} {flag}")

# ------------------------------------------------------------ name resolution
# hero id -> name : reuse the friend's client-derived roster-band resolution
#                   (hero id->name is stable across the 302.1->302.2 patch);
#                   each is verified present in our v302.2 localization below.
fr_ds = reff("dataset_s6.json")
hero_name = {h["id"]: h["name"] for h in fr_ds["heroes"]}
hero_summon = {h["id"]: h.get("isSummon", False) for h in fr_ds["heroes"]}
loc_values = set(loc.values())
hero_name_current = {hid: (nm in loc_values) for hid, nm in hero_name.items()}

# synergy relId -> name : FIRST-PARTY.
#   class band  loc[493757747 + (relId-1)]   (relId 1..10)
#   faction band loc[2012764216 + (relId-50)] (relId 50..59)
#   relId 8 & 10 class names are stale in the band; resolved by FX_Fetter pinyin
#   + all-assassin / all-phaser membership + the live UI set.
CLASS_BASE, FACT_BASE = 493757747, 2012764216
SYN_OVERRIDE = {8: "Assassin", 10: "Phasewarper"}  # band='Swiftblade'/None; live name


def synergy_name(rel):
    if rel in SYN_OVERRIDE:
        return SYN_OVERRIDE[rel], "fx_pinyin+membership (band stale)"
    if rel < 50:
        return loc.get(CLASS_BASE + (rel - 1)), "class band loc[%d]" % (CLASS_BASE + rel - 1)
    return loc.get(FACT_BASE + (rel - 50)), "faction band loc[%d]" % (FACT_BASE + rel - 50)


# ------------------------------------------------------- hero -> synergy membership
hero_rows = parsed["MCHero_S6"]["rows"]
members = defaultdict(list)
for r in hero_rows:
    for rel in r["m_Sort"]:
        members[rel].append(r["m_ID"])

# ------------------------------------------------------- synergy tiers (RelationSkill)
rs_rows = parsed["RelationSkill_MC_S6"]["rows"]
tiers = defaultdict(list)
fx = defaultdict(set)
for r in rs_rows:
    rel = r["m_relationId"]
    tiers[rel].append({
        "need": r["m_NeedCnt"],
        "skillLv": r["m_skillLv"],
        "skillId": r["m_SkillId"],
        "dps": r["m_DPSValue"],
        "valueFormulas": [x for x in r["m_NumDescribe"] if x != "0"],
    })
    if r.get("m_RelationHeadEff"):
        fx[rel].add(r["m_RelationHeadEff"])

# ------------------------------------------------------- synergy display (RelationSkillTip)
tip_rows = parsed["RelationSkillTip_MC_S6"]["rows"]
tip = {r["m_RelationId"]: r for r in tip_rows}

synergies = []
for rel in sorted(tip):
    name, ev = synergy_name(rel)
    t = tip[rel]
    mh = [h for h in members.get(rel, []) if not hero_summon.get(h, False)]
    synergies.append({
        "relId": rel,
        "name": name,
        "nameEvidence": ev,
        "axis": "class" if t["m_RelationType"] == 2 else "faction",
        "displayOrder": t["m_HandBookSeq"],
        "icon": t["m_RelationIcon"],
        "recommendEquipId": t.get("m_EquipID"),
        "fxName": sorted(fx.get(rel, [])),
        "memberHeroes": mh,
        "memberNames": [hero_name.get(h, "id%d" % h) for h in mh],
        "tiers": tiers.get(rel, []),
    })

# ------------------------------------------------------- per-star stats (Starlevel)
star_rows = parsed["MCHeroStarlevel_S6"]["rows"]
stars = defaultdict(list)
for r in star_rows:
    stars[r["m_ID"]].append({
        "star": r["m_StarId"],
        "hp": r["m_BaseHp"], "phyAtk": r["m_BasePhyAtt"], "magAtk": r["m_BaseMagAtt"],
        "phyDef": r["m_PhyBaseShield"], "magDef": r["m_MagBaseShield"],
        "atkSpeed": r["m_AttSpeed_show"], "moveSpeed": r["m_MoveSpeed"],
        "crit": r["m_Crit"], "dps": r["m_DPSValue"], "ehp": r["m_EHPValue"],
        "buyPrice": r["m_BuyingPrice"],
    })

# ------------------------------------------------------- heroes
heroes = []
for r in hero_rows:
    hid = r["m_ID"]
    heroes.append({
        "id": hid,
        "name": hero_name.get(hid),
        "nameInCurrentLoc": hero_name_current.get(hid),
        "codename": r["m_Prefabs"],
        "cost": r["m_Quality"],
        "synergies": r["m_Sort"],
        "synergyNames": [synergy_name(s)[0] for s in r["m_Sort"]],
        "skills": [s[0] for s in r["m_SkillList"]],
        "isTank": bool(r["m_IsTank"]),
        "headIcon": r["m_Head"],
        "stars": sorted(stars.get(hid, []), key=lambda s: s["star"]),
    })

# ------------------------------------------------------- items (MCEquipBase ver-1)
# attr percent flag from AttrbuteDescribe (m_ShowType contains '%')
attr_rows = parsed["AttrbuteDescribe_MC"]["rows"]
attr_percent = {}
for r in attr_rows:
    if r.get("m_ID") is not None:
        attr_percent[r["m_ID"]] = "%" in (r.get("m_ShowType") or "")

item_rows = parsed["MCEquipBase"]["rows"]
items = []
for r in item_rows:
    attrs = []
    pairs = [("m_Attr1", "m_AttrValue1"), ("m_Attr2", "m_AttrValue2"), ("m_Attr3", "m_AttrValue3"),
             ("m_ExtraAttr1", "m_ExtraAttrValue1"), ("m_ExtraAttr2", "m_ExtraAttrValue2"),
             ("m_ExtraAttr3", "m_ExtraAttrValue3"), ("m_ExclusiveAttr1", "m_ExclusiveAttrValue1")]
    for ak, vk in pairs:
        aid = r.get(ak, 0)
        if aid:
            attrs.append({"attrId": aid, "value": r.get(vk, 0),
                          "percent": attr_percent.get(aid),
                          "name": None})  # display name = hashed/unresolvable (see report)
    items.append({
        "id": r["m_EuqipID"],
        "name": None,            # m_mItemName is a localized hash lookup -> unresolvable
        "tier": r.get("m_ModelLevel"),
        "icon": (r.get("m_Icon") or [None])[0],
        "slot": r.get("m_Slot"),
        "attrs": attrs,
        "skills": [s[0] for s in r.get("m_SkillList", [])],
    })

# ------------------------------------------------------- consolidated dataset
dataset = {
    "meta": {
        "season": "S6", "status": "live", "label": "S6 (live)",
        "source": "Magic Chess GoGo client (BlueStacks pull)",
        "version": VERSION,
        "heroCount": len(heroes), "synergyCount": len(synergies), "itemCount": len(items),
        "notes": "Synergy names resolved first-party (localization bands + FX_Fetter pinyin "
                 "+ membership). Hero names reuse the friend's client-derived roster-band map, "
                 "each verified present in this build's localization. Item display names and "
                 "item-attribute display names are localized hash lookups with no in-table "
                 "stringId and could not be resolved from data (left null).",
    },
    "synergies": synergies,
    "heroes": heroes,
    "items": items,
}
p, sz = write("dataset_live_s6.json", dataset)
print(f"\n  dataset_live_s6.json  heroes={len(heroes)} synergies={len(synergies)} items={len(items)}  ({sz//1024} KB)")

# ------------------------------------------------------- quick verification print
named = sum(1 for s in synergies if s["name"])
print(f"\nVERIFICATION")
print(f"  synergies named: {named}/{len(synergies)}")
print(f"  hero names present in v302.2 loc: {sum(hero_name_current.values())}/{len(hero_name_current)}")
print(f"  item attr percent flags resolved: "
      f"{sum(1 for it in items for a in it['attrs'] if a['percent'] is not None)} of "
      f"{sum(len(it['attrs']) for it in items)} attr-slots")
print("  synergy table:")
for s in synergies:
    print(f"    relId {s['relId']:>2} {s['axis']:7} {str(s['name']):16} <- {s['nameEvidence']}")
