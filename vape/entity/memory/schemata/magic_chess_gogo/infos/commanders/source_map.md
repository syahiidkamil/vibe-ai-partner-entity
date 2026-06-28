<!-- Authored from first-party in-game Commander detail panels (S6), captured at
storage/magic-chess-gogo/commanders/*.png. Names, titles, skill names and exact values are
verbatim from the panels (Basic + the second/upgrade skill). The earlier localization-only version
resolved 10 kits with templated <Num>; this is the full 37 with real numbers. -->

# Source Map: where the commander facts come from

Provenance + the non-essential catalog for [index](index.md) and
[resolved_commanders](resolved_commanders.md), kept here so those stay essentials-only. Two
sources: the in-game Commander detail panels (kits + exact skill values) and the EN localization
(names, titles, skin bands, the legacy skill pool). Governed by [[disclaimer]].

## Provenance
- **Kits (essential):** first-party from the 37 Commander detail panels (S6),
  `storage/magic-chess-gogo/commanders/*.png` — names, titles, skill names, and exact values
  transcribed verbatim. This replaced the earlier localization-only pass (10 templated kits).
- **Skin titles + legacy pool (below):** localization title band `637068560-637070700`,
  gap-clustered; structured dump `parsed/strategy/commanders.json`, gen `gen_commanders.py`.
- **Numeric tables (structurally present):** `CommanderSkillSelectConfig.bin`,
  `MCCommanderSkillValue.bin`, `MCCommanderInterestNum.bin`, `IndividualCommanderLevel.bin`,
  `CommanderRisingStar_MC2.bin` — the exact `<Num>` fills are the panels' job, not these.

## MLBB name ↔ original-GoGo character
The S6 UI presents each commander under an MLBB-hero skin; the underlying GoGo character is the
skin-band owner. Map by matching skin title — e.g. **Remy**→Lancelot, **Bersi**→Ruby,
**Saki**→Kagura, **Asta**→Cyclops, **Kaboom**→Johnson, **Mavis**→Alice, **Eggie**→Diggie,
**Connie**→Vexana, **Rya**→Lunox, **Pao**→Yu Zhong.

## Skin-title catalog (cosmetic — does not change the kit)
Original GoGo characters and their skin titles, first-party from the title band:
- **Remy** (→ Lancelot): Blade of Roses, Sword-expert Remy, Peter Who, Swordmaster, Floral Knight,
  Honor Guard, Blade of Fall, Masked Knight
- **Benny**: Icefield Companions, Stealthy Hunter, Jailbreaker Benny, Jungle Reporter, Dustland Pals
- **Bersi**: Little Red Hood, Nether Bersi, Mystic Puppet, Shadow Reaper, Verdant Huntress,
  Dawnlight Nexus
- **Brown**: Son of Minos, Freedom Bringer, Bovine Enforcer, Grandmaster Smith, Shadow Guardian,
  Orbiter, Dreadnought
- **Tharz**: Little Witch, Poltergeist, Astro Probe, Mischievous Ghost, Devious Imp, Lovable Witch,
  Future Star, School Idol
- **Austus**: Duke of Shards, Hunter Griffin, Sky Hunter, Light's Defender, Night's Edge, Noble
  Crest, Cyber Assassin
- **Harper**: Demon Hunter, Harper O'Lantern, Chevalier Harper, Lightning Envoy, Shadow Hunter
- **Dubi**: Surging Wave, Rouge Whisper, Tranquil Spirit, Crimson Serpent
- **Abe**: Kungfu Expert, Kungfu Master, Badass Roller, Practitioner Abe, Akai
- **Kaboom** (→ Johnson): Wild Engine, Off-road Kaboom, Excavator Kaboom, RC Roadster, Swifting
  Heart, Death Chariot, Jeepney Racer
- **Ragnar**: Frozen Warrior, Axe-expert Ragnar, Baking-master Ragnar, Viking Ragnar, Miner Ragnar,
  Axeman Ragnar, Fierce Warrior
- **Eva**: Mysterious Deer, Jingle Deer, Frost Princess, Violet Eva, Water Priestess
- **Eggie**: Naughty Eggie, Deteggtive, Scavenger Eggie, Aerial Scout, Timekeeper, Sage of Time,
  Constellation
- **Mavis**: Queen of Blood, Night Princess, Jade Mavis, Wings of Eclipse, Nocturnal Core, Divine Owl
- **Buss**: Mage Genius, Magic Meow, Astrologer Buss, Gentleman Buss, Prodigy Mage, Naughty Joker,
  Dreaming Koi
- **Pao**: Black Dragon, Sky Roamer, Molten Breath, Full Armor Pao, Cosmic Dragon, Dragon's Shade,
  Emerald Dragon, Exorcist Yu Zhong
- **Yuki**: Yin-yang Geomancer, Onmyoji Yuki, Fate Reader Yuki, Ice Mage Yuki, Gold Alchemist,
  Veiled Geomancer, Siren Priestess, Yin-yang Mage
- **Connie**: Shimmer of Hope, Tender Fluff, Strawberry Cone, Jovial Conductor, Wonderland Guide,
  Glimmer of Verdancy
- **Saki**: Frangipani Saki, Lotus Pixie, Festival Flutter, Onmyouji Master, Onmyouji Spring, Rainy
  Walk, Exorcist Kagura
- **Rya**: Twilight Goddess, Daffodil Rya, Divine Goddess, Springtime Blush, Spirit Sprout, Fate
  Goddess, Ash Blossom, Dawn Revelation
- **Asta**: Starsoul Magician, Clover Charm, Cosmic Starseer, Magic Apprentice, Silvermoon Magician,
  Super Adventurer

## Legacy localization skill pool
Harvested verbatim before the panels were captured; several now map to a resolved commander
(**Alarm Chest** → Diggie, **Copy Trap** → Popol and Kupa, **Astral Blessing** → Cyclops). Kept as
cross-reference; where it conflicts with a panel, the panel ([[resolved_commanders]]) wins.
- **Economy/utility pool:** Economize (-`<%Num1>` Level Gold cap), Surging Morale (win-streak cuts
  upgrade cost), Waste Not (cheaper first refresh), Boon to the Weak (free refreshes after a small
  loss), Midas Touch! (free high-cost refreshes), Alarm Chest (loot chests).
- **Charm/sacrifice (owner unresolved):** Charming — a Charm makes adjacent allies sacrifice HP/ATK
  to empower a hero; plus sacrifice-mana and gather-power.
- **Synergy manipulation:** stun crystal-holders at round start; grant a random Synergy Magic
  Crystal; grant a Blessing (+1 Role/Faction synergy). See [[synergies]].
- **Inherit-on-elimination:** Astral Blessing — Gold / Heroes / Equipment from an eliminated player
  (now Cyclops, [[resolved_commanders]]).
- **Traps:** Frost Trap (freeze on the center tile); Copy Trap (1-star copy of an enemy who steps in).
