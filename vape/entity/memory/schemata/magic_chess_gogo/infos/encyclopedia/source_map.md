# Source Map: where the MCGG schema facts come from

Provenance and capture notes, kept here so the schema files stay essentials-only. All from the
live client **v1.2.88.302.2** (BlueStacks pull, 2026-06-27/28) unless noted.

## Encyclopedia (the rules tabs)

Each tab was drafted from the localization, then verified tab-by-tab against in-app screenshots
(`storage/magic-chess-gogo/encyclopedia/*.png`), the source of truth. Where the draft disagreed,
the screenshot won (this caught invented headings, a bogus 3-month-season claim, and a misplaced
Commander Skills section). Economy and stage numbers come from `MCClassicsBattleConfig_S6`.

## Synergy names (all 20, first-party)

Resolved three independent ways: (1) the faction localization band `loc[2012764216 + (relId-50)]`
for r50-r59, classes from `loc[493757747+]`; (2) each synergy's `FX_Fetter_<pinyin>` matches its
name (r5 SheShou = Marksman, r51 QuMoShi = Exorcist, r54 ZhenLong = Dragoncaller); (3) `m_Sort`
membership. r8 (Assassin) and r10 (Phasewarper) had stale bands, resolved via FX pinyin plus
roster. This corrected the datamine `plan.md`, which had 51/54 swapped: **relId 51 = Exorcist**,
**relId 54 = Dragoncaller** (the dragon faction; it summons the Dragon, hero id 179).

Internal relId map (for cross-reference): class 1-10 = Bruiser, Dauntless, Defender, Weapon Master,
Marksman, Mage, Stargazer, Assassin, Scavenger, Phasewarper. faction 50-59 = Emberlord, Exorcist,
Heartbond, Astro Power, Dragoncaller, Neobeasts, Kishin, Enchanted Tales, Mystic Meow, Northern
Vale.

## Synergy effects

Effect SUMMARIES in [synergies](../synergies.md) are extracted from the parsed localization:
- **Faction summaries** map deterministically by a localization band: stringIds 1280695776-785 =
  relId 50-59 in order (776 = Emberlord, 779 = Astro Power, 784 = Mystic Meow, 785 = Northern Vale).
- **Class summaries** come from each class's self-naming effect strings. Scavenger is the exception:
  its strings are cosmetic/mission text, so its effect is described from its known economy role.

What the localization does NOT give is the displayed NUMBERS (they are `[Num]` placeholders). The
per-tier values are **not in the client data at all**: the client carries only the effect *template*
(a value-formula token like `[2|4500200|FPara1|%|N*0.1]`) and fetches the actual number from the
**backend on demand** at runtime. That is the real reason no static parse finds them, and it was
checked hard (2026-06-28, four ways): the token's composite id is not a flat MCEffect row key (its
sibling tier ids are absent, and the known values appear nowhere near it in any int/float encoding);
the 64-column ver-1 MCEffect layout does not converge to a clean parse from data alone (a
cross-file-EOF backtracking solver fails); and the datamine's own `dataset_s6.json` leaves every
synergy value templated for the same reason. So per-tier numbers come from the in-game Synergy Guide
UI. Emberlord and Astro Power are filled exact that way; the rest carry the mechanic with numbers
pending. The tier structure (activation `need`, `skillId`, `dps`, value-formula tokens) and the DSL
spec live in `work_dir/saori/mcgg/FORMULA_DSL.md` and `parsed/strategy/resolved_effects.json`.

## Item display names

Item names exist in the localization (e.g. Demon Hunter Sword, Glowing Wand, Inspire) but cannot be
joined to item ids from the data (hash-keyed; the name string-ids appear in no decoded equip
table). Equipment names need in-game Equipment-tab screenshots to bind to items.

## Synergy Guide capture caveat

The three `synergy_guide_*.png` are one section (Neobeasts Point Rewards) at three scroll positions;
the overlap resolves every line. The 999 band lists three reward lines with no explicit "or"/"all"
connector in the UI, so whether they are alternatives or combined is not stated; transcribed as-is.

## Hero data

Per-star stats are generated exact from the datamined `dataset_s6.json` (v302.1, matches the live
v302.2). Skills are from the 52 in-game Hero-Details screenshots (the parsed skill names were
unreliable, e.g. real "Groundsplitter" not the parsed "Fission Wave"). Recommended equipment is
pending the Equipment-tab capture (same item-name wall as above).
