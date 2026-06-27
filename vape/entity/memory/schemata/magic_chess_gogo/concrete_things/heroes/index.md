<!-- GENERATED from storage/magic-chess-gogo/game-client/dataset_s6.json by work_dir/saori/mcgg/gen_heroes.py. Stats are exact; do not hand-edit. Regenerate on a season patch. -->
<!-- Active-skill lines added from the live client string table by work_dir/saori/mcgg/gen_skills.py (-> parsed/strategy/heroes_skills.json) + inject_skills.py. See "Active skills" below. -->

# Heroes (MCGG S6): the full roster, organized by domain

The complete S6 hero data, generated exact from Kamil's datamined `dataset_s6.json` (the flat client export, re-organized here by the domain's own axis: cost tier). Per-cost detail files carry every field including full per-star stat tables plus each hero's **active skill** (name + description); this index is the map. Governed by ../disclaimer.md (regenerate on a season patch).

## Cost distribution (shop heroes)

| Cost | Heroes | Detail |
|---|---|---|
| 1 | 8 | [cost_1.md](cost_1.md) |
| 2 | 11 | [cost_2.md](cost_2.md) |
| 3 | 12 | [cost_3.md](cost_3.md) |
| 4 | 12 | [cost_4.md](cost_4.md) |
| 5 | 9 | [cost_5.md](cost_5.md) |
| special | 2 | [special_units.md](special_units.md) |
| **total** | **54** | |

## Per-star mechanic

Each hero has 3 star tiers (the Dragon summon has 4). Merge 3 copies of a hero to raise its star (1->2->3); nine 1-stars make a 3-star. HP roughly 1.8x per step, so a 3-star is a large power spike. Every per-star stat block is in the cost files.

## Stat legend

HP, PhyAtk/MagAtk (physical/magic attack), PhyDef/MagDef, AtkSpd (attacks/sec), MoveSpd, Crit, DPS (the client's damage-per-second figure), EHP (effective HP vs the modeled defense), MP (mana to cast the skill). compCount/carryCount come from the client's recommended-comp data (how often a hero appears, and as a carry): the tier-list seed.

## Active skills

Each hero's `m_SkillList[0]` (the `[1,0]`-flagged entry) is its ACTIVE skill, the one auto-cast in
battle when mana fills. The active skill is shown in the cost files as an `**Active skill (...)**`
bullet under each hero. The skill is central to strategy: it is what the unit actually *does* when
the fight runs on its own.

Resolution and its honest limits:
- **Source.** Skill text is verbatim from the live client string table (`AllLanguageEN`, the full
  MLBB strings == `localization_en.json`). Each description names the hero as its subject
  ("Saber charges...", "Tigreal unleashes..."), so it is attributed by that subject, never invented.
- **Currency.** That table co-mingles strings across modes and seasons, so several versions of a
  hero's text co-exist. The current S6 active-skill catalog is the band ~2212515000-2212525000,
  confirmed by exact hits (Triple Sweep->Saber, Implosion->Tigreal, Fission Wave->Alucard); it is
  preferred. 41/52 picks come from that band; the other 11 fall back to the nearest clean version.
- **Coverage.** 52 of 54 heroes have a resolved active-skill description; the 2 summon/special units
  (Dragon, Claude (special)) are marked "skill text not resolved." Of the 52, 30 also resolve a
  skill NAME (= `loc[descId-1]` when it is a clean title); the rest are marked
  "(name not resolved)" but keep the description.
- **Numbers.** `Num1`, `Num2`, `Num1%` are the client's in-game scaling placeholders, not concrete
  values (the table ships the mechanic, not the per-star numbers). Treat skill text as the mechanic;
  verify exact numbers in-game. Full provenance (all candidates, string ids, band membership):
  `storage/.../game-client-from-bluestack/parsed/strategy/heroes_skills.json`.

## Roster at a glance  (`name (class / faction)`)

**Cost 1:** Alucard (Weapon Master (r4) / Heartbond (r52)) · Brody (Marksman (r5) / Neobeasts (r55)) · Cecilion (Mage (r6) / Emberlord (r50)) · Dyrroth (Bruiser (r1) / Kishin (r56)) · Eudora (Stargazer (r7) / Dragoncaller (r54)) · Minotaur (Defender (r3) / Astro Power (r53)) · Phoveus (Scavenger (r9) / Exorcist (r51)) · Silvanna (Dauntless (r2) / Mystic Meow (r58))

**Cost 2:** Angela (Scavenger (r9) / Kishin (r56)) · Balmond (Dauntless (r2) / Dragoncaller (r54)) · Belerick (Bruiser (r1) / Enchanted Tales (r57)) · Fanny (Phasewarper (r10) / Heartbond (r52)) · Gatotkaca (Bruiser (r1), Defender (r3) / Neobeasts (r55)) · Granger (Marksman (r5) / Exorcist (r51)) · Hanzo (Assassin (r8) / Emberlord (r50)) · Joy (Assassin (r8) / Northern Vale (r59)) · Lylia (Mage (r6) / Neobeasts (r55)) · Martis (Weapon Master (r4) / Astro Power (r53)) · Selena (Stargazer (r7) / Enchanted Tales (r57))

**Cost 3:** Clint (Phasewarper (r10) / Dragoncaller (r54)) · Franco (Dauntless (r2), Weapon Master (r4) / Kishin (r56)) · Fredrinn (Weapon Master (r4) / Neobeasts (r55)) · Helcurt (Assassin (r8) / Astro Power (r53)) · Hilda (Dauntless (r2) / Astro Power (r53)) · Julian (Mage (r6), Phasewarper (r10) / Mystic Meow (r58)) · Khufra (Defender (r3) / Heartbond (r52)) · Luo Yi (Stargazer (r7) / Northern Vale (r59)) · Masha (Bruiser (r1) / Emberlord (r50)) · Miya (Marksman (r5) / Heartbond (r52)) · Saber (Assassin (r8) / Exorcist (r51)) · Tigreal (Defender (r3) / Emberlord (r50))

**Cost 4:** Aurora (Stargazer (r7) / Astro Power (r53)) · Esmeralda (Dauntless (r2) / Heartbond (r52)) · Gusion (Assassin (r8) / Dragoncaller (r54)) · Irithel (Marksman (r5) / Emberlord (r50)) · Kagura (Mage (r6) / Exorcist (r51)) · Karrie (Marksman (r5) / Kishin (r56)) · Leomord (Weapon Master (r4) / Enchanted Tales (r57)) · Lunox (Stargazer (r7) / Kishin (r56)) · Pharsa (Stargazer (r7) / Neobeasts (r55)) · Terizla (Defender (r3) / Dragoncaller (r54)) · Vexana (Mage (r6) / Enchanted Tales (r57)) · Yu Zhong (Bruiser (r1) / Exorcist (r51))

**Cost 5:** Alpha (Weapon Master (r4) / Emberlord (r50)) · Badang (Bruiser (r1) / Dragoncaller (r54)) · Bane (Defender (r3) / Northern Vale (r59)) · Claude (Scavenger (r9) / Heartbond (r52)) · Lancelot (Phasewarper (r10) / Kishin (r56)) · Lesley (Marksman (r5) / Mystic Meow (r58)) · Ling (Assassin (r8) / Neobeasts (r55)) · Odette (Mage (r6) / Astro Power (r53)) · Ruby (Dauntless (r2) / Exorcist (r51))

**Special:** Dragon (id 179) · Claude (special) (id 180)
