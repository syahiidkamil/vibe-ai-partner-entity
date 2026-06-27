<!-- GENERATED: stat rows + ids from storage/magic-chess-gogo/game-client-from-bluestack/parsed/strategy/equipment.json (built by work_dir/saori/mcgg/build_equipment.py from the live client v302.2). Stat rows are exact; prose is authored. Regenerate on a season patch. -->

# Equipment (MCGG S6): system, catalog, and stat rows

The items heroes carry, generated exact from the live client. This index holds the **system** and the **data model**; the per-item stat rows live in the detail files. Complements [[equipment_and_economy]] (economy + the gold/pool side); read that first for where items drop. Governed by [[disclaimer]]; the world-model is [[schemata]].

## The count, said precisely

The base table is **97 rows = 61 distinct items**. Each item has a **Basic** form, and most also a separate **Enhanced** row (**36** of 61 carry one). So the often-quoted "97 items" is the row count; the player sees ~61 items, each with a Basic and an Enhanced variant. (Refines [[equipment_and_economy]]'s "~97 base items".) Magic-Crystal items live in a separate table, not these rows.

## The equipment system

- **3 gear slots per hero.** `m_Slot` is `[1,2,3]` on almost every item (a few are slot-restricted, e.g. id 9999 sits in slot 4). Stack up to three items on one hero.
- **Basic vs Enhanced** = `m_EquipUpgradeState` (0 = Basic, 1 = Enhanced). Enhancement does one or both of: **adds an extra Unique Passive** (an `812xx` skill that appears only on enhanced rows, marked `*` in the tables) and/or **raises the stat values** (e.g. id 8052: 35% -> 55%). Verified: 0 Basic rows carry an `812xx`, 13 Enhanced rows do; the rest enhance by swapping the base skill or scaling stats.
- **Where they come from** (not the gold shop): creep (PvE) rounds (pick 1 of a few) and the Go Go Box. Full source/economy detail in [[equipment_and_economy]].

## Categories (the UI tabs)

Split by `m_EquipOrigin`. **Regular (origin 0) is confirmed** by name overlap with the localization catalog; the other four origin codes map to the remaining UI tabs (Magic Crystal, Synergy Exclusive, Commander Exclusive, Special) but the exact code->tab label is **[inferred]** from item composition, not proven from data.

| origin | label | distinct items | detail |
|---|---|---|---|
| 0 | Regular | 23 | [regular_items.md](regular_items.md) |
| 1 | Magic Crystal? [inferred] | 1 | [exclusive_and_special_items.md](exclusive_and_special_items.md) |
| 2 | Commander Exclusive? [inferred] | 16 | [exclusive_and_special_items.md](exclusive_and_special_items.md) |
| 4 | Synergy Exclusive? [inferred] | 17 | [exclusive_and_special_items.md](exclusive_and_special_items.md) |
| 5 | Special? [inferred] | 4 | [exclusive_and_special_items.md](exclusive_and_special_items.md) |
| **total** | | **61** | |

## Type groups, and the stat legend

The UI also groups items as **Basic / Physical / Magic**. This is a display axis over the stat an item is built around, not a single clean field in the table (`m_EquipType` has 6 codes, not 3), so per-item type-group is **resolved only for the named items** below, from the in-game UI.

**Stat values are exact** via `AttrbuteDescribe_MC` (`m_ChangePara` x raw, `m_ShowType` format). Correcting [[equipment_and_economy]]'s guess: the core stats are **percent**, not flat. Per 1000 raw: `1021`,`1031`,`1001`,`1042`,`62`,`1180` = **10%** (ChangePara 0.0001, `0%` format); `1062`,`1072` are **flat integers** (ChangePara 1). Attribute *names* are localized hash lookups with no in-table stringId, so stats are recorded **by attrId**. Pattern-inferred (not asserted): `1021`/`1031` the two damage stats (physical/magic %), `1001` HP %, `1042` Attack Speed %.

## The names wall (honest)

Item **display names cannot be keyed to stat rows from the data**: `m_mItemName` is a localized lookup with no stringId in the table (the same wall the prior parse hit). The names ARE present in localization as ordered bands, harvested into the catalog in [[regular_items]], but listed **unkeyed** to ids. Names asserted against a specific id below are only the two UI-verified anchors.

## Anchors verified (name + effect, cross-checked)

- **Inspire** (Basic, Attack Speed): name band `206779510` (`Inspire`/`Enhanced Inspire`); effect skill `2212458459`, desc `2212461181`: "Provide <Num1> ATK Speed (increases with Stage progression).". UI: provide 20/25/30/40% ATK Speed (rises with Stage); Enhanced adds Unique Passive - Swift (+20% ATK Speed). Stat anchor: attr 1042.
- **Demon Hunter Sword** (Physical, role Tank Killer): name `149526013` (`Demon Hunter Sword`/`Enhanced ...`); passive **Engulf** (`2212492988`), desc `2212493025`: "Basic ATKs deal extra Physical DMG equal to <%Num1> of the target's max HP." (UI: 2% of target max HP).

## The one set

`EquipSuit_MC` has a single set, id 1001: components [1101, 1102] grant skill 25950. components 1101/1102 live in a separate/season table, not the base 97.
