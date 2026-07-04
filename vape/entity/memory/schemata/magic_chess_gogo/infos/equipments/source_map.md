# Source Map: where the equipment facts come from

Provenance for the per-tab files — [regular](regular.md), [magic_crystal](magic_crystal.md),
[synergy_exclusive](synergy_exclusive.md), [commander_exclusive](commander_exclusive.md),
[special](special.md) — and [index](index.md), kept here so those stay essentials-only. Two
sources: the in-game Equipment UI (names + effects + per-item Basic/Enhanced detail panels) and the
parsed base table (exact stats, by id). Governed by [[disclaimer]].

## Names: keyed to stat rows by UI position, anchored (the bridge)

**The data wall stands:** the parsed tables do not key names to stat rows. `m_mItemName` is null
across all 97 rows, the icon code is just the id (`Atlas_EquipIcon_MC/2006`), and no equip field
holds a name stringId (verified: 0/97). The names DO exist in the localization pool but as
MLBB-series stringIds not ordered by MCGG equip id, so they don't map by stringId either.

**The bridge that works (Regular tab):** sort each UI stat-group's origin-0 ids ascending and align
them to the UI's in-group order. This is **anchor-validated** — 6 items whose stats are confirmed by
a UI detail panel each land at exactly their positional slot:

| Anchor item | id | confirmed stat | slot in its group |
|---|---|---|---|
| Demon Hunter Sword | 2006 | +10% ATK Speed | Physical #1 |
| War Axe | 2013 | +10% Phys, +15% Spell Vamp | Physical #3 |
| Berserker's Fury | 3003 | +10% Phys, +20% Crit Ch, +40% Crit DMG | Physical #5 |
| Glowing Wand | 3102 | +15% Magic ATK | Magic #2 |
| Blade Armor | 2207 | +50 Physical DEF | Defense #1 |
| Claude's Theft Device | 3999 | +10% Phys +10% Magic (= +10% Hybrid) | Hybrid #5 |

Six anchors across four groups all hitting their slot validates the positional key. So: the **stat
values are exact** (by id, from data) and **name↔id is anchor-certain for those 6, positional for
the other 17** (stats right, name-pairing inferred by id-order, not each panel-checked).

**Lifesteal tension RESOLVED:** id `2013` (+10% Phys, +15% Spell Vamp) is **War Axe** — confirmed by
its UI panel (subtitle "Spell Vamp"). My earlier MLBB-lore doubt (that lifesteal should be Haas'
Claws) was wrong; the positional key held. All four groups now map cleanly.

Source: in-game Equipment UI, captured per tab (S6, 2026-06-28):
`storage/magic-chess-gogo/equipment_samples/{regular,magic_crystal,synergy_exclusive,
commander_exclusive,special}/*.png`, plus detail shots `inspire.png`, `demon_hunter_sword.png`,
`glowing_wand.png`, `war_axe` (basic + enhanced). The 5 Basic actives (Inspire, Revitalize, Purify,
Aegis, Retribution) are NOT in the 97-row table (a separate active-item system); the 23 origin-0 rows
are exactly the 23 combat items (Physical 7, Magic 4, Defense 7, Hybrid 5).

## Enhanced form: values come from the UI panels, not the static tables

The passive **numbers** (War Axe Fighting Spirit 4→6 Hybrid DEF / +10%→+30% DMG; Purple Buff Malefic
+20% Hybrid ATK; etc.) are **not in the decoded tables** — they live behind composite effect-ids the
client resolves at runtime (proven three ways: the `81xxx` enhanced-passive skills have no definition
row anywhere; the basic-passive tokens point at composite effect-ids like `2507100` that never appear
as a flat int32 row; every "gain N% …" loc string is `<Num>`-templated). Same wall as the synergy
per-tier values. **So the UI detail panels are the canonical value source — and they are now captured
per item** (Basic + Enhanced) under `storage/magic-chess-gogo/equipments/`, transcribed into the
per-tab files. The data still supplies the exact **stat block** and *that* an enhance happens; the
enhance *mechanism* it can see (skill id basic→enh):
- **Stat gain on enhance:** Thunder Belt (+20% Max HP), and the exclusive/synergy items whose stat
  block rises Basic→Enhanced.
- **Adds a 2nd Unique Passive `812xx`:** Sea Halberd (Pierce), Berserker's Fury (Valiant), Haas'
  Claws (Frenzy), Divine Glaive (Spellbreaker), Ice Queen Wand (Extract), Blade Armor (Defiance),
  Guardian Helmet (Titan), Purple Buff (Malefic) — names+values now from the panels.
- **Skill id changes:** Oracle `28130→28135`, Spellblade `25950→25954`, Feline Blade
  `27999→2027999`, Claude's `28040→28041` — deltas now from the panels.
