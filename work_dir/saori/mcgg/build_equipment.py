"""
Build the MCGG S6 equipment provenance JSON, generated EXACT from the live client.

Sources (all under vape/entity/storage/magic-chess-gogo/game-client-from-bluestack/parsed/):
  - MCEquipBase.json        97 rows (61 distinct ids; Basic + Enhanced via m_EquipUpgradeState)
  - AttrbuteDescribe_MC.json per-attrId display scale (m_ChangePara) + format (m_ShowType)
  - EquipSuit_MC.json        (read from game-client-from-friend; identical for S6) the one set
  - localization_en.json     {stringId: text} for the item-NAME catalog (not keyed to ids)

What is solid (from data): the per-id stat blocks (attrId + value), display conversion,
tier (m_ModelLevel), slots (m_Slot), skill ids (m_SkillList), Basic/Enhanced pairing,
the 812xx enhanced extra-passive, category (m_EquipOrigin), the set.

What is NOT keyable from data: item display names and attribute display names are
localized hash lookups with no in-table stringId. The name CATALOG is harvested from
localization bands and listed separately, honestly unkeyed to the stat rows.

Run: uv run python3 work_dir/saori/mcgg/build_equipment.py
"""
import json, os, bisect

ROOT = "vape/entity/storage/magic-chess-gogo"
P = f"{ROOT}/game-client-from-bluestack/parsed"
OUT = f"{P}/strategy/equipment.json"


def load(name, base=P):
    return json.load(open(f"{base}/{name}"))


