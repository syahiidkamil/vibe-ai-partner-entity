# Go Go Cards (Commander Power Cards) — MCGG (concrete rung)

The game's signature twist, and the "Go Go" in the name. A Go Go Card is a chosen, run-shaping
power (the augment of MCGG), picked from a small hand at set points in a run. They bend a whole
run, not a single round: economy, EXP, free star-ups, team buffs, traps, equipment.

## Provenance (read this first)
First-party from the live client (v1.2.88.302.2, BlueStacks pull). The card text lives only in the
**localization pool** (`AllLanguageEN` -> `parsed/localization_en.json`): the card name/desc are
**runtime lookups** that consume zero bytes in any decoded table (the mulong "skip" column), so no
skill table stores a card stringId or a rarity column. In the pool, card names and effects are
interleaved with hero skills in column-major blocks (a names band, then a descs band), with no clean
per-card band. So this section resolves what is first-party verifiable and marks the rest
unresolved, never fabricating. Extractor + JSON: `work_dir/saori/mcgg/gen_gogo_cards.py` ->
`parsed/strategy/gogo_cards.json`. Governed by [[../../disclaimer]].

## The categories (UI filter tabs)
The card picker shows tabs: **All, Power Cards, Orange Cards, Purple Cards, Blue Cards**.
- **Power Cards** ([[power_cards]]): commander-themed, each tied to a Commander (the pink frame).
  Their effects are tied to that Commander's abilities.
- **Orange / Purple / Blue Cards** ([[generic_cards]]): the rarity tiers of the generic cards.
  Rarity ascends **Blue < Purple < Orange** (loc tab ids 1079733338 < 339 < 340; orange highest).

## How they fit the run (first-party)
- **The Power Card stage.** "Introducing Commander Power Cards in Round I-2! This new feature
  replaces the first Go Go Card round." Only Power Cards appear in this round, and your own
  Commander's exclusive Power Card is guaranteed among the options (`loc[2912711108]`).
- **Borrow or self-boost.** "You can boost your Commander with their own Power Card or borrow an
  ability from another Commander" (`loc[1629673760]`) -> non-exclusive Power Cards can be taken by
  any Commander; exclusive ones only by their owner.
- **Quality upgrade.** Cards can be upgraded by 1 quality tier (e.g. all available Go Go Cards at
  the start of Round II-3). At maximum quality, the upgrade pays out a random **Black Dragon
  Treasure** instead (`loc[2212550713]`, `loc[2212545908]`).
- **Interaction with comps.** A lifesteal card rewards a sustain board; a free-star-up card rewards
  committing to those heroes' [[../synergies]]; an economy card funds a later spike
  ([[../equipment_and_economy]]). The Go Go Box round ([[../game_rules_and_round_flow]]) supplies
  the pedestal rewards; cards bend the whole run.

## Counts (this resolution pass, 2026-06-28)
- **Power Cards:** 36 distinct "X's Power" names found first-party. 15 Commanders' cards identified
  (14 with effect text, Dyrroth label-only); 21 name-resolved, effect-unpaired. See [[power_cards]].
- **Anchors:** all 4 UI anchor cards (Minotaur, Kagura, Johnson, Lunox) confirmed **verbatim**.
- **Generic (Orange/Purple/Blue):** the effect set is partly enumerated; the per-card rarity tier is
  the open gap (no rarity column survives the datamine). See [[generic_cards]].

## Status: substantially resolved, with named gaps
Power Card names complete and the system fully first-party; per-card effect pairing partial (the loc
limitation above); generic-card rarity assignment unresolved. Feed a fresh UI capture of each card,
or a decode of the card-quality table, to close the gaps. Governed by [[../../disclaimer]].
