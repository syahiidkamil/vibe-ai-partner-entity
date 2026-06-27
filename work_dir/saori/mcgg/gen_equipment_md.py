#!/usr/bin/env python3
"""Generate the equipments/ markdown for the magic_chess_gogo schema from
equipment.json (built by build_equipment.py), so every stat/id is exact (no
transcription). Prose is authored here; the tables are generated.

Run order: build_equipment.py first (writes equipment.json), then this.
"""
import json, os

SRC = ("vape/entity/storage/magic-chess-gogo/game-client-from-bluestack/"
       "parsed/strategy/equipment.json")
OUT = "vape/entity/memory/schemata/magic_chess_gogo/concrete_things/equipments"
os.makedirs(OUT, exist_ok=True)
D = json.load(open(SRC))
items = D["items"]

HEADER = (
    "<!-- GENERATED: stat rows + ids from "
    "storage/magic-chess-gogo/game-client-from-bluestack/parsed/strategy/equipment.json "
    "(built by work_dir/saori/mcgg/build_equipment.py from the live client v302.2). "
    "Stat rows are exact; prose is authored. Regenerate on a season patch. -->\n"
)


def attr_str(attrs):
    if not attrs:
        return "-"
    out = []
    for a in attrs:
        tag = "EXC" if a.get("exclusive") else ""
        out.append(f"{tag}{a['attrId']}:{a['display']}")
    return ", ".join(out)


def skills_str(block):
    if not block:
        return "-"
    sk = block.get("skills", [])
    extra = set(block.get("extra_passive_skills", []))
    return ", ".join((f"{s}*" if s in extra else str(s)) for s in sk) or "-"


def item_table(rows):
    head = ("| id | cat | tier | slots | Basic stats | Basic skills "
            "| Enh stats | Enh skills |")
    sep = "|---|---|---|---|---|---|---|---|"
    out = [head, sep]
    for it in rows:
        b = it.get("basic")
        e = it.get("enhanced")
        slots = "".join(str(s) for s in it["slots"])
        out.append(
            f"| {it['id']} | {it['category_origin']} | {it['tier']} | {slots} "
            f"| {attr_str(b['attrs']) if b else '-'} | {skills_str(b)} "
            f"| {attr_str(e['attrs']) if e else '-'} | {skills_str(e)} |"
        )
    return "\n".join(out)


# ----------------------------------------------------------------- index.md
m = D["meta"]
cat = m["category_counts"]
anc = D["anchors_verified"]
idx = [HEADER, "# Equipment (MCGG S6): system, catalog, and stat rows", ""]
idx += [
    "The items heroes carry, generated exact from the live client. This index holds the "
    "**system** and the **data model**; the per-item stat rows live in the detail files. "
    "Complements [[equipment_and_economy]] (economy + the gold/pool side); read that first for "
    "where items drop. Governed by [[disclaimer]]; the world-model is [[schemata]].",
    "",
    "## The count, said precisely",
    "",
    f"The base table is **{m['rows']} rows = {m['distinct_items']} distinct items**. Each item has "
    "a **Basic** form, and most also a separate **Enhanced** row "
    f"(**{m['items_with_enhanced_row']}** of {m['distinct_items']} carry one). So the often-quoted "
    f"\"{m['rows']} items\" is the row count; the player sees ~{m['distinct_items']} items, each "
    "with a Basic and an Enhanced variant. (Refines [[equipment_and_economy]]'s \"~97 base "
    "items\".) Magic-Crystal items live in a separate table, not these rows.",
    "",
    "## The equipment system",
    "",
    "- **3 gear slots per hero.** `m_Slot` is `[1,2,3]` on almost every item (a few are "
    "slot-restricted, e.g. id 9999 sits in slot 4). Stack up to three items on one hero.",
    "- **Basic vs Enhanced** = `m_EquipUpgradeState` (0 = Basic, 1 = Enhanced). Enhancement "
    "does one or both of: **adds an extra Unique Passive** (an `812xx` skill that appears only "
    "on enhanced rows, marked `*` in the tables) and/or **raises the stat values** (e.g. id "
    "8052: 35% -> 55%). Verified: 0 Basic rows carry an `812xx`, 13 Enhanced rows do; the rest "
    "enhance by swapping the base skill or scaling stats.",
    "- **Where they come from** (not the gold shop): creep (PvE) rounds (pick 1 of a few) and "
    "the Go Go Box. Full source/economy detail in [[equipment_and_economy]].",
    "",
    "## Categories (the UI tabs)",
    "",
    "Split by `m_EquipOrigin`. **Regular (origin 0) is confirmed** by name overlap with the "
    "localization catalog; the other four origin codes map to the remaining UI tabs (Magic "
    "Crystal, Synergy Exclusive, Commander Exclusive, Special) but the exact code->tab label is "
    "**[inferred]** from item composition, not proven from data.",
    "",
    "| origin | label | distinct items | detail |",
    "|---|---|---|---|",
]
# stable category order by origin code
order = sorted({it["category_origin"]: it["category_label"] for it in items}.items())
cnt = {}
for it in items:
    cnt[it["category_origin"]] = cnt.get(it["category_origin"], 0) + 1