def main():
    equip = load("MCEquipBase.json")
    attr = load("AttrbuteDescribe_MC.json")
    suit = load("EquipSuit_MC.json", base=f"{ROOT}/game-client-from-friend")
    loc = {int(k): v for k, v in load("localization_en.json").items()}

    cp = {r["m_ID"]: (r["m_ChangePara"], r["m_ShowType"]) for r in attr}

    def disp(aid, val):
        c, s = cp.get(aid, (1.0, "0"))
        d = val * c
        if "%" in s:
            return {"display": f"{round(d * 100)}%", "percent": True}
        return {"display": f"{round(d)}", "percent": False}

    def attrs_of(r):
        out = []
        for i in (1, 2, 3):
            a, v = r.get(f"m_Attr{i}"), r.get(f"m_AttrValue{i}")
            if a:
                out.append({"attrId": a, "raw": v, **disp(a, v)})
        a, v = r.get("m_ExclusiveAttr1"), r.get("m_ExclusiveAttrValue1")
        if a:
            out.append({"attrId": a, "raw": v, "exclusive": True, **disp(a, v)})
        return out

    def skills(r):
        return [s[0] for s in r["m_SkillList"]]

    # group rows by equip id -> {basic, enhanced}
    by = {}
    for r in equip:
        by.setdefault(r["m_EuqipID"], {})[
            "enhanced" if r["m_EquipUpgradeState"] == 1 else "basic"
        ] = r

    ORIGIN = {0: "Regular", 1: "Magic Crystal? [inferred]", 2: "Commander Exclusive? [inferred]",
              4: "Synergy Exclusive? [inferred]", 5: "Special? [inferred]"}

    items = []
    for eid in sorted(by):
        rows = by[eid]
        anchor = rows.get("basic") or rows.get("enhanced")
        item = {
            "id": eid,
            "icon": anchor["m_Icon"][0] if anchor.get("m_Icon") else None,
            "category_origin": anchor["m_EquipOrigin"],
            "category_label": ORIGIN.get(anchor["m_EquipOrigin"], "?"),
            "equip_type_code": anchor["m_EquipType"],
            "special_type_code": anchor["m_SpecialType"],
            "tier": anchor["m_ModelLevel"],
            "slots": anchor["m_Slot"],
            "has_enhanced_row": "enhanced" in rows,
        }
        if "basic" in rows:
            item["basic"] = {"attrs": attrs_of(rows["basic"]), "skills": skills(rows["basic"])}
        if "enhanced" in rows:
            er = rows["enhanced"]
            sk = skills(er)
            item["enhanced"] = {
                "attrs": attrs_of(er),
                "skills": sk,
                "extra_passive_skills": [s for s in sk if 81000 <= s < 82000],
            }
        items.append(item)

    # ---- name catalog (unkeyed): harvest clean localization bands ----
    keys = sorted(loc)

    def band(lo, hi):
        i = bisect.bisect_left(keys, lo)
        return [(k, loc[k]) for k in keys[i:] if k <= hi]

    # Basic/utility + a few, the 206779510 run
    util = [t for k, t in band(206779510, 206929427)]
    # Regular named items: GoGo-box "Enhanced X" catalog, strip the prefix
    reg = []
    for k, t in band(3157212089, 3157212152):
        if t.startswith("Enhanced "):
            reg.append(t[len("Enhanced "):])
    name_catalog = {
        "note": ("display names present in client localization but NOT keyable to equip "
                 "ids (no in-table stringId). Listed for coverage, honestly unkeyed."),
        "basic_and_misc_band_206779510": util,
        "regular_named_items_from_gogo_catalog": sorted(set(reg)),
    }

    # ---- anchors verified ----
    anchors = {
        "Inspire": {
            "skill_name_stringId": 206779510, "enhanced_name_stringId": 206779511,
            "effect_skill_name_stringId": 2212458459,
            "effect_desc_stringId": 2212461181,
            "effect_desc": loc[2212461181],
            "ui_ground_truth": "Provide 20/25/30/40% ATK Speed (increases with Stage); "
                               "Enhanced adds Unique Passive - Swift: +20% ATK Speed.",
            "stat_anchor_attr": "1042 (Attack Speed%, 10% per 1000 raw)",
        },
        "Demon Hunter Sword": {
            "name_stringId": 149526013, "enhanced_name_stringId": 149526014,
            "effect_skill_name_stringId": 2212492988,  # Engulf
            "effect_desc_stringId": 2212493025,
            "effect_desc": loc[2212493025],
            "ui_ground_truth": "+10% ATK Speed; Unique Passive - Engulf: basic ATKs deal "
                               "extra Physical DMG = 2% of target max HP. Role: Tank Killer.",
        },
    }

    from collections import Counter
    cat_counts = Counter(it["category_label"] for it in items)

    data = {
        "meta": {
            "season": "S6", "source": "Magic Chess GoGo client (BlueStacks pull) v1.2.88.302.2",
            "rows": len(equip), "distinct_items": len(items),
            "items_with_enhanced_row": sum(1 for it in items if it["has_enhanced_row"]),
            "category_counts": dict(cat_counts),
            "generated_by": "work_dir/saori/mcgg/build_equipment.py",
            "names_caveat": ("item + attribute display names are localized hash lookups with "
                             "no in-table stringId; stat rows are by id, names left unkeyed."),
        },
        "attr_conversion": {
            str(r["m_ID"]): {"change_para": r["m_ChangePara"], "show_type": r["m_ShowType"]}
            for r in attr if r["m_ID"] in {1021, 1031, 1001, 1042, 1062, 1072, 18, 62, 22,
                                           1180, 12, 13, 92}
        },
        "set": {"suit_id": suit[0]["m_SuitID"], "components": suit[0]["m_EquipIDlist"],
                "grants_skill": suit[0]["m_SuitSkillList"][0][0],
                "note": "components 1101/1102 live in a separate/season table, not the base 97"},
        "anchors_verified": anchors,
        "name_catalog_unkeyed": name_catalog,
        "items": items,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(data, open(OUT, "w"), ensure_ascii=False, indent=1)
    print("wrote", OUT)
    print("distinct items:", len(items), "rows:", len(equip),
          "with enhanced:", data["meta"]["items_with_enhanced_row"])
    print("category counts:", dict(cat_counts))


if __name__ == "__main__":
    main()
