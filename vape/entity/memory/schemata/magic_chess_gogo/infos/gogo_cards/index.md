# Go Go Cards (Commander Power Cards) — MCGG (concrete rung)

A Go Go Card is MCGG's augment: a run-shaping power picked from a small hand at set points, bending
the whole run (economy, EXP, free star-ups, buffs, traps, equipment), not one round.

177 cards (Power 46, Blue 19, Purple 66, Orange 46), every effect exact from the card picker.
Source: [source_map](source_map.md).

## The categories (UI filter tabs)
The picker shows tabs: **All, Power Cards, Orange Cards, Purple Cards, Blue Cards**.
- **Power Cards** ([[power_cards]]): commander-themed (pink frame), each tied to a Commander; some
  Commanders have two (an exclusive and a borrowable). `(Exclusive)` = only its own Commander.
- **Orange / Purple / Blue Cards** ([[generic_cards]]): the rarity tiers of the generic cards.
  Rarity ascends **Blue < Purple < Orange**; higher rarity = a stronger roll of the same effect.

## Patterns worth knowing
- **Tiered families** carry a `I / II / III` suffix tracking rarity (Blue/Purple/Orange): e.g.
  Barrier's Seal I/II/III = +650/+950/+1900 front-row HP. Same for Breath of Berserk, Thickened
  Blood, Magic Immersion, Customize Recruitment, Solid Alliance, Purest Power, Dimensional Shot,
  Attack & Defend, Glittering Jewels, Premium Client.
- **`+` variants** are upgraded versions (Reinforcement+, Golden Era+, Shield of Fortune+, ...).
- **Synergy reward cards**: **Blessing** (orange) = Magic Crystal + item + hero; **Badge** (purple)
  = Magic Crystal + hero. One per synergy; this is a draw-path for the [[../synergies/synergies]]
  Magic Crystal that grants +1 synergy count.

## How they fit the run (first-party)
- **The Power Card stage.** "Introducing Commander Power Cards in Round I-2! This new feature
  replaces the first Go Go Card round." Only Power Cards appear that round, and your own Commander's
  exclusive Power Card is guaranteed among the options.
- **Borrow or self-boost.** Non-exclusive Power Cards can be taken by any Commander; exclusive ones
  only by their owner.
- **Quality upgrade.** Cards can be upgraded by 1 quality tier (e.g. all available cards at the
  start of Round II-3). At maximum quality, the upgrade pays a random **Black Dragon Treasure**
  instead (e.g. Yu Zhong's Power).
- **Interaction with comps.** A lifesteal card rewards a sustain board; a free-star-up card rewards
  committing to those heroes' [[../synergies/synergies]]; an economy card funds a later spike
  ([[../equipment_and_economy]]). The Go Go Box round ([[../game_rules_and_round_flow]]) supplies
  pedestal rewards; cards bend the whole run.

## Observed in play (high-confidence assumptions, not datamined)

From watching actual matches (the [replay](../../experience/custom_with_computer/replay.md) + Kamil's
play), held as high-confidence assumptions rather than data facts. See [source_map](source_map.md).

- **Offerings are random but synergy-biased.** The cards offered are not uniform-random: they lean
  toward the synergies of the heroes you have **deployed or on the bench**, so a committed comp tends
  to be shown cards that pay it off. A bias, not a guarantee.
- **Your commander's own Power Card is always in the I-2 offer.** One of the Power Cards offered at
  the I-2 stage always matches your selected Commander (replay: commander Kagura was offered Kagura's
  Power). This is the player-visible face of the first-party rule above (your Commander's exclusive
  Power Card is guaranteed among the options).
- **2 refreshes per card selection, one card at a time.** Each Go Go Card selection grants **2
  refreshes**, and a refresh re-rolls only **one** of the two offered cards (you choose which), never
  both at once (the picker shows a `Refresh ×2` charge on each card; seen at I-2, II-3, III-3).
