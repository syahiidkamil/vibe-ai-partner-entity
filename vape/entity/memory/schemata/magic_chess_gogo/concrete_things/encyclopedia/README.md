# Encyclopedia — MCGG in-app guide (first-party, verbatim)

The game's own in-app **Encyclopedia**, captured from the live client. This is the authoritative
rules text, verified tab-by-tab against the in-app screenshots (the localization was the starting
draft, the screenshots the source of truth). The distilled round-flow lives in
[[game_rules_and_round_flow]]; the deep particulars (heroes, synergies, items, cards) live in
their own concrete files. This folder is the **prose**; the **numbers** come from the decoded
S6 battle config.

## Provenance
- Prose: first drafted from `parsed/localization_en.json` (one stringId per panel), then verified
  and corrected tab-by-tab against the in-app Encyclopedia screenshots
  (`storage/magic-chess-gogo/encyclopedia/*.png`, 2026-06-28). Where the draft disagreed, the
  screenshot won (this pass fixed invented headings, a bogus season claim, and a misplaced table).
- Numbers: `readable/decoded/MCClassicsBattleConfig_S6.txt` (the S6 economy/stage XML).
- Both from the live MCGG client **v1.2.88.302.2** (BlueStacks pull, 2026-06-27).
- The localization extract `parsed/strategy/encyclopedia.json` (via `gen_encyclopedia.py`) is the
  draft layer; the committed files are the screenshot-verified version. Re-verify after any re-pull.

## The in-game tabs (UI labels, ids 1982040849-879)
Game Rules · Round · Hero · Commander · Gold · Advanced Tutorial · Synergy Guide · Season
Information. (A "Special Attack" label, id 1982040856, also sits in the strip.)

## Files
- [[game_rules]] — the four-point ruleset (Game Rules tab).
- [[round_and_battle]] — Battle Stage, Battle Round, Battle Complete, Creep Round + stage table.
- [[hero]] — Star & Quality, Faction & Role, Summoned Heroes, Shop Refresh Probability table.
- [[commander]] — Level & EXP, Upgrade Cost, Commander DMG (formula + stage-round base table).
- [[gold_economy]] — the Gold tab + the exact S6 income numbers.
- [[advanced_tutorial]] — the three advanced panels (Advanced Finance, Battle, Tactics).
- [[synergy_guide]] (Synergy Guide tab): the captured portion is the Neobeasts Point Rewards
  ladder; [[synergies]] holds the full rosters.
- [[season_information]] — Dawnlight Celebration header + three season guides (Commander Power
  Card, Blessing System, Go Go Auction).
- [[mode_and_feature_guides]] — the other MCGG guides NOT on the tab bar (Go Go Auction, Draft
  Pick, Commander Power Card, Crystal Dice, Magic Crystal/Rune, Auto Buy, Lock Shop, Collection
  Points, the Heartbond synergy tutorial) + an honest list of the image/interactive/UI-only ones.

Expiry and scope: [[disclaimer]].
