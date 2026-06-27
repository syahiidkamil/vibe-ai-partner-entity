# Encyclopedia: Gold (and the exact S6 income numbers)

The in-app **Gold** tab (prose) plus the first-party S6 economy numbers from the decoded battle
config. The prose says "a certain amount" / "some Gold"; the config gives the actual values.

## Gold tab, verbatim (id `3003307287`)
> 1. **Basic Reward** — You will automatically get a certain amount of Gold at the end of each
>    round.
> 2. **Interest** — You can get 2 Gold as Interest for every 10 Gold you have at the end of each
>    round (up to a max of 4 Gold).
> 3. **Winning or Losing Streak Bonus** — You can get some Gold based on your current winning or
>    losing streak at the end of each round.
> 4. **Victory Reward** — You will get 1 Gold after each victory.
> 5. **Commander** — Some Commanders can help you earn extra Gold.

Shop actions (id `3003307288`): 1. Purchase to recruit Heroes. 2. Refresh the Shop. 3. Level up
your Commander.

## The exact numbers (first-party, `MCClassicsBattleConfig_S6.txt`)

| Source | Value | Config |
|--------|-------|--------|
| Starting resources | **2 Gold**, 1 EXP at match start | `AResourceInit iMoneyInit=2 iExpInit=1` |
| Base salary (per round) | **5 Gold**, flat (no per-round increase) | `ABaseSalary 5/0/5` |
| Stage IV extra salary | **+2** rounds 17-22, **+3** round 23+ (<=16: +0) | `SExtraSalary` |
| Interest | **+2 per 10 Gold** at round end, **cap +4** (maxes at 20 Gold) | loc + `Interest=4` |
| Victory reward | **+1** per round won; **+1** for clearing a Creep round | `AVictoryReward 1/1` |
| Win streak bonus | array **1;1;2;3** by streak length (caps +3) | `AContinueVictoryReward` |
| Lose streak bonus | array **1;1;2;3** by streak length (caps +3) | `AContinueFailureReward` |
| Commander EXP | **+2 EXP** per round start; Gold can be spent 1:1 for EXP | loc 3003307285 |

So a typical round-end income is: **5 (base) + interest (0-4) + streak (0-3) + 1 if you won**, plus
any Commander-specific gold. In Stage IV the base rises to 7 (round 17-22) then 8 (round 23+).

**Honest flags.** The streak arrays `1;1;2;3` and their start field (`iContinueVictoryTimes=1`) are
first-party exact; the precise streak-length -> array-index mapping (whether a 2-streak reads the
1st or 2nd element) is my reading, not stated in-data, so treat the per-streak split as the likely
shape, not gospel. The **shop per-tier appearance probability by Commander Level** is a separate
numeric grid not present in the localization or this config; it remains **unknown** (do not invent).
The shared-pool copy-counts per tier are in [[equipment_and_economy]] (column meanings reliable,
raw values flagged). Governed by [[disclaimer]].
