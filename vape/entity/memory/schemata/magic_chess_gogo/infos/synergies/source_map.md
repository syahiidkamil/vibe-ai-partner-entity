# Source Map: where the synergy facts come from

Provenance for [synergies.md](synergies.md), kept here so the synergy file stays
essentials-only. All from the live client **v1.2.88.302.2** (BlueStacks pull) plus the in-game
Synergy Guide UI, unless noted.

## Effects and per-tier numbers (the exact values)

Every effect summary and per-tier number in `synergies.md` is transcribed from the in-game
**Synergy Guide** panels, captured 2026-06-28, one screenshot per synergy:
- Class: `storage/magic-chess-gogo/synergy_role/*.png`
- Faction: `storage/magic-chess-gogo/synergy_faction/*.png`

The UI is the ground truth. This pass corrected several earlier localization-derived guesses, e.g.
Marksman is an ATK-Speed buff (not "Physical ATK + slow"), Weapon Master adds Physical ATK (no
"heal on kills"), and the relId-8 class is **Swiftblade**, a Hybrid-Penetration buff (see Names).

**Why these numbers are not in the data dump:** the client carries only the effect *template* (a
value-formula token like `[2|4500200|FPara1|%|N*0.1]`) and fetches the actual number from the
**backend on demand** at runtime (confirmed 2026-06-28). That was checked hard four ways: the
token's composite id is not a flat MCEffect row key (sibling tier ids absent, known values nowhere
near it in any int/float encoding); the 64-column ver-1 MCEffect layout does not converge to a clean
parse from data alone (a cross-file-EOF backtracking solver fails); and the datamine's own
`dataset_s6.json` leaves every synergy value templated. So the only readout is the Synergy Guide UI,
which is what `synergies.md` now uses. The tier structure (activation `need`, `skillId`, `dps`,
value-formula tokens) and the DSL spec live in `work_dir/saori/mcgg/FORMULA_DSL.md` and
`parsed/strategy/resolved_effects.json`.

## Names (all 20, first-party)

Resolved three independent ways: (1) the faction localization band `loc[2012764216 + (relId-50)]`
for r50-r59, classes from `loc[493757747+]`; (2) each synergy's `FX_Fetter_<pinyin>` matches its
name (r5 SheShou = Marksman, r51 QuMoShi = Exorcist, r54 ZhenLong = Dragoncaller); (3) `m_Sort`
membership. This corrected the datamine `plan.md`, which had 51/54 swapped: **relId 51 = Exorcist**,
**relId 54 = Dragoncaller** (the dragon faction; it summons the Dragon, hero id 179).

**relId 8 displays in-game as "Swiftblade", not "Assassin".** The datamine resolved r8 via an
FX-pinyin + roster heuristic (a stale loc band) and labelled it "Assassin"; the Synergy Guide UI
header is the authority, so the schema uses **Swiftblade** (its members are unchanged: Saber,
Helcurt, Gusion, Hanzo, Ling, Joy). The icon file is `synergy_icons/swiftblade.png`.

Internal relId map (for cross-reference): class 1-10 = Bruiser, Dauntless, Defender, Weapon Master,
Marksman, Mage, Stargazer, **Swiftblade**, Scavenger, Phasewarper. faction 50-59 = Emberlord,
Exorcist, Heartbond, Astro Power, Dragoncaller, Neobeasts, Kishin, Enchanted Tales, Mystic Meow,
Northern Vale.

## Members

Member rosters per synergy are generated exact from the datamined `dataset_s6.json` (v302.1, matches
the live v302.2 client), the same source as the hero stats.

## Neobeasts point-reward ladder

The detailed point-threshold reward ladder (the 300 / 700 progress rewards and the 999 band) is in
[../encyclopedia/synergy_guide.md](../encyclopedia/synergy_guide.md), transcribed from three
`synergy_guide_*.png` scroll positions (one section, three scrolls; the overlap resolves every line).
