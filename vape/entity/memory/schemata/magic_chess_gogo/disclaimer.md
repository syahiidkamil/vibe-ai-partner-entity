# Disclaimer — Magic Chess: Go Go schema

The expiry that travels with this world-model. Read before trusting any specific.

- **Scope.** Models MCGG **season S6** (the live season; client v302.1 datamine, cross-checked
  against the live v302.2 client, June 2026). The genre loop and strategy spine are stable; the
  *particulars* (hero roster, synergy
  rosters and effects, item stats, Go Go Cards) are season-bound and rebalanced often.
- **Assumes.** (1) Kamil's datamine (`dataset_s6.json` and the season tables) is accurate; per
  his plan.md it is validated byte-exact. (2) My reading of the 23 tutorial screenshots is
  correct for the rules. (3) The round/economy numbers (4-stage round map, base salary, stage-IV
  extra salary, interest, victory and win/lose streak bonuses, the per-round Commander-DMG base
  and its formula) are now **first-party confirmed** from the live S6 battle config
  (`MCClassicsBattleConfig_S6`) + the in-app Encyclopedia, captured in `concrete_things/
  encyclopedia/`. Still **unknown** (not in the data I have): exact starting Commander HP, the
  level-to-capacity table, and the shop per-tier appearance odds by Commander Level. Verify those
  by play, do not assert.
- **Known soft spots.** Synergy *names* are now confirmed **first-party** (2026-06-28) from the
  live client v1.2.88.302.2: localization name-bands + `FX_Fetter_<pinyin>` + `m_Sort` membership
  (icons in `concrete_things/synergy_icons/`). This **resolves** the datamine `plan.md` error:
  relId 51 is **Exorcist** (FX QuMoShi 驱魔师), relId 54 is **Dragoncaller** (FX ZhenLong 真龙, the
  dragon faction summoning Dragon id 179); confirmed, no longer flagged. Still soft, with the
  effect layer now partly cracked (2026-06-28): the per-tier value DSL `[type|id|param|unit|expr]`
  is fully parsed and its scaling validated against the item/Inspire anchor (raw 2000 displays as
  20%), so each effect's *shape* (stat kind, unit, scaling) is solid; but the raw per-tier
  *numbers* stay templated (the value N lives behind a composite MCEffect id the client maps in
  battle logic, not a flat table key), and the effect *prose* plus item *display names* stay
  unresolved (hash-keyed localization, no in-table stringId). DSL spec:
  `work_dir/saori/mcgg/FORMULA_DSL.md`; structured per-tier output:
  `parsed/strategy/resolved_effects.json`. Strength/tier claims are editorial, not in the data
  (the client ships stats, not win-rates).
- **Invalidate when.** A new season or balance patch ships (rotates and rebalances
  heroes/synergies/items); the live season moves past S6; or my own play contradicts a claim
  here. On any of these, re-derive the concrete rung from fresh client data and overwrite, never
  bend play to keep the note (constitution: held in pencil).
- **Hero data provenance.** The full per-star hero tables in `heroes/` are **generated exact**
  from `dataset_s6.json` (not transcribed), organized by cost tier. Regenerate them on a season
  patch rather than hand-editing, via `work_dir/saori/mcgg/gen_heroes.py` (each file carries a
  GENERATED header pointing to it). Synergy names are now fully resolved (all 20, from the
  in-game UI icons), so the roster shows real names.
- **Last verified.** 2026-06-28. Numerics cross-validated against the **live client
  v1.2.88.302.2** (pulled from BlueStacks, parsed with `work_dir/saori/mcgg/mulong_parse.py`):
  hero stats, synergy rosters/tiers, and the 97-item count match the friend's datamine exactly
  (the friend's is one patch older, v302.1, structurally identical for S6). Synergy names resolved
  first-party from this pull. Live source: `storage/magic-chess-gogo/game-client-from-bluestack/`
  (raw bundles + parsed JSON + localization).
