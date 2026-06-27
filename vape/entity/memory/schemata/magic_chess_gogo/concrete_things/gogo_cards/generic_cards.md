# Generic Go Go Cards (Blue / Purple / Orange) — MCGG (concrete rung)

The non-commander Go Go Cards: the generic run-shaping effects, sorted into three rarity tiers.
These are the cards under the **Blue / Purple / Orange** tabs (the Power Cards tab is separate, the
commander cards in [[power_cards]]). First-party from the live client localization
(v1.2.88.302.2); method and limits in [[index]] and [[../../disclaimer]].

## The rarity system (first-party)
- Three tiers, ascending: **Blue < Purple < Orange** (loc tab ids 1079733338 < 339 < 340; orange the
  highest). A separate progress-chest scale uses Green < Blue < Purple < Gold for its own rewards
  (`loc[2212551770..794]`), distinct from the card tabs.
- **Quality upgrade.** Effects exist that bump available/subsequent cards by 1 quality tier; at
  maximum quality the bump pays a random **Black Dragon Treasure** instead (`loc[2212550713]`,
  Round II-3 variant `loc[2212545908]`, Yu Zhong's exclusive variant in [[power_cards]]).
- Higher rarity generally means a stronger roll of the same effect family (more Gold, more
  refreshes, better chests). The exact per-tier numbers live in the card-quality table, unresolved.

## Generic card effect families (verified strings, rarity per-card UNRESOLVED)
Template text; the rarity tier each instance belongs to is the open gap (no rarity column survives
the datamine, see below). Examples of the effect families:
- **Gold**: Gain `<Num1>` Gold.
- **Free refresh**: Gain `<Num1>` free Shop refresh(es).
- **Equipment Chest**: Obtain `<Num1>` Equipment Chest(s).
- **Magic Crystal Chest**: Obtain `<Num1>` Magic Crystal Chest(s).
- **Copy Trick**: When HP first drops to `<%Num1>` in battle, summon a copy of the carrier that
  deals `<%Num2>` DMG; the copy grows stronger over time.
- **Quality upgrade**: the subsequent / available Go Go Cards are upgraded by 1 quality tier (see
  above).
- **Black Dragon Treasures** (the max-quality payouts): Gain Magic Crystal x`<Num1>`; or random
  Equipment x`<Num1>` and `<Num2>` Gold; or a Hero of your highest-count Synergy x`<Num1>`; or
  `<Num1>` Gold.

Other named generic effects seen in the pool but not yet tier-tagged: Verdant Huntress, Phantom
Resonance, Justice, Battle Fury, Exquisite Toy, Feral Command (each a card name with its own effect
string interleaved among hero skills).

## The gap (honest)
A complete per-tier enumeration (every Blue, Purple, Orange card with its exact effect and numbers)
is **not** resolvable from this datamine: the card name/desc are runtime lookups absent from every
decoded table, so no stored rarity column or per-card stringId exists, and the loc pool interleaves
generic-card strings with hero skills in column-major blocks. Closing it needs either a UI capture
of each rarity tab, or a decode of the card-quality / distribution table
(`MC_DistributeCardCon`, `MCSpecialCardPool`, or the GoGo `MCSuperPowerKey` icon table, none
schema-cracked yet). Until then: families verified, per-card rarity marked unresolved, nothing
fabricated. Full record: `parsed/strategy/gogo_cards.json`.
