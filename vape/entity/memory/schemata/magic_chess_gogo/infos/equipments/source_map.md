# Source Map: where the equipment facts come from

Provenance for [index](index.md), [regular_items](regular_items.md), and
[exclusive_and_special_items](exclusive_and_special_items.md), kept here so those stay
essentials-only. Two sources: the in-game Equipment UI (names + effects) and the parsed base table
(exact stats, by id). Governed by [[disclaimer]].

## Names: in localization, but not keyed to the stat rows

The item names DO exist in the parsed data, in the localization pool (e.g. Demon Hunter Sword =
stringId `149526013`, Glowing Wand = `179074841`; 22 of the 28 regular names resolve to a unique
stringId, the rest are common words with several). What is missing is the **key** from a name to its
equip stat-row: `m_mItemName` is null across all 97 rows, the icon code is just the id
(`Atlas_EquipIcon_MC/2006`), and no equip field holds the name's stringId (verified exhaustively:
0/97 rows contain any item-name stringId). The loc name-ids are MLBB item-series ids, not ordered by
MCGG equip id, so they don't map positionally either. So names exist in data but cannot be attached
to specific stat rows from this dump.

The named catalogs therefore use the in-game Equipment UI, captured per tab (S6, 2026-06-28):
`storage/magic-chess-gogo/equipment_samples/{regular,magic_crystal,synergy_exclusive,
commander_exclusive,special}/*.png`, plus loose detail shots `inspire.png`, `demon_hunter_sword.png`,
`glowing_wand.png`. The UI is preferred over the raw loc band because it gives the **current** per-tab
grouping (the loc band includes stale items not in the live tabs). Effects are transcribed from the
right-side detail panel; only items whose panel was on screen have effect text (the rest are
name-confirmed, effect pending a per-item capture).

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
= **flat integers** (ChangePara 1). Pattern-inferred: `1021`/`1031` = physical/magic damage %, `1001`
HP %, `1042` ATK Speed %. Attribute *names* are localized hash lookups with no in-table stringId, so
stats are recorded by attrId. `m_Slot` is `[1,2,3]` on almost every item (id 9999 sits in slot 4);
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