detail_for = {0: "[regular_items.md](regular_items.md)"}
for code, label in order:
    det = detail_for.get(code, "[exclusive_and_special_items.md](exclusive_and_special_items.md)")
    idx.append(f"| {code} | {label} | {cnt[code]} | {det} |")
idx.append(f"| **total** | | **{len(items)}** | |")
idx += [
    "",
    "## Type groups, and the stat legend",
    "",
    "The UI also groups items as **Basic / Physical / Magic**. This is a display axis over the "
    "stat an item is built around, not a single clean field in the table (`m_EquipType` has 6 "
    "codes, not 3), so per-item type-group is **resolved only for the named items** below, from "
    "the in-game UI.",
    "",
    "**Stat values are exact** via `AttrbuteDescribe_MC` (`m_ChangePara` x raw, `m_ShowType` "
    "format). Correcting [[equipment_and_economy]]'s guess: the core stats are **percent**, not "
    "flat. Per 1000 raw: `1021`,`1031`,`1001`,`1042`,`62`,`1180` = **10%** (ChangePara 0.0001, "
    "`0%` format); `1062`,`1072` are **flat integers** (ChangePara 1). Attribute *names* are "
    "localized hash lookups with no in-table stringId, so stats are recorded **by attrId**. "
    "Pattern-inferred (not asserted): `1021`/`1031` the two damage stats (physical/magic %), "
    "`1001` HP %, `1042` Attack Speed %.",
    "",
    "## The names wall (honest)",
    "",
    "Item **display names cannot be keyed to stat rows from the data**: `m_mItemName` is a "
    "localized lookup with no stringId in the table (the same wall the prior parse hit). The "
    "names ARE present in localization as ordered bands, harvested into the catalog in "
    "[[regular_items]], but listed **unkeyed** to ids. Names asserted against a specific id below "
    "are only the two UI-verified anchors.",
    "",
    "## Anchors verified (name + effect, cross-checked)",
    "",
    f"- **Inspire** (Basic, Attack Speed): name band `{anc['Inspire']['skill_name_stringId']}` "
    f"(`Inspire`/`Enhanced Inspire`); effect skill `{anc['Inspire']['effect_skill_name_stringId']}`"
    f", desc `{anc['Inspire']['effect_desc_stringId']}`: \"{anc['Inspire']['effect_desc']}\". "
    "UI: provide 20/25/30/40% ATK Speed (rises with Stage); Enhanced adds Unique Passive - Swift "
    "(+20% ATK Speed). Stat anchor: attr 1042.",
    f"- **Demon Hunter Sword** (Physical, role Tank Killer): name "
    f"`{anc['Demon Hunter Sword']['name_stringId']}` (`Demon Hunter Sword`/`Enhanced ...`); "
    f"passive **Engulf** (`{anc['Demon Hunter Sword']['effect_skill_name_stringId']}`), desc "
    f"`{anc['Demon Hunter Sword']['effect_desc_stringId']}`: "
    f"\"{anc['Demon Hunter Sword']['effect_desc']}\" (UI: 2% of target max HP).",
    "",
    "## The one set",
    "",
    f"`EquipSuit_MC` has a single set, id {D['set']['suit_id']}: components "
    f"{D['set']['components']} grant skill {D['set']['grants_skill']}. {D['set']['note']}.",
    "",
]
open(f"{OUT}/index.md", "w").write("\n".join(idx).rstrip() + "\n")

