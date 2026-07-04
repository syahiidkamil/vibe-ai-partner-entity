<!-- Commander system + the S6 roster. Kits are first-party from the in-game Commander detail
panels (storage/magic-chess-gogo/commanders/*.png); skin lists from the localization title band.
Regenerate on a season/balance patch. -->

# Commanders (MCGG S6): the player-avatar system and roster

The Commander is the player. This folder models the commander layer: the system (who you are on
the board), the full **37 commander kits** with exact skill values ([[resolved_commanders]]), and
the provenance + character/skin titles ([[source_map]]). The objective game world is [[schemata]]; hero
units live in [[heroes/index]], team bonuses in [[synergies]], run-shaping powers in
[[gogo_cards/index]]. Governed by [[disclaimer]].

## The commander system (you ARE the commander)

- **Player = Commander.** Each player in a lobby is one Commander, an avatar that builds and
  fields a team but never acts during combat (the build is the move). See
  [[game_rules_and_round_flow]] and [[schemata]].
- **Commander HP.** Each Commander has its own HP; a lost PvP round drains it, 0 eliminates you,
  last alive wins. Several skills restore/protect HP (Nana, Cyclops, Harper-class survival).
- **Commander Level.** Raised with Gold; gates Hero Capacity (board size). Some skills gate on
  Capacity (Lylia at 8) or on Level (Vale's charges at 4/6/8/10).
- **Stars and skins.** A Commander has a star level (up to 3); the **second skill is the star-up**
  of the first (e.g. Aurora Frost Energy 2→3). Skins are cosmetic titles only; many are MLBB-hero
  crossovers — the S6 UI presents each commander under its MLBB hero name.
- **2 signature skills.** Tagged Passive/Active; they reshape gold, the shop, equipment, synergies,
  rewards, or combat — never normal combat skills. Full kits with exact values: [[resolved_commanders]].
- **Exclusive Go Go cards.** Some commanders unlock commander-exclusive Go Go cards
  ([[gogo_cards/index]]); Valir and Yu Zhong are Go Go / Commander-EXP specialists.
- **Interest.** Most commanders earn interest on saved Gold ([[equipment_and_economy]]); Lancelot
  forgoes it by design.

## The roster (37) — `Commander · title · archetype`

| Commander | Title | Archetype |
|---|---|---|
| Lancelot | Blade of Roses | Economy / self-scaling |
| Chou | Kung Fu Boy | Economy (Gold on win/loss) |
| Nana | Sweet Leonin | Economy / survival |
| Aamon | Duke of Shards | Copy (Mirror Devices) |
| Alice | Queen of Blood | Star-up without 3 copies |
| Dyrroth | Prince of the Abyss | Devour → higher-quality heroes |
| Harley | Mage Genius | Shop floods 5-Gold heroes |
| Lylia | Lovable Witch | Gain highest-cost deployed hero |
| Moskov | Spear of Quiescence | Enhance + duplicate a hero |
| Paquito | The Heavenly Fist | Boxing Gloves copy by cost |
| Popol and Kupa | Icefield Companions | Copy Trap (steal enemy heroes) |
| Vale | Windtalker | Synergy-targeted shop + free buys |
| Karina | Shadow Blade | Equipment: execute blades |
| Luo Yi | Mistveil Mage | Equipment: hero → Essence Core |
| Minotaur | Son of Minos | Equipment: enhance gear |
| Ruby | Little Red Hood | Equipment: Cloak + Scythe |
| Zilong | Spear of the Dragon | Equipment: Dragon Spear + traits |
| Gusion | Holy Blade | Synergy grant (Light Sigil) |
| Guinevere | Ms. Violet | Free heroes in shop |
| Lunox | Twilight Goddess | Synergy grant (Blessing) |
| Alucard | Demon Hunter | Reward engine (Altar) |
| Aurora | Maiden of the Glacier | Reward engine (Frost Energy) |
| Cyclops | Asta | Loot eliminated commanders |
| Diggie | Timekeeper | Reward engine (Alarm Chest) |
| Kalea | Surging Wave | Reward engine (dice / Trove) |
| Vexana | Shimmer of Hope | Extra Go Go Box picks |
| Valir | Son of Flames | Go Go cards + Commander EXP |
| Yu Zhong | Black Dragon | Upgrade Go Go cards |
| Angela | Bunnylove | Combat: shield an ally |
| Fanny | Blade Dancer | Combat: Hero Launcher shadows |
| Johnson | Wild Engine | Combat: Johnny units (own Go Go cards) |
| Kagura | Onmyouji Master | Combat: shield umbrella |
| Layla | Blue Specter | Combat: hologram lasers |
| Ling | Cyan Finch | Combat: Dueling Ring |
| Lukas | Beast of Light | Combat: statue shockwave |
| Miya | Greenwood Archer | Combat: coordinated arrows |
| Wanwan | Agile Tiger | Combat: low-HP burst |

Full kits with exact values: [[resolved_commanders]]. Provenance + character/skin titles: [[source_map]].
