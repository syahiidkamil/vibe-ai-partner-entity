# Synergies — MCGG S6 (concrete rung)

The 20 team-bonus groups ("Sort"/relations). Source: `dataset_s6.json` + `synergy_names.json` +
`plan.md`. **Member rosters and activation tiers are solid ground truth.** Names and per-tier
effect *text* are mostly NOT in the client (the game resolves them from a language pool with no
relationId key), so most names are unresolved and effect gists read "not in data." The only
per-tier numbers the data carries are the activation count (`need`) and a `dps` scaling value.

**Axis.** class = relId 1-10 (role/archetype-pure, RelationType 2). faction = relId 50-59
(origin-mixed, RelationType 1). A hero usually belongs to one class and one faction.

**Confirmed names (5 of 20):** 3 Defender, 5 Marksman, 6 Mage (from synergy_names.json); 8
Assassin, 51 Dragon Altar / Dragoncaller (from plan.md). The other **15 are owner-to-name** —
Kamil is the domain expert (going pro) and the client literally ships `synergy_names.json` as an
owner-curated map. Identify each unresolved one by its member roster below; do not trust a guess.

## Class synergies (relId 1-10) — tiers = member counts that activate
- **r1** unresolved — tiers 2/4/6 — Gatotkaca, Belerick, Badang, Dyrroth, Masha, Yu Zhong
- **r2** unresolved — 2/4/6 — Balmond, Franco, Ruby, Hilda, Esmeralda, Silvanna
- **r3 Defender** — 2/4/6 — Tigreal, Bane, Minotaur, Gatotkaca, Khufra, Terizla
- **r4** unresolved — 2/4/6 — Alucard, Franco, Alpha, Martis, Leomord, Fredrinn
- **r5 Marksman** — 2/4/6 — Miya, Karrie, Irithel, Lesley, Granger, Brody
- **r6 Mage** — 2/4/6 — Kagura, Vexana, Odette, Lylia, Cecilion, Julian
- **r7** unresolved (an all-mage roster, distinct from r6) — 2/4/6 — Eudora, Aurora, Pharsa, Selena, Lunox, Luo Yi
- **r8 Assassin** — 2/4/6 — Saber, Helcurt, Gusion, Hanzo, Ling, Joy
- **r9** unresolved (dps 0, so likely a utility/economy class) — 2/3 — Angela, Claude, Phoveus
- **r10** unresolved — 2/3 — Clint, Fanny, Lancelot, Julian

## Faction synergies (relId 50-59)
- **r50** unresolved — 2/4/6/10 — Tigreal, Alpha, Irithel, Hanzo, Masha, Cecilion
- **r51 Dragon Altar / Dragoncaller** — 2/4/6/10, summons the **Dragon (id 179)** and scales its
  damage up hard at higher tiers — Saber, Kagura, Ruby, Granger, Yu Zhong, Phoveus
- **r52** unresolved — 2/4/6/10 — Miya, Alucard, Fanny, Claude, Khufra, Esmeralda
- **r53** unresolved — 2/4/6/10 — Minotaur, Hilda, Aurora, Odette, Helcurt, Martis
- **r54** unresolved — 2/4/6/10 — Balmond, Clint, Eudora, Gusion, Badang, Terizla
- **r55** unresolved (dps 0, likely a utility/economy faction) — 2/4/6/10 — Gatotkaca, Pharsa, Ling, Lylia, Brody, Fredrinn
- **r56** unresolved — 2/4/6/10 — Franco, Karrie, Lancelot, Angela, Lunox, Dyrroth
- **r57** unresolved (a death/undead theme, tentative) — 2/4 — Vexana, Selena, Leomord, Belerick
- **r58** unresolved (a summon/duel theme: data shows summon ids + red/blue team icons) — 2 only — Lesley, Silvanna, Julian
- **r59** unresolved — 2/3 — Bane, Luo Yi, Joy

## Reading notes
- Most class synergies have 6 members and full 2/4/6 ladders; r9/r10 are short (3 members, 2/3).
  Factions mostly run 2/4/6/10 (so a pure-faction board reaching 10 is a real win condition),
  but the small factions (r57/r58/r59) cap low.
- The `dps` numbers scale steeply with tier (e.g. r51 ramps to 40000 at tier 10) but are raw
  scaling values, not readable effects; the human-readable per-tier effects must come from an
  external MCGG reference or Kamil, not the current client dump. Marked unknown here, honestly.
- Comp-building target: cross faction *and* class breakpoints with the fewest slots. See
  [[heroes/index]] for who shares what, and [[abstract_generalization]] for why thresholds rule.