# -------------------------------------------------- regular_items.md (origin 0)
reg = [it for it in items if it["category_origin"] == 0]
cat_names = D["name_catalog_unkeyed"]
r = [HEADER, "# Regular Items (MCGG S6, origin 0)", ""]
r += [
    f"The standard item pool: **{len(reg)} distinct items** (Basic + Enhanced rows). These are "
    "the MLBB-derived equipment plus the Basic utility set. Stat rows are exact (by attrId; see "
    "[[index]] for the conversion and the names wall). Governed by [[disclaimer]].",
    "",
    "## Named catalog (from localization, unkeyed to ids)",
    "",
    "Display names present in the client but not keyable to the stat rows below. The Basic "
    "utility items resolve to effects from the in-game UI; the rest are the named MLBB items.",
    "",
    "**Basic / utility band:** " + " · ".join(cat_names["basic_and_misc_band_206779510"]),
    "",
    "**Regular named items (Go Go Box catalog, each has Basic + Enhanced):** "
    + " · ".join(cat_names["regular_named_items_from_gogo_catalog"]),
    "",
    "## Basic utility items (effects from the in-game UI)",
    "",
    "The creep-round picks, simple and powerful. Effects per the UI; see [[equipment_and_economy]]"
    " for which round offers them.",
    "",
    "- **Inspire** - Increase ATK Speed. Unique Passive - Inspire: provide 20/25/30/40% ATK Speed "
    "(rises with Stage). Enhanced adds Unique Passive - Swift: +20% ATK Speed.",
    "- **Revitalize** - healing/sustain item (Enhanced variant exists). Effect text not yet "
    "captured from the UI; name confirmed first-party.",
    "- **Purify** - cleanse/anti-CC. Effect text not yet captured; name confirmed.",
    "- **Aegis** - shield. Effect text not yet captured; name confirmed.",
    "- **Retribution** - jungle/economy (slow + extra gold on affected kills, per the keyword "
    "prose). Effect text not yet fully captured; name confirmed.",
    "",
    "## Verified named item: Demon Hunter Sword (Physical, Tank Killer)",
    "",
    "+10% ATK Speed; Unique Passive - **Engulf**: basic ATKs deal extra Physical DMG equal to "
    "2% of the target's max HP. (Name + effect both confirmed first-party; see [[index]] for "
    "the stringIds.) Not yet keyed to a specific id row below.",
    "",
    "## Stat rows (exact, by attrId)",
    "",
    "`*` on a skill = an Enhanced-only extra Unique Passive (`812xx`). `cat` = origin code. "
    "Stat = `attrId:value` (EXC = exclusive slot). See [[index]] for attrId meanings.",
    "",
    item_table(reg),
    "",
]
open(f"{OUT}/regular_items.md", "w").write("\n".join(r).rstrip() + "\n")

# ------------------------- exclusive_and_special_items.md (origin 1/2/4/5)
other = [it for it in items if it["category_origin"] != 0]
groups = {}
for it in other:
    groups.setdefault(it["category_origin"], []).append(it)
e = [HEADER, "# Exclusive & Special Items (MCGG S6)", ""]
e += [
    f"The non-Regular pool: **{len(other)} distinct items** across four UI tabs (Magic Crystal, "
    "Synergy Exclusive, Commander Exclusive, Special). The exact `m_EquipOrigin` code -> tab "
    "label is **[inferred]** from item composition (only Regular/origin-0 is name-confirmed), so "
    "the groups below are labelled by origin code with the best-guess tab. Stat rows are exact. "
    "Governed by [[disclaimer]]; system + conversion in [[index]].",
    "",
    "These items skew to large multi-stat blocks and synergy/commander-tied skills (the `45xxxx`/"
    "`47xxxx`/`48xxxx` skill ids, distinct from Regular's `25xxx`/`28xxx`). Names for these are "
    "not in the clean Regular catalog and are left unresolved.",
    "",
]
for code in sorted(groups):
    label = groups[code][0]["category_label"]
    n = len(groups[code])
    e.append(f"## origin {code} - {label} ({n} item{'s' if n != 1 else ''})")
    e.append("")
    e.append("`*` = Enhanced-only extra passive. Stat = `attrId:value` (EXC = exclusive slot).")
    e.append("")
    e.append(item_table(groups[code]))
    e.append("")
open(f"{OUT}/exclusive_and_special_items.md", "w").write("\n".join(e).rstrip() + "\n")

print("wrote:", sorted(os.listdir(OUT)))
print("regular:", len(reg), "other:", len(other),
      "groups:", {k: len(v) for k, v in groups.items()})
