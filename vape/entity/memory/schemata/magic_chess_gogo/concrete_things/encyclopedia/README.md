# Encyclopedia — MCGG in-app guide (first-party, verbatim)

The game's own in-app **Encyclopedia**, captured from the live client. This is the authoritative
rules text, lifted verbatim from the localization (color/markup stripped, `##` rendered as line
breaks). The distilled round-flow lives in [[game_rules_and_round_flow]]; the deep particulars
(heroes, synergies, items, cards) live in their own concrete files. This folder is the **prose**;
the **numbers** come from the decoded S6 battle config.

## Provenance
- Prose: `parsed/localization_en.json` (one stringId per panel; ids noted on each file).
- Numbers: `readable/decoded/MCClassicsBattleConfig_S6.txt` (the S6 economy/stage XML).
- Both from the live MCGG client **v1.2.88.302.2** (BlueStacks pull, 2026-06-27).
- Extracted exact (not transcribed) by `work_dir/saori/mcgg/gen_encyclopedia.py` ->
  `parsed/strategy/encyclopedia.json`. Regenerate on a client re-pull / season patch.

## The in-game tabs (UI labels, ids 1982040849-879)
Game Rules · Round · Hero · Commander · Gold · Advanced Tutorial · Synergy Guide · Season
Information. (A "Special Attack" label, id 1982040856, also sits in the strip.)

## Files
- [[game_rules]] — the four-point ruleset (Game Rules tab).
- [[round_and_battle]] — Battle Stage, Battle Round, Battle Complete, Creep Round + stage table.
- [[hero]] — Star & Quality, Faction & Role, Summoned Heroes, Blessing System.
- [[commander]] — Level & EXP, Commander Skills, Commander DMG (formula + round-base table).
- [[gold_economy]] — the Gold tab + the exact S6 income numbers.
- [[advanced_tutorial]] — the three advanced strategy panels.
- [[season_information]] — the live season (Dawnlight Celebration) and the Arena side-mode.
- [[mode_and_feature_guides]] — the other MCGG guides NOT on the tab bar (Go Go Auction, Draft
  Pick, Commander Power Card, Crystal Dice, Magic Crystal/Rune, Auto Buy, Lock Shop, Collection
  Points, the Heartbond synergy tutorial) + an honest list of the image/interactive/UI-only ones.

Expiry and scope: [[disclaimer]].
