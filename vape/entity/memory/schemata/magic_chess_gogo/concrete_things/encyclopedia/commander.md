# Encyclopedia: Commander

Transcribed from the in-app Encyclopedia screenshots (commander_01/02.png), 2026-06-28, live
client v1.2.88.302.2. The screenshots are the source of truth; this captures the Commander tab
in full. The tab has three sections, in this order: EXP, Upgrade Cost, Commander DMG.

## EXP

> 1. At the start of each round, the Commander will obtain 2 EXP.
> 2. Players can use Gold to exchange for the equivalent amount of EXP.
> 3. The Commander reaches the next level by gaining enough EXP.
> 4. At a higher Commander level, you can deploy more Heroes to battle.
> 5. The chance to get high-quality Heroes from the Shop also increases with Commander Level.

So Commander level does two things beyond unlocking the next level: it raises how many Heroes
deploy to battle, and it improves the Shop's odds of higher-quality Heroes. The exact
level-to-capacity and level-to-shop-odds numbers are not shown on this tab.

## Upgrade Cost

Gold required to advance the Commander one level (shown as current level ">>" next level):

| Level     | 3 >> 4 | 4 >> 5 | 5 >> 6 | 6 >> 7 | 7 >> 8 | 8 >> 9 | 9 >> 10 (Max) |
|-----------|--------|--------|--------|--------|--------|--------|---------------|
| Gold req. | 3      | 8      | 20     | 32     | 40     | 54     | 74            |

Level 10 is the Max. The table starts at level 3 >> 4, so the cost of the first two upgrades
(1 >> 2 and 2 >> 3) is not shown on this tab.

## Commander DMG

> Commander DMG: After each round, the winning Commander deals a certain amount of DMG to the
> losing Commander. DMG varies by round and the number of surviving units.
> Commander DMG = Round Base DMG + Total Star Levels of Surviving Units

Round Base DMG by round range (round labels as shown in-app, e.g. III-4), start ">>" end:

| Rounds         | Base DMG |
|----------------|----------|
| I-2 >> I-4     | 3        |
| II-1 >> II-4   | 5        |
| II-5 >> II-6   | 6        |
| III-1 >> III-3 | 7        |
| III-4 >> III-6 | 11       |
| IV-1 >> IV-3   | 13       |
| IV-4 >> IV-6   | 14       |
| V-1 >> V-5     | 15       |

> Special Case: Certain surviving non-Hero units increase Commander DMG by 1. If the round ends
> in a draw, both sides deal DMG to each other.

So a lost PvP round costs HP equal to: the round's base DMG, plus the sum of the winner's
surviving units' star levels, plus 1 for each surviving non-Hero unit. Base DMG climbs from 3 in
stage I to a flat 15 by stage V, so a clean late-game board is a big HP swing per loss. The table
starts at I-2, so the first round (I-1) deals no Commander DMG.

The roster of Commanders and their skills lives at [[commanders/index]].
