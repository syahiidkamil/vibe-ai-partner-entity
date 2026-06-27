# Go Go Cards (Commander Power Cards) — MCGG (concrete rung)

The game's signature twist, and the "Go Go" in the name. A Go Go Card is a chosen, run-shaping
power (the augment of MCGG), picked from a small hand at set points in a run.

## Provenance (read this first)
This data is NOT in the datamined client. The consolidated dataset has heroes/synergies/items/comps
but no card table, and a content-grep of the extracted lang tables finds none of the card text
("Copy Trap", "gold per round", the "X's Power" names are all absent). So it comes from the in-game
UI (screenshots in `storage/magic-chess-gogo/ui_reference/gogo_cards_all.png`) and the tutorial. A
programmatic pull would mean extending the Windows-client datamine to decode the card table; the Mac
app ships a sparse, runtime-downloaded bundle, so it is not a viable mining source.

## The card categories (UI tabs)
- **Power Cards**: commander/hero-themed powers, each tied to a hero (the pink portrait frame).
- **Orange / Purple / Blue Cards**: rarity tiers of the generic cards (orange the highest).

The captured Power Cards: [[power_cards]]. (Orange/Purple/Blue not yet captured.)

## How they fit the run
Chosen at set points (the tutorial's "select a Go Go Card"). They bend a whole run, not a single
round: economy boosts, EXP, free star-ups, team buffs, traps. They interact with comps (a lifesteal
card rewards a sustain board; a free-3-stars card rewards committing to those heroes' synergies).

## Status: partial
Only the Power Cards visible in one screenshot are captured (see [[power_cards]]). Feed more UI tabs
(Orange/Purple/Blue, and the rest of the Power Cards) to complete this, or datamine the card table
for the full list. Governed by [[disclaimer]].
