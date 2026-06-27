<!-- Roster characters + skin titles extracted programmatically from the localization title band
(637068560-637070700) by gap-clustering; skill pool is verbatim by stringId. Provenance:
storage/.../parsed/strategy/commanders.json, work_dir/saori/mcgg/gen_commanders.py. -->

# Commander roster, skin titles, and the unattributed skill pool (MCGG S6)

The full set of commander characters and their cosmetic skin titles, first-party from the title
band, plus the named commander skills whose owner is not resolvable from this dump. Resolved
kits and the system: [[index]], [[resolved_commanders]].

## The 21 commander characters (`character: skin titles`)

Original GoGo characters. A skin is cosmetic (it does not change the kit); many skins are
MLBB-hero crossovers (so a commander can appear in the UI under a hero name, e.g. Remy as the
Lancelot skins, Kaboom as the car/Johnson). Bold = a resolved kit exists ([[resolved_commanders]]).

- **Remy** (-> Lancelot): Blade of Roses, Sword-expert Remy, Peter Who, Swordmaster, Floral
  Knight, Honor Guard, Blade of Fall, Masked Knight
- **Benny**: Icefield Companions, Stealthy Hunter, Jailbreaker Benny, Jungle Reporter, Dustland
  Pals
- **Bersi**: Little Red Hood, Nether Bersi, Mystic Puppet, Shadow Reaper, Verdant Huntress,
  Dawnlight Nexus
- **Brown** (skin Grandmaster Smith): Son of Minos, Freedom Bringer, Bovine Enforcer, Grandmaster
  Smith, Shadow Guardian, Orbiter, Dreadnought
- **Tharz**: Little Witch, Poltergeist, Astro Probe, Mischievous Ghost, Devious Imp, Lovable
  Witch, Future Star, School Idol
- **Austus**: Duke of Shards, Hunter Griffin, Sky Hunter, Light's Defender, Night's Edge, Noble
  Crest, Cyber Assassin
- **Harper**: Demon Hunter, Harper O'Lantern, Chevalier Harper, Lightning Envoy, Shadow Hunter
- **Dubi**: Surging Wave, Rouge Whisper, Tranquil Spirit, Crimson Serpent
- **Abe**: Kungfu Expert, Kungfu Master, Badass Roller, Practitioner Abe, Akai
- **Kaboom** (-> Johnson): Wild Engine, Off-road Kaboom, Excavator Kaboom, RC Roadster, Swifting
  Heart, Death Chariot, Jeepney Racer
- Ragnar: Frozen Warrior, Axe-expert Ragnar, Baking-master Ragnar, Viking Ragnar, Miner Ragnar,
  Axeman Ragnar, Fierce Warrior
- Eva: Mysterious Deer, Jingle Deer, Frost Princess, Violet Eva, Water Priestess
- Eggie: Naughty Eggie, Deteggtive, Scavenger Eggie, Aerial Scout, Timekeeper, Sage of Time,
  Constellation
- Mavis: Queen of Blood, Night Princess, Jade Mavis, Wings of Eclipse, Nocturnal Core, Divine Owl
- Buss: Mage Genius, Magic Meow, Astrologer Buss, Gentleman Buss, Prodigy Mage, Naughty Joker,
  Dreaming Koi
- Pao: Black Dragon, Sky Roamer, Molten Breath, Full Armor Pao, Cosmic Dragon, Dragon's Shade,
  Emerald Dragon, Exorcist Yu Zhong
- Yuki: Yin-yang Geomancer, Onmyoji Yuki, Fate Reader Yuki, Ice Mage Yuki, Gold Alchemist, Veiled
  Geomancer, Siren Priestess, Yin-yang Mage
- Connie: Shimmer of Hope, Tender Fluff, Strawberry Cone, Jovial Conductor, Wonderland Guide,
  Glimmer of Verdancy
- Saki: Frangipani Saki, Lotus Pixie, Festival Flutter, Onmyouji Master, Onmyouji Spring, Rainy
  Walk, Exorcist Kagura
- Rya: Twilight Goddess, Daffodil Rya, Divine Goddess, Springtime Blush, Spirit Sprout, Fate
  Goddess, Ash Blossom, Dawn Revelation
- Asta: Starsoul Magician, Clover Charm, Cosmic Starseer, Magic Apprentice, Silvermoon Magician,
  Super Adventurer

The 11 non-bold characters (Ragnar, Eva, Eggie, Mavis, Buss, Pao, Yuki, Connie, Saki, Rya, Asta)
have first-party names and titles but no skill kit isolatable from this dump. The hero-commander
**Lunox** is also named by the live UI (with an exclusive Go Go card, [[gogo_cards/index]]) but is
not in this title band and her kit is not isolated here. Marked open, not fabricated.

## Unattributed commander skills (named, owner not resolved)

Verbatim from the localization; the commander cannot be joined to these from the dump (hash-keyed
text, no in-table id). Grouped by what they do.

**Shared economy / utility (likely a selectable pool):**
- **Economize** (Passive): "Reduces the Gold cap required for upgrading Commander Level by
  `<%Num1>`."
- **Surging Morale** (Passive): win-streak reduces Gold cost of Commander upgrades.
- **Waste Not** (Passive): reduces the Gold cost of the first refresh each round.
- **Boon to the Weak** (Passive): free shop refreshes next round if you lose with little damage.
- **Midas Touch!** ([C4Active]): free shop refreshes that always roll the highest-cost heroes.
- **Alarm Chest**: unlocks at a Commander Level; grants Equipment and Magic Crystal loot chests.

**Sacrifice / charm / gather-power (one commander, name unresolved; described with "she/her"):**
- **Charming** ([C4Active]): grant a hero a Charm that makes adjacent allies sacrifice HP/ATK to
  empower it. Plus a sacrifice-mana active and a gather-power passive (heroes feed the Commander's
  damage to the strongest enemy).

**Synergy manipulation (name unresolved):**
- Stun all enemies holding Synergy Magic Crystals at round start; grant a hero a random Synergy
  Magic Crystal; grant a hero a Blessing (+1 to a Role or Faction Synergy). See [[synergies]].

**Scavenger / inherit-on-elimination (name unresolved; plausibly Eggie's "Scavenger" skin, not
confirmed):**
- **Astral Blessing - Gold / Hero / Equipment**: when a player is eliminated, gain Gold by their
  lineup value, gain heroes at their star level, and inherit pieces of their equipment.

**Traps (band-adjacent to Benny, attribution soft):**
- **Frost Trap** (Passive): a Frost Trap on the center tile freezes enemies who step on it.
- **Copy Trap**: a movable trap that yields a 1-star copy of an enemy hero who steps in it.
