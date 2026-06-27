# Encyclopedia: Commander (Level & EXP, Skills, Commander DMG)

Verbatim, in-app Encyclopedia > **Commander** tab, plus the first-party Commander-DMG model.

## Level & EXP (id `3003307285`)
> 1. At the start of each round, the Commander will obtain 2 EXP.
> 2. Players can use Gold to exchange for the equivalent amount of EXP.
> 3. The Commander reaches the next level by gaining enough EXP.
> 4. At a higher Commander level, you can deploy more Heroes to battle.
> 5. The chance to get high-quality Heroes from the Shop also increases with Commander Level.

Level gates **Hero Capacity** (board size) and shifts the shop's per-tier appearance odds. The
exact level->capacity and level->tier-odds tables are data-driven and not in the localization
prose (the shop-probability grid is a numeric table); treat both as **unknown** until pulled clean.

## Commander Skills (id `3003307286`)
> 1. Each Commander has 3 unique skills.
> 2. The first skill will be unlocked when obtaining the Commander. The other 2 skills can be
>    unlocked by using the Commander to play more battles.
> 3. These 2 skills can also be unlocked by purchasing the skin of the Commander.

The Commander roster and skills: [[commanders/index]].

## Commander DMG (the player-vs-player damage model)
First-party, ids `2912711205` / `2912711204` / `2912711203`:

> Commander DMG: After each round, the winning Commander deals a certain amount of DMG to the
> losing Commander. DMG varies by round and the number of surviving units.
> **Commander DMG = Round Base DMG + Total Star Levels of Surviving Units**

> Special Case: Certain surviving non-Hero units increase Commander DMG by **1**. If the round ends
> in a draw, **both sides deal DMG to each other**.

So a lost PvP round costs HP equal to: the round's base DMG, plus the sum of the winner's surviving
units' star levels, plus 1 per surviving non-Hero (summoned) unit.

**Round Base DMG** (first-party, `MCClassicsBattleConfig_S6.txt` `<SRoundExtraDamage>`):

| Rounds | Base DMG | Stage |
|--------|----------|-------|
| 2-4    | 3        | I     |
| 5-8    | 5        | II    |
| 9-10   | 6        | II    |
| 11-13  | 7        | III   |
| 14-16  | 11       | III   |
| 17-19  | 13       | IV    |
| 20-22  | 14       | IV    |
| 23-27+ | 15       | IV    |

(Round 1 has no entry. Values are flat at 15 from round 23 onward. This is why a clean board late
ends games fast: base 15 + a full late-game board of 3-stars is a large HP swing each loss.)

Note: a separate **Arena** side-mode uses a flat **-25 HP per loss** instead of this scaling
(id `2912711204`); see [[season_information]].
