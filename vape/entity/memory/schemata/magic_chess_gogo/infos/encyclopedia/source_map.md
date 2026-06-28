# Source Map: where the MCGG schema facts come from

Provenance and capture notes, kept here so the schema files stay essentials-only. All from the
live client **v1.2.88.302.2** (BlueStacks pull, 2026-06-27/28) unless noted.

## Encyclopedia (the rules tabs)

Each tab was drafted from the localization, then verified tab-by-tab against in-app screenshots
(`storage/magic-chess-gogo/encyclopedia/*.png`), the source of truth. Where the draft disagreed,
the screenshot won (this caught invented headings, a bogus 3-month-season claim, and a misplaced
Commander Skills section). Economy and stage numbers come from `MCClassicsBattleConfig_S6`.

## Synergies (names, effects, members)

Moved to [../synergies/source_map.md](../synergies/source_map.md): the names
resolution (incl. relId 8 = Swiftblade, not "Assassin"), the exact per-tier effects (from the
in-game Synergy Guide UI), the backend-fetch reason the numbers aren't in the dump, and the
Neobeasts ladder.

## Item display names

Item names exist in the localization (e.g. Demon Hunter Sword, Glowing Wand, Inspire) but cannot be
joined to item ids from the data (hash-keyed; the name string-ids appear in no decoded equip
table). Equipment names need in-game Equipment-tab screenshots to bind to items.

## Hero data

Per-star stats are generated exact from the datamined `dataset_s6.json` (v302.1, matches the live
v302.2). Skills are from the 52 in-game Hero-Details screenshots (the parsed skill names were
unreliable, e.g. real "Groundsplitter" not the parsed "Fission Wave"). Recommended equipment is
pending the Equipment-tab capture (same item-name wall as above).
