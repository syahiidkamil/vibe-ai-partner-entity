# Encyclopedia: Round (Stage, Battle Round, Battle Complete, Creep Round)

Transcribed from the in-app Encyclopedia screenshots (round_01/02/03.png), 2026-06-28, live
client v1.2.88.302.2.

In-app Encyclopedia > **Round** tab and its sub-panels. round_01 and round_02 are the Round tab.
(round_03 is actually the **Hero** tab's shop draw-rate table; it lives in [[hero]] where it
belongs.) Lines marked "first-party config" come from the datamined config, not the
screenshots; everything in blockquotes is the screenshot text.

## Battle Stage (id `3003306607`)
> 1. A Magic Chess match consists of **four** stages (I to IV).
> 2. Each stage contains several rounds. At the end of a stage, there is a Go Go Box round that
>    provides supplies for battle.
> 3. Advancing to a new stage grants **increased basic rewards and higher Commander DMG**.
> 4. Stage IV is the final stage, where higher Commander DMG allows players to eliminate each
>    other faster. Finalize your lineup beforehand to secure victory!

**Stage->round map** (first-party config, `MCClassicsBattleConfig_S6.txt` `<SMCRoundRange>`):

| Stage | Rounds |
|------|--------|
| I    | 1-4    |
| II   | 5-10   |
| III  | 11-16  |
| IV   | 17-99 (final, open-ended) |

## Battle Round (id `3003307280`)
> 1. At the start of each round, the Shop **refreshes automatically**, and the Commander gains
>    **2 EXP**.
> 2. Each round consists of a Preparation phase and a Battle phase. **Battle Acceleration begins
>    in the last 10s** of the Battle phase.
> 3. During Battle Acceleration, all units gain **massive Resilience, ATK Speed, Hybrid ATK, and
>    extra DMG** every second, while **Healing and Shield Effects are significantly reduced**.
> 4. At the end of each round, players receive **Basic Rewards**, **Interest**, and **Win/Lose
>    Streak Rewards**.

(First-party config: prep-phase timer ~25-30s per `iPrepareTime`; Battle Acceleration is the
last 10s overtime that forces a result.)

## Battle Complete (id `3003307281`)
> 1. Upon a successful defense, you immediately gain **1 Gold**.
> 2. Your Commander deals damage to the enemy Commander based on the number of surviving units,
>    their **Star Levels**, and the current **Round**. When the **Nature Spirit** Synergy is
>    active, Nature Spirit Heroes will adjust their damage based on their remaining HP.

The Commander-DMG formula and its per-round base values are in [[commander]].

## Creep Round (id `3003307282`)
> In every stage, the player will encounter a Creep Round where items can be looted by killing
> the Creeps. Three pieces of equipment will be dropped at the same time. The player can pick one
> from them and the other two will disappear.

Equipment sources and the item model: [[equipment_and_economy]]. The gold numbers (base salary,
interest, streak, victory): [[gold_economy]].

## When each special round lands (the match calendar)

This tab gives the stage frame and the round *types*; the **schedule** of which special event
(creep, power card, blessing shifter, reward selection, auction) lands at which exact round
position is in [[rounds/index]], confirmed against a full replay.

## Shop draw rates (Hero tab, not Round)

round_03.png is actually the **Hero** tab's shop draw-rate table (a capture-time tab slip), so it
lives with the Hero-tab content: [[hero]] (Shop Refresh Probability), the full Lv.3 to Lv.10
table. The only round-relevance is that the Shop refreshes every round.
