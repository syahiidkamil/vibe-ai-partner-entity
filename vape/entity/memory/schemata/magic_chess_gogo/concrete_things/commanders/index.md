<!-- Authored from first-party live-client localization. Names, titles, skill names and skill
descriptions are verbatim by stringId (not transcribed); see the provenance JSON and
work_dir/saori/mcgg/gen_commanders.py. Regenerate on a season/balance patch. -->

# Commanders (MCGG S6): the player-avatar system and roster

The Commander is the player. This folder models the commander layer: the system (who you are
on the board), the resolved commander kits (the passives that define a strategy), and the full
roster of commander characters and their skin titles. The objective game world is [[schemata]];
this is its commander rung. Hero units live in [[heroes/index]], team bonuses in [[synergies]],
run-shaping powers in [[gogo_cards/index]]. Governed by [[disclaimer]].

Provenance: live client v1.2.88.302.2 (BlueStacks), EN localization, parsed with
`work_dir/saori/mcgg/mulong_parse.py`. Structured dump:
`storage/magic-chess-gogo/game-client-from-bluestack/parsed/strategy/commanders.json`.

## The commander system (you ARE the commander)

- **Player = Commander.** Each of the 8 players in a lobby is one Commander, an avatar that
  builds and fields a team but never acts during combat (the build is the move). See
  [[game_rules_and_round_flow]] and [[schemata]].
- **Commander HP.** Each Commander has its own HP; a lost PvP round drains it, 0 HP eliminates
  you, last alive wins. Many commander skills restore or protect HP (on a win, on defeating
  another Commander, or a flat damage cut for a round).
- **Commander Level.** Raised with Gold; gates Hero Capacity (board size). Several skills lower
  the Gold cap to level, or cut shop-refresh cost (the economy lever lives partly here).
- **Stars and skins.** A Commander has a star level (up to 3 per the live UI); star level
  scales its skills (Golden Legacy scales its bonus by stage/star). Skins are cosmetic titles
  only (the title band below); many skins are MLBB-hero crossovers.
- **Commander DMG scales with stage.** The Commander deals damage that grows as stages progress
  (per the live UI; supported by post-win commander-damage and gather-power skills). Exact
  scaling not deterministically extracted (see [[disclaimer]] and the gaps note below).
- **Skills define the strategy.** Each Commander carries 2-3 signature run-level skills, tagged
  `[C7Passive]` / `[C7Active]` (commander passive/active) or `[C4Active]` (an active ability).
  These are not combat skills; they reshape gold, HP, the shop, synergies, or the rounds.
- **Exclusive Go Go cards.** Some commanders unlock commander-exclusive Go Go cards (Johnson and
  Lunox per the live UI). Cross-link: [[gogo_cards/index]].
- **Interest.** Most commanders earn interest on saved Gold (the genre default,
  [[equipment_and_economy]]); a few forgo it by design (Lancelot). `MCCommanderInterestNum`
  holds the interest brackets.

Data tables (numerics, structurally present): `CommanderSkillSelectConfig.bin`,
`MCCommanderSkillValue.bin`, `MCCommanderInterestNum.bin`, `IndividualCommanderLevel.bin`,
`CommanderRisingStar_MC2.bin`, `IndividualCommandel.bin`.

## What is resolved vs open

- **Resolved kits (10):** name + verbatim passive/active text + the strategy each enables, for
  the commanders the skill text explicitly names. Full detail: [[resolved_commanders]].
- **Roster (21 characters):** every commander character and its skin titles, first-party from
  the title band. Plus the named commander skills whose owner is not resolvable from this dump.
  See [[roster_and_skins]].
- **Open gaps:** of the 21 roster characters, 10 have a resolved kit; the other 11 have
  names + titles but no kit isolatable from this dump (the localization is hash-keyed, so a
  skill cannot be joined to its commander by id, only by the text naming it). Exact `<Num>`
  skill values are present in the data tables but not deterministically keyable per skill
  (same soft spot as synergy/item value prose, [[disclaimer]]). Marked, never fabricated.

## Resolved commanders at a glance  (`Name (archetype): strategy`)

| Commander | Archetype | Strategy in one line |
|---|---|---|
| Lancelot | Economy / self-scaling | Drop interest, sink all Gold into upgrading Lancelot |
| Benny | Creep recruiter | Each PvE creep round recruits the enemy's strongest creep |
| Bersi | Resurrection | Outlast: revive dead heroes; Bersi himself revives once |
| Brown | Equipment denial + execute | Strip the enemy carry's gear; win-scaling execute (Smith) |
| Tharz | Anti-3-star stacking | No 3-stars; every extra 2-star copy enhances it (Devil's Might) |
| Austus | Shard/Totem value | Shards on wins/deaths fire a Totem for Gold and free heroes |
| Harper | Win-streak tank | Damage reduction + stacking win shields; block a full round |
| Dubi | Fluffy mines | Seed exploding Fluffy that stun rows/columns |
| Abe | Anti-commander aggro | Extra damage to enemy Commanders; enhanced follow-up |
| Johnson | Exclusive-unit summoner | Add Johnny/Katoom to shop; become a car; own Go Go cards |

Lancelot and Johnson are hero-commanders (the live UI shows the MLBB hero name); the title band
clusters their skins under roster characters Remy and Kaboom respectively. See
[[roster_and_skins]] for the full character list.
