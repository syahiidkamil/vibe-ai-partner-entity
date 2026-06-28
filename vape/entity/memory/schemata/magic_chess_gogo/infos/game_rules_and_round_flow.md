# Game Rules & Round Flow — MCGG (concrete rung)

The rules of play, now **first-party**: the game's in-app Encyclopedia (localization) and the
decoded **live S6 battle config**, cross-checked against the 23-screen tutorial. Tags:
**[confirmed]** = lifted from the encyclopedia or the `MCClassicsBattleConfig_S6` table;
**[unknown]** = still not in the data I have (do not assert; held in pencil per [[disclaimer]]).
The fuller verbatim text lives in [[encyclopedia/README]].

## The frame
- **8 Commanders**, free-for-all; each Commander is a player (me). **[confirmed]**
- **Win condition:** last Commander standing becomes the **Champion**. **[confirmed]**
- **Commander HP:** a life total that drops when you lose a PvP round; at 0 you are out. Exact
  starting value not in these tables (genre norm ~100). **[confirmed mechanic, start unknown]**

## The round, step by step
1. **Gold** arrives at round end (not start): base salary + interest + streak + victory. Exact
   numbers in [[encyclopedia/gold_economy]]. **[confirmed]**
2. **Shop** **refreshes automatically** each round start; the Commander also gains **2 EXP**. Buy
   a hero, **refresh** for a new offer, or **level up**. **[confirmed]**
3. **Place & position** within **Hero Capacity** (set by Level). Every hero is **front-row** or
   **back-row**; melee/high-DEF front, ranged/high-DMG back. **[confirmed]**
4. **Star-Up:** 3 identical heroes auto-combine to the next star (1->2->3); nine 1-stars make a
   3-star. Five quality tiers (cost 1-5). **[confirmed]**
5. **Combat** auto-resolves in a Battle phase; no input mid-fight. **[confirmed]**
6. **Resolve:** lose the PvP fight -> lose Commander HP equal to the Commander DMG (below).
   **[confirmed]**

## The 4-stage structure **[confirmed]**
A match is **four stages (I-IV)**, each several rounds, each ending in a **Go Go Box** round.
Advancing a stage grants **increased basic rewards and higher Commander DMG**; Stage IV is the
final, faster-killing stage. Exact stage->round map (`<SMCRoundRange>`):

| Stage | Rounds | Round Base DMG |
|------|--------|----------------|
| I    | 1-4    | 3 |
| II   | 5-10   | 5 (r5-8), 6 (r9-10) |
| III  | 11-16  | 7 (r11-13), 11 (r14-16) |
| IV   | 17-99  | 13 (r17-19), 14 (r20-22), 15 (r23+) |

## Battle Acceleration **[confirmed]**
Each round is a **Preparation phase** then a **Battle phase**; **Battle Acceleration** begins in
the **last 10s** of the Battle phase. During it, all units gain massive Resilience, ATK Speed,
Hybrid ATK, and extra DMG every second, while Healing and Shield Effects are sharply reduced
(the overtime that forces a result).

## Commander DMG (HP loss on a lost round) **[confirmed]**
`Commander DMG = Round Base DMG (table above) + Total Star Levels of the winner's surviving units`,
**+1 per surviving non-Hero (summoned) unit**. A **draw** makes both sides deal DMG. (A separate
**Arena** mode instead deducts a flat 25 HP per loss; see [[encyclopedia/season_information]].)
Nature Spirit heroes scale their contribution by remaining HP.

## The gold economy (live S6) **[confirmed except where noted]**
Start with **2 Gold**. Each round end: **base salary 5** (flat; +2 at rounds 17-22, +3 at round
23+), **interest +2 per 10 Gold held, capped +4**, **win/lose streak bonus** (array 1;1;2;3 by
streak length; per-streak split inferred), **+1 per round won** (and +1 for clearing a Creep
round). Some Commanders earn extra gold. Full table + caveats: [[encyclopedia/gold_economy]].

## Commander Level & capacity
- **Level** (Lv, with an XP bar) raised by spending gold for EXP (1:1) or the 2 EXP/round.
  **[confirmed]**
- Level sets **Hero Capacity** (board size) and raises the odds of high-quality heroes in the
  shop. Exact level->capacity and level->tier-odds tables are data-driven and not in this config.
  **[unknown]**

## Round types (the rhythm) **[confirmed]**
- **PvP combat** — your board vs another Commander's; drains the loser's HP (the main loop).
- **Creep round (PvE)** — fight monsters; **3 equipment drop, pick 1**, the rest vanish; +1 gold.
- **Go Go Box** — a shared reward stage at each stage's end; all Commanders pick in turn
  (catch-up: lowest HP first).
- **Power Card selection** — choose a **Go Go Card** at set points. See [[gogo_cards/index]].

## New mechanics worth knowing
- **Blessing System:** from Round II-1, combining a 2-star (when no hero holds a Blessing) grants
  **+1 to one of its Synergy counts** for free. **[confirmed]** — [[encyclopedia/hero]].
- **Summoned Heroes:** some synergies summon units that **don't use Capacity**; they vanish if
  the synergy goes inactive. **[confirmed]** — [[encyclopedia/hero]].

## Where it connects
Heroes + per-star stats: [[heroes/index]]. Synergies: [[synergies]]. Equipment + pool economy:
[[equipment_and_economy]]. Full verbatim rules: [[encyclopedia/README]]. The loop + strategy
spine: [[schemata]].
