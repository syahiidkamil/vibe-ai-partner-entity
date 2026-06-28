# Encyclopedia: Season Information, Synergy Guide, and the Arena side-mode

The last two encyclopedia tabs plus the Arena Match Guide (a separate mode that shares the
encyclopedia). Sources noted per item.

## Season Information

Transcribed from the in-app Encyclopedia screenshots (season_information_01/02.png), 2026-06-28,
live client v1.2.88.302.2.

The live season is **S6** (`dataset_live_s6.json` meta), surfaced in-client as the **Dawnlight
Celebration** event (id `3275246170`). "Dawnlight Celebration" is the header title shown at the
top-left of this tab, above the "Arena" label. The datamined event blurb:
> Come and join the Dawnlight Celebration! The new Season Factions are here! Plus, the Go Go
> Auction mode makes a surprise return!

The string **"Rising Dawn"** also appears as a season-title string in this build (ids 523494437,
2395214313). Treat "S6 / Dawnlight Celebration" as the authoritative live-season handle (it matches
the datamine meta); the exact in-UI season name may localize differently by region. Scope and
expiry: [[disclaimer]].

The in-app **Season Information** tab (the rightmost Encyclopedia tab, after Synergy Guide)
documents this season's three new or returning mechanics, transcribed in full below.

### Commander Power Card Guide
1. Introducing Commander Power Cards in Round I-2! This new feature replaces the first Go Go Card
   round.
2. Each Commander has a unique Power Card that provides effects tied to their abilities.
3. Only Power Cards appear in this round, with your Commander's exclusive Power Card guaranteed
   among the options. Choose wisely to seize victory!

### Blessing System
- **Blessing Effect:** Increases one of the Hero's Synergy counts by 1.
- **How to Trigger:**
  1. Starting from Round II-1, if no Heroes have a Blessing Effect (excluding those granted by
     Commander Skills or Synergies), combining a 2-Star Hero grants a Blessing Effect to one of
     their random Synergies.
  2. Certain Commander Skills or Synergies can grant an additional Blessing Effect to a Hero.

### Go Go Auction Guide
1. Enter the Auction Arena at round II-6.
2. Players gain Gold based on Commander HP (from low to high): 10, 8, 6, 4, 1, 1, 1, 1.
3. 8 reward sets are available in the Auction Arena. Enter a reward zone to place your bid.
4. Bid prices are fixed at: 0, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30.
5. If no competition occurs within 10 seconds, the highest bid wins.
6. When bidding ends, winners receive rewards at their bid price. Players who don't win any bids
   get one random unsold reward at base price.

## Synergy Guide
The **Synergy Guide** tab (label id 1982040857) is a generated UI list of the season's synergies
and their tier effects, driven by the relation tables rather than a single prose panel. The full,
structured synergy data lives in [[synergies]] (20 synergies: 10 class + 10 faction, with member
thresholds). The summoning synergies are noted in [[hero]].

## Arena (a separate mode, not the main auto-battler)
The encyclopedia also carries an Arena **Match Guide** (ids `2912711140`-`2912711147`). Arena
differs from the standard Magic Chess mode the rest of this schema models, so it is kept here, not
folded into [[game_rules_and_round_flow]]:
- Build from your **own** Hero pool, **no time limit** in Preparation; then face a random opponent
  who reached the same round.
- Each match lasts up to **9 rounds**; **each loss deducts 25 HP** (flat, not the scaled Commander
  DMG); eliminated after **4 losses**. Trophies tallied at the end decide win/loss.
- Pick a **Go Go Card** at the start of rounds **2/4/6**; spend Gold in the **Arena Shop** at the
  start of rounds **3/5/7**.
- Economy: base reward each round, **no Interest**, **+2 Gold per round won**, loss gives a Loss
  Compensation; **no win/lose streak bonuses**.

This is useful context for play but does not change the main-mode rules above.
