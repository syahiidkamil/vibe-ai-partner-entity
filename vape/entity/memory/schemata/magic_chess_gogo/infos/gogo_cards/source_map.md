# Source Map: where the Go Go Card facts come from

Provenance for [index](index.md), [power_cards](power_cards.md), and [generic_cards](generic_cards.md),
kept here so those files stay essentials-only. Governed by [[../../disclaimer]].

## Source: the in-game card picker UI (exact)

Every card name, effect, and number is transcribed **exact from the in-game Go Go Card picker**,
captured per rarity tab (S6, 2026-06-28). Raw screenshots:
`storage/magic-chess-gogo/gogo_cards/{power,blue,purple,orange}_cards/*.png`. Each PNG is a scroll
position of one scrolling grid, so cards repeat across consecutive shots; the lists are deduped
across the scrolls (one card kept per unique name+effect; a card cut off in one shot is taken from
the shot where it is full).

## Why the UI, not the data dump

The card name/desc are **runtime lookups** that consume zero bytes in any decoded table (the mulong
"skip" column), and in the localization pool the card strings are interleaved with hero skills in
column-major blocks with no clean per-card band and no stored rarity column. So the datamine could
neither pair each effect to its card nor assign rarity, only enumerate name fragments. The UI
capture closes both gaps cleanly. The earlier loc-based extractor
(`work_dir/saori/mcgg/gen_gogo_cards.py` -> `parsed/strategy/gogo_cards.json`) is superseded by this
pass for effects/rarity; it remains only as the name-fragment record.

## Counts (this resolution pass, 2026-06-28)

- **Power Cards:** 46 (commander cards; several Commanders contribute two: an exclusive plus a
  borrowable variant).
- **Generic:** Blue 19, Purple 66, Orange 46 = 131.
- **Total: 177 cards.** In `generic_cards.md` the 15 purple Synergy Badges and 15 orange Synergy
  Blessings are each collapsed into one summary bullet (so the bullet count is lower than the card
  count by 14 per section).

## What is still not data-extracted

The internal card-quality scaling table (the engine numbers behind the `I/II/III` tiering) is not
decoded, but every **displayed** output is captured from the UI, so nothing player-visible is
missing. Re-capture on a season patch.