- **Same skill id, scaling that was INVISIBLE in data:** Demon Hunter Sword (Engulf 2→4%), Golden
  Staff (Impulsive 2→3.5%), War Axe, Blade of Despair (Despair 25→50%), Glowing Wand (Scorch
  2.5→5%), Holy Crystal (Mystery 10→30%), Antique Cuirass (Deter 4→7%), Dominance Ice (25→50% mana),
  Ancient Wrath (10→18 DEF), Winter Crown — all confirmed scaling, captured from the Enhanced panels.

## Completeness (this pass, 2026-06-28)

- **Regular — complete** (4 shots, top-to-bottom): 28 items (Basic 5, Physical 7, Magic 4, Defense 7,
  Hybrid ATK 5). The UI corrects the old loc-harvested list (e.g. Great Dragon Spear and Essence Core
  are Commander Exclusive, not Regular).
- **Magic Crystal — complete** (2 shots): 16 (15 synergy crystals + Go Go Crystal). These live in a
  separate table, not the 97-row base (the base table shows only 1 origin-1 row, id 9999).
- **Commander Exclusive — complete** (2 shots): 15 (Defense 2, Hybrid ATK 8, Consumable 5).
- **Synergy Exclusive — PARTIAL** (1 shot): 4 of ~17 captured. Needs more scroll shots.
- **Special — PARTIAL** (1 shot): 2 of ~4 captured. Needs more scroll shots.

## Count reconciliation (UI vs data)

The parsed base table is **97 rows = 61 distinct items** (each item a Basic row, 36 also an Enhanced
row). Origin codes split it: 0 Regular (23), 1 (1), 2 (16), 4 (17), 5 (4). The UI tab counts differ
because Magic-Crystal items are a separate table (16 in UI vs 1 origin-1 row) and the loc-harvested
Regular list over/under-counted vs the live tab (28). The UI is authoritative for names and grouping;
the base table is authoritative for exact stats.

## Anchors verified (name + effect + stringIds)

- **Inspire** — name band `206779510`; effect skill `2212458459`, desc `2212461181`. UI: 20/25/30/40%
  ATK Speed; Enhanced adds Swift (+20% ATK Speed). Stat attr 1042.
- **Demon Hunter Sword** — name `149526013`; passive Engulf `2212492988`, desc `2212493025` (2% of
  target max HP). +10% ATK Speed.
- **Glowing Wand** — +15% Magic ATK; passive Scorch (burn 2.5% max HP/s 3s, -30% Healing 3s).

## Stat system (exact, by attrId)

Stat values are exact via `AttrbuteDescribe_MC` (`m_ChangePara` x raw, `m_ShowType` format). Per 1000
raw: `1021`,`1031`,`1001`,`1042`,`62`,`1180` = **10%** (ChangePara 0.0001, `0%` format); `1062`,`1072`
= **flat integers** (ChangePara 1). **AttrId legend now resolved from the UI panels:** `1021` Physical
ATK %, `1031` Magic ATK %, `1001` Max HP %, `1042` ATK Speed %, `62` Spell Vamp %, `18` Crit Chance %,
`22` Crit DMG %, `1062` Physical DEF (flat), `1072` Magic DEF (flat), `1180` **DMG Reduction %** (not
CDR), `EXC12` **Physical Penetration %**, `EXC13` **Magic Penetration %**, `EXC92` **Lifesteal %**.
Attribute *names* are localized hash lookups with no in-table stringId, so the table records by attrId
and the panels supply the names. `m_Slot` is `[1,2,3]` on almost every item (id 9999 sits in slot 4);
`m_EquipUpgradeState` 0 = Basic, 1 = Enhanced. `EquipSuit_MC` has one set, id 1001: components
[1101, 1102] grant skill 25950.

## Raw stat rows (by id — exact, not name-keyed)

Built by `work_dir/saori/mcgg/build_equipment.py` from the live client (v302.2). `*` = Enhanced-only
extra passive (`812xx`). `cat` = `m_EquipOrigin`.

