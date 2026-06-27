# Disclaimer — Magic Chess: Go Go schema

The expiry that travels with this world-model. Read before trusting any specific.

- **Scope.** Models MCGG **season S6** (the live season in the datamined client v302.1, June
  2026). The genre loop and strategy spine are stable; the *particulars* (hero roster, synergy
  rosters and effects, item stats, Go Go Cards) are season-bound and rebalanced often.
- **Assumes.** (1) Kamil's datamine (`dataset_s6.json` and the season tables) is accurate; per
  his plan.md it is validated byte-exact. (2) My reading of the 23 tutorial screenshots is
  correct for the rules. (3) Where the tutorial was silent (gold interest, win/loss streak
  bonuses, exact starting Commander HP, the exact level-to-capacity table), I marked it
  **inferred from standard auto-chess**; verify by play, do not assert.
- **Known soft spots.** Synergy and item *names* are not in the client (null/templated, no
  in-table stringId); they were resolved on 2026-06-27 from in-game UI screenshots, matched to the
  icons (now in `concrete_things/synergy_icons/`). This corrected the datamine `plan.md`: relId 51
  is **Exorcist**, relId 54 is **Dragoncaller** (the dragon faction, which summons the Dragon id
  179) — flagged for Kamil to confirm. Per-tier synergy/item *effect* text is still templated and
  mostly absent. The HeroQuality_MC pool numbers decode scrambled (a ver-2 format the auto-decoder
  mishandles), so trust the column *meanings*, not the raw counts. Strength/tier claims are
  editorial, not in the data (the client ships stats, not win-rates).
- **Invalidate when.** A new season or balance patch ships (rotates and rebalances
  heroes/synergies/items); the live season moves past S6; or my own play contradicts a claim
  here. On any of these, re-derive the concrete rung from fresh client data and overwrite, never
  bend play to keep the note (constitution: held in pencil).
- **Hero data provenance.** The full per-star hero tables in `heroes/` are **generated exact**
  from `dataset_s6.json` (not transcribed), organized by cost tier. Regenerate them on a season
  patch rather than hand-editing, via `work_dir/saori/mcgg/gen_heroes.py` (each file carries a
  GENERATED header pointing to it). Synergy names are now fully resolved (all 20, from the
  in-game UI icons), so the roster shows real names.
- **Last verified.** 2026-06-27, from the tutorial images and the datamine plan.md + S6 client
  tables (heroes generated from `dataset_s6.json`, synergies via extraction agent,
  equipment/economy verified against raw JSON).
