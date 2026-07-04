# Equipment & Economy — MCGG S6 (concrete rung)

Items held on heroes, and the gold/pool economy under the shop. Source: `MCEquipBase.json`,
`attr_names.json`, `EquipSuit_MC.json`, `HeroQuality_MC.json` (verified against the raw client).
Item *stat names* are owner-curated and mostly blank in the client (the same no-stringId wall as
synergy names), so attrs are recorded by **attrId**, not invented names.

## Equipment model
- **~97 base items** (`MCEquipBase.json`; ~37 more season items live in per-season tables). No
  recipe tree (`m_Relation = 0` on all 97 — unlike TFT, items are whole, not crafted from
  components).
- Each item record has 48 fields. **94 of 97 carry a skill** (`m_SkillList`, e.g. an item that
  grants a small active/passive), so most items do more than raw stats.
- **Attribute slots** (the `(attrId, value)` stat blocks; raw values ~x10-scaled, 1000 = 100):
  - **primary** — up to 3 stats (`m_Attr1..3`); the main slot. ~19 items stack a 2nd/3rd stat.
  - **extra** — schema exists but **unused this season** (0 populated).
  - **exclusive** — 6 items carry one exclusive-slot stat (special, grouped).
- **Tier** = `m_ModelLevel`: tier 1 (21 items), tier 2 (74), tier 3 (2). Higher tier = stronger.
- **Placement** (`m_Slot`): 94 items fit any of a hero's **3 gear slots** ([1,2,3]); a few are
  slot-restricted.

### The 13 attrIds in use (by frequency, with the client's own hint-guesses)
- **1021** (31 items) and **1031** (29) — the two **core damage/HP stats** (values 1000-5500).
- **1001** (23) — likely **HP / a defensive stat** (1000-4000).
- **1042** (7) — flagged percent by the data.
- **1062** (6), **1072** (6) — small values (20/50), so **likely % stats** (atk-speed / crit /
  CDR-type).
- **18, 62, 22, 1180** — low-frequency primary stats. **12, 13, 92** — the exclusive-slot stats.
Stat *names* unresolved (owner-curated `attr_names.json`); kept as ids, honestly.

### The one set (`EquipSuit_MC`)
A single set, id 1001: components **items 1101 + 1102** grant **skill 25950**. (Those two
component ids are not in the base table; they live in a separate/season table.) No other sets.

## Where equipment comes from
Not bought in the gold shop. It drops from **creep (PvE) rounds** (pick 1 of a few) and the
**Go Go Box** shared stage. See [[game_rules_and_round_flow]].

## Named items and UI categories (from the in-game UI)

The datamine gives item stats and ids but not names/effects (effects are templated formula strings
in the lang tables, e.g. `Unique Passive - {0}:`). The in-game UI supplies the readable names and
effects; captured here from screenshots (`storage/magic-chess-gogo/ui_reference/equipment_all.png`
and `equipment_inspire_enhanced.png`, 2026-06-27). Item NAMES are also confirmed present in the lang
storage (Inspire, Aegis, Purify, Retribution, Revitalize), so names are recoverable; the clean
per-item EFFECTS are best taken from the UI.

- **UI category tabs:** Regular · Magic Crystal · Synergy Exclusive · Commander Exclusive · Special.
- **Type groups:** Basic · Physical · Magic.
- **Basic / Enhanced:** each item has a Basic and an Enhanced version; Enhanced adds one extra
  Unique Passive.

**Basic items (captured):**
- **Inspire** (Increase ATK Speed): Unique Passive - Inspire: provide 20/25/30/40% ATK Speed
  (increases with Stage progression). Enhanced Inspire adds Unique Passive - Swift: gain 20% ATK
  Speed.
- **Revitalize · Purify · Aegis · Retribution**: names confirmed (UI + lang storage); effects not
  yet captured.

**Physical items:** four seen in the UI, names not readable in the crop. Partial.

Status: partial. Feed more equipment tabs to complete the named list; a full programmatic pull needs
the Windows-client datamine (name resolution + effect formulas).

## The shop/gold economy (`HeroQuality_MC`) — column meanings reliable, numbers NOT
This table sets the **shared hero pool** (how many copies of each hero exist for all 8
Commanders to draw from, the contention that makes contested heroes scarce). Columns, inferred:
- `m_Quality` — the cost/rarity tier the row configures.
- `m_Base` — base copies of each hero of that tier seeded into the shared pool.
- `m_Multiplemin` / `m_Multiplemax` — a min/max multiplier (bound), plausibly scaling with stage
  or lobby size.
- `m_NewPlayerBase` — the (more generous) pool base used in the new-player economy.

**Honest caveat:** the decoded *values* come out scrambled/column-misaligned (a ver-2 binary
format the auto-decoder mishandles, per plan.md), so trust the **column meanings**, not the raw
six rows. Re-derive the real per-tier pool counts from a clean decode before relying on a number.
Standard auto-chess pool logic (cheaper heroes = many copies, expensive = few) is the
**[inferred]** prior until then. Gold income, interest, and streak bonuses were not in these
tables (genre-standard, [inferred]; see [[game_rules_and_round_flow]]). Governed by [[disclaimer]].