### origin 0 — Regular
| id | tier | slots | Basic stats | Basic skills | Enh stats | Enh skills |
|---|---|---|---|---|---|---|
| 2006 | 2 | 123 | 1042:10% | 25003 | 1042:10% | 25003 |
| 2009 | 2 | 123 | 1042:15% | 25940 | 1042:15% | 25940 |
| 2013 | 2 | 123 | 1021:10%, 62:15% | 25060 | 1021:10%, 62:15% | 25060 |
| 2106 | 2 | 123 | 1031:15%, 1021:15% | 25950 | 1031:15%, 1021:15% | 25954 |
| 2108 | 2 | 123 | 1031:25%, EXC13:40% | - | 1031:25%, EXC13:40% | 81299* |
| 2113 | 2 | 123 | 1031:10%, 1021:10%, 1001:10% | 26020 | (same) | 26020 |
| 2207 | 2 | 123 | 1062:50 | 25019 | 1062:50 | 25019, 81292* |
| 2302 | 2 | 123 | 1021:15%, EXC12:40% | 25056 | (same) | 25056, 81271* |
| 2304 | 2 | 123 | 1001:15% | 25044 | 1001:15% | 25044, 81281* |
| 3003 | 2 | 123 | 1021:10%, 18:20%, 22:40% | - | (same) | 81287* |
| 3008 | 2 | 123 | 1021:20% | 25850 | 1021:20% | 25850 |
| 3013 | 2 | 123 | 1021:20%, 18:15%, EXC92:15% | - | (same) | 81311* |
| 3102 | 2 | 123 | 1031:15% | 25007 | 1031:15% | 25007 |
| 3104 | 2 | 123 | 1031:15%, 62:15% | 25080 | (same) | 25080, 81283* |
| 3105 | 2 | 123 | 1031:20% | 26050 | 1031:20% | 26050 |
| 3110 | 2 | 123 | 1021:15%, 1031:15%, 1001:10% | 27999 | (same) | 2027999 |
| 3203 | 2 | 123 | 1001:10%, 1180:10% | 25090 | (same) | 25090 |
| 3208 | 2 | 123 | 1062:20, 1072:20 | 28530 | 1062:20, 1072:20, 1001:20% | 28530 |
| 3211 | 2 | 123 | 1062:20, 1072:20 | 28130 | 1062:20, 1072:20 | 28135 |
| 3214 | 2 | 123 | 1072:50, 1001:10% | 28120 | (same) | 28120 |
| 3997 | 2 | 123 | 1001:15% | 28510 | 1001:15% | 28510 |
| 3998 | 2 | 123 | 1021:10%, 1031:10% | 26060 | (same) | 26060, 81289* |
| 3999 | 2 | 1 | 1021:10%, 1031:10% | 28040 | (same) | 28041 |

### origin 1 — Magic Crystal table (base row)
| id | tier | slots | Basic skills |
|---|---|---|---|
| 9999 | 2 | 4 | 26100 |

### origin 2 — Commander Exclusive
| id | tier | Basic skills | Enh skills |
|---|---|---|---|
| 4001 | 1 | 28060 | 28060, 81295* |
| 4002 | 1 | 28070 | 28070, 81296* |
| 4004 | 1 | 28090 (1042:15%) | 28090, 81295* |
| 4005 | 1 | 28100 | - |
| 4008 | 1 | 28140 | 28140, 81296* |
| 4009 | 1 | 28150 | 28150, 81297* |
| 4102 | 1 | 28420 | - |
| 4103 | 1 | 28090 (1042:20%) | - |
| 4104 | 1 | 28430 | - |
| 4105 | 1 | 28470 | - |
| 4106 | 1 | 28490 | - |
| 4107 | 1 | 28440 | - |
| 4108 | 1 | 28450 | - |
| 4109 | 1 | 28460 | - |
| 4110 | 1 | 28480 | - |
| 4111 | 1 | 28500 | - |

### origin 4 — Synergy Exclusive
| id | tier | Basic stats | Basic skills | Enh stats | Enh skills |
|---|---|---|---|---|---|
| 4006 | 2 | - | 451980 | - | - |
| 4007 | 2 | - | 452570 | - | - |
| 4050 | 2 | - | 470721 | 1021:20%, 1031:20% | 470721 |
| 4052 | 2 | 1021:10%, 1031:10%, 1001:10% | 481650 | 1021:20%, 1031:20%, 1001:20% | 481650 |
| 8052 | 2 | 1021:35%, 1031:35%, 1001:25% | 471630 | 1021:55%, 1031:55%, 1001:30% | 471630 |
| 8053 | 2 | 1021:35%, 1031:35%, 1001:25% | 471631 | 1021:55%, 1031:55%, 1001:30% | 471631 |
| 8054 | 2 | 1021:20%, 1031:20% | 451801 | 1021:40%, 1031:40% | 451801 |
| 8055 | 2 | 1001:20% | 451811 | 1001:40% | 451811 |
| 8056 | 2 | 1021:20%, 1031:20% | 451801, 451820 | 1021:40%, 1031:40% | 451801, 451820 |
| 8057 | 2 | 1001:20% | 451811, 10451820 | 1001:40% | 451811, 10451820 |
| 8061-8065 | 2 | - | 471920 | - | - |
| 8066 | 2 | - | 28010 | - | - |
| 85130 | 3 | - | 85131 | - | - |

### origin 5 — Special
| id | tier | Basic skills |
|---|---|---|
| 3210 | 2 | 28010 |
| 9000 | 2 | 29000 |
| 80760 | 3 | 80761 |
| 83100 | 2 | 83101 |
