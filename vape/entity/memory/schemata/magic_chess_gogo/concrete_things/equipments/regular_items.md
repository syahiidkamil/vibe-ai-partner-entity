<!-- GENERATED: stat rows + ids from storage/magic-chess-gogo/game-client-from-bluestack/parsed/strategy/equipment.json (built by work_dir/saori/mcgg/build_equipment.py from the live client v302.2). Stat rows are exact; prose is authored. Regenerate on a season patch. -->

# Regular Items (MCGG S6, origin 0)

The standard item pool: **23 distinct items** (Basic + Enhanced rows). These are the MLBB-derived equipment plus the Basic utility set. Stat rows are exact (by attrId; see [[index]] for the conversion and the names wall). Governed by [[disclaimer]].

## Named catalog (from localization, unkeyed to ids)

Display names present in the client but not keyable to the stat rows below. The Basic utility items resolve to effects from the in-game UI; the rest are the named MLBB items.

**Basic / utility band:** Inspire · Enhanced Inspire · Revitalize · Enhanced Revitalize · Purify · Enhanced Purify · Flicker · Blazing Hammer · Fluffy's Rage · Aegis · Enhanced Aegis · Retribution · Enhanced Retribution · Great Dragon Spear · Enhanced Great Dragon Spear · Essence Core · Enhanced Essence Core

**Regular named items (Go Go Box catalog, each has Basic + Enhanced):** Antique Cuirass · Berserker's Fury · Blade Armor · Blade of Despair · Brute Force Breastplate · Demon Hunter Sword · Dominance Ice · Enchanted Talisman · Feather of Heaven · Feline Blade · Glowing Wand · Golden Staff · Guardian Helmet · Haas' Claws · Holy Crystal · Ice Queen Wand · Oracle · Purple Buff · Sea Halberd · War Axe · Winter Crown

## Basic utility items (effects from the in-game UI)

The creep-round picks, simple and powerful. Effects per the UI; see [[equipment_and_economy]] for which round offers them.

- **Inspire** - Increase ATK Speed. Unique Passive - Inspire: provide 20/25/30/40% ATK Speed (rises with Stage). Enhanced adds Unique Passive - Swift: +20% ATK Speed.
- **Revitalize** - healing/sustain item (Enhanced variant exists). Effect text not yet captured from the UI; name confirmed first-party.
- **Purify** - cleanse/anti-CC. Effect text not yet captured; name confirmed.
- **Aegis** - shield. Effect text not yet captured; name confirmed.
- **Retribution** - jungle/economy (slow + extra gold on affected kills, per the keyword prose). Effect text not yet fully captured; name confirmed.

## Verified named item: Demon Hunter Sword (Physical, Tank Killer)

+10% ATK Speed; Unique Passive - **Engulf**: basic ATKs deal extra Physical DMG equal to 2% of the target's max HP. (Name + effect both confirmed first-party; see [[index]] for the stringIds.) Not yet keyed to a specific id row below.

## Stat rows (exact, by attrId)

`*` on a skill = an Enhanced-only extra Unique Passive (`812xx`). `cat` = origin code. Stat = `attrId:value` (EXC = exclusive slot). See [[index]] for attrId meanings.

| id | cat | tier | slots | Basic stats | Basic skills | Enh stats | Enh skills |
|---|---|---|---|---|---|---|---|
| 2006 | 0 | 2 | 123 | 1042:10% | 25003 | 1042:10% | 25003 |
| 2009 | 0 | 2 | 123 | 1042:15% | 25940 | 1042:15% | 25940 |
| 2013 | 0 | 2 | 123 | 1021:10%, 62:15% | 25060 | 1021:10%, 62:15% | 25060 |
| 2106 | 0 | 2 | 123 | 1031:15%, 1021:15% | 25950 | 1031:15%, 1021:15% | 25954 |
| 2108 | 0 | 2 | 123 | 1031:25%, EXC13:40% | - | 1031:25%, EXC13:40% | 81299* |
| 2113 | 0 | 2 | 123 | 1031:10%, 1021:10%, 1001:10% | 26020 | 1031:10%, 1021:10%, 1001:10% | 26020 |
| 2207 | 0 | 2 | 123 | 1062:50 | 25019 | 1062:50 | 25019, 81292* |
| 2302 | 0 | 2 | 123 | 1021:15%, EXC12:40% | 25056 | 1021:15%, EXC12:40% | 25056, 81271* |
| 2304 | 0 | 2 | 123 | 1001:15% | 25044 | 1001:15% | 25044, 81281* |
| 3003 | 0 | 2 | 123 | 1021:10%, 18:20%, 22:40% | - | 1021:10%, 18:20%, 22:40% | 81287* |
| 3008 | 0 | 2 | 123 | 1021:20% | 25850 | 1021:20% | 25850 |
| 3013 | 0 | 2 | 123 | 1021:20%, 18:15%, EXC92:15% | - | 1021:20%, 18:15%, EXC92:15% | 81311* |
| 3102 | 0 | 2 | 123 | 1031:15% | 25007 | 1031:15% | 25007 |
| 3104 | 0 | 2 | 123 | 1031:15%, 62:15% | 25080 | 1031:15%, 62:15% | 25080, 81283* |
| 3105 | 0 | 2 | 123 | 1031:20% | 26050 | 1031:20% | 26050 |
| 3110 | 0 | 2 | 123 | 1021:15%, 1031:15%, 1001:10% | 27999 | 1021:15%, 1031:15%, 1001:10% | 2027999 |
| 3203 | 0 | 2 | 123 | 1001:10%, 1180:10% | 25090 | 1001:10%, 1180:10% | 25090 |
| 3208 | 0 | 2 | 123 | 1062:20, 1072:20 | 28530 | 1062:20, 1072:20, 1001:20% | 28530 |
| 3211 | 0 | 2 | 123 | 1062:20, 1072:20 | 28130 | 1062:20, 1072:20 | 28135 |
| 3214 | 0 | 2 | 123 | 1072:50, 1001:10% | 28120 | 1072:50, 1001:10% | 28120 |
| 3997 | 0 | 2 | 123 | 1001:15% | 28510 | 1001:15% | 28510 |
| 3998 | 0 | 2 | 123 | 1021:10%, 1031:10% | 26060 | 1021:10%, 1031:10% | 26060, 81289* |
| 3999 | 0 | 2 | 1 | 1021:10%, 1031:10% | 28040 | 1021:10%, 1031:10% | 28041 |
