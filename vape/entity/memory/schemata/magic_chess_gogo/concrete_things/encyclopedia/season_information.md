# Encyclopedia: Season Information, Synergy Guide, and the Arena side-mode

The last two encyclopedia tabs plus the Arena Match Guide (a separate mode that shares the
encyclopedia). Sources noted per item.

## Season Information
The live season is **S6** (`dataset_live_s6.json` meta), surfaced in-client as the **Dawnlight
Celebration** event (id `3275246170`):
> Come and join the Dawnlight Celebration! The new Season Factions are here! Plus, the Go Go
> Auction mode makes a surprise return!

The string **"Rising Dawn"** also appears as a season-title string in this build (ids 523494437,
2395214313). Treat "S6 / Dawnlight Celebration" as the authoritative live-season handle (it matches
the datamine meta); the exact in-UI season name may localize differently by region. Seasons run
**three months**; rank resets and finale mail-rewards at the boundary. Scope and expiry:
[[disclaimer]].

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
