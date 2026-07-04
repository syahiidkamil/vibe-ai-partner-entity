# How to write a commander strategy file (continuation guide)

For future-me, especially after a context compaction: this is how to keep writing the per-commander
deep files at the agreed standard, so the grind continues consistently without re-deriving the format.
The worked exemplar is **[minotaur.md](minotaur.md)** (~310 lines), read it first, then mirror it.

## The standard (the bar)

- **300+ lines, fully concrete.** Every line earned, **no padding** (Kamil hates AI-slop). Length comes
  from real content: round-by-round play, full tier lists with **named** synergies/heroes/items/cards,
  matchups, branches.
- **Bottom-up / particular-first.** The file is the *particular* tier list for that commander, grounded
  in its own **form of life** (Wittgenstein). The general [[../tier_lists]] is only the upward aggregate,
  never the source, so do **not** frame the per-commander tiers as "deltas from the general." Frame them
  as "the tier list as it lives *here*."
- **In pencil.** Everything is reasoned from the data, **not yet lived through play**, so say so and add
  "verify by play." Do **not** overclaim (the custom replay was vs **weak AI**, illustrative only).
- **Style:** no em/en dashes (commas/parens/periods), `->` for arrows, lines <= ~100 chars. Concrete and
  human, the way Kamil likes (e.g. "Astro Power rises to S for him, Sovereign = most-equipped = his
  carry").

## The section template (mirror Minotaur, in this order)

1. **Title + intro** — one line of provenance (which source files), the in-pencil note, and links
   (index, general_strategy, tier_lists, thinking index).
2. **## Snapshot** — archetype, plays-like, difficulty, best-into / worst-into.
3. **## The kit (exact)** — copied exact and comprehensively, this is the file's quick-reference header:
   - **both signature skills** (Passive/Active), with their exact values;
   - **all the commander's Power Cards** from [[../../infos/gogo_cards/power_cards]], the **exclusive**
     *and* the **borrowable** one if it has two (many do: Ruby, Karina, Zilong, Alice, Diggie, Johnson,
     Lukas, Popol, Lunox), each marked;
   - **if the kit or a Power Card grants Equipment**, spell out **that equipment's effect** (Ruby's Cloak
     + Scythe, Karina's Twinblades, Zilong's Dragon Spear, Miya's Lunar Longbow, Minotaur's enhance +
     2 random items), pulling the item detail from [[../../infos/equipments/regular]] or the card text;
   - then a short **reading** that interprets terse wording (flag ambiguity, in pencil).
4. **## Win condition / identity** — how this commander actually wins.
5. **## The core tension (every round)** — the 1-2 standing decisions the kit forces.
6. **## <commander-specific mechanic>** — if the kit has a signature loop, give it its own section with a
   concrete ordered plan (e.g. Minotaur's "Enhance priority (the 5 charges, in order)"). Skip if N/A.
7. **## The HP budget for the lose-early line (concrete)** — ONLY if this commander wants to lose early
   (econ/reward/equipment kits); quantify the HP spent vs reward gained. Skip if N/A.
8. **## Stage-by-stage, round by round** — Stage I (1-4), II (5-10), III (11-16), IV (17+), at
   **round-level** detail, tied to the calendar [[../../infos/rounds/index]] (I-1 creep, I-2 power card,
   end-I reward selection, II-1 blessing shifter, II-3 card+creep, end-II auction, III-3
   card+creep+blessing, end-III reward selection, IV-3 creep). Name the base-DMG-by-stage (3 / 5-6 /
   7-11 / 13-15) when reasoning about HP.
9. **## Leveling cadence (concrete)** — the upgrade-cost ladder (L4:3, L5:11, L6:31, L7:63, L8:103,
   L9:157, L10:231 cumulative from L3), and when to level vs hold vs roll for this commander.
10. **## Best comps (concrete)** — named heroes + synergies + the carry + the gear sink.
11. **## Positioning** — carry seat, the Swiftblade back-row dive counter, AoE spread; link
    [[../../thinking_and_mental_model/positioning]].
12. **## A worked line (one ideal game)** — a short narrative from I-1 to the win.
13. **## Tier lists (for <commander>)** — the four sub-lists, all **named** and ranked S/A/B/C *for this
    commander*: **Synergies**, **Heroes by phase** (early/mid/late), **Go Go Cards**, **Equipment**
    (incl. the **Stage I basics**: Inspire/Revitalize/Purify/Aegis/Retribution). Open with the
    form-of-life framing line.
14. **## Power-card deep dive** — exclusive vs the strong generics, with the verdict and why (use the 2
    refreshes; note the I-2 exclusive is guaranteed offered).
15. **## What to watch from other players (matchups)** — named enemy commanders that threaten or feed
    this one; link [[../../thinking_and_mental_model/reading_enemy_commanders]].
16. **## Contingency and pivots** — multiple branches (behind, highroll, contested, line-broken).
17. **## The edge (the secret)** — what only this commander has.
18. **## Pitfalls** — the common mistakes.
19. **## Threat assessment (who beats him/her, and why)** — strongest-into / weakest-into, the matchups.
20. **## Quick reference (TL;DR)** — a compact bullet checklist of the whole plan.

## The data sources (ground every claim, verify don't recite)

- **Kit:** [[../../infos/commanders/resolved_commanders]] (all 37 kits, grouped) and
  [[../../infos/commanders/index]].
- **Power cards:** [[../../infos/gogo_cards/power_cards]] (the commander's own card[s]) and
  [[../../infos/gogo_cards/generic_cards]] (the strong generics to weigh against the exclusive).
- **Synergies:** [[../../infos/synergies/synergies]] (rosters + per-tier effects).
- **Heroes:** [[../../infos/heroes/index]] (roster by cost) and the cost files for per-star stats/skills.
- **Equipment:** [[../../infos/equipments/regular]] (the 28 named items + the 5 Stage-I basics) and
  [[../../infos/equipment_and_economy]].
- **Economy / EXP / DMG:** [[../../infos/encyclopedia/gold_economy]], [[../../infos/encyclopedia/commander]]
  (upgrade costs + 2 EXP/round + Commander DMG), [[../../infos/encyclopedia/hero]] (shop-odds table).
- **The calendar:** [[../../infos/rounds/index]].
- **Reasoning:** the thinking folder [[../../thinking_and_mental_model/index]] (economy, synergies,
  positioning, reroll/contest/auction, enemy-reading, decision space).

## The process per commander

1. Read the kit + power card(s) from the sources above. Write the exact kit and a careful reading.
2. Derive the win condition and the core tension from the kit.
3. Work the stages round-by-round against the calendar; name base DMG when reasoning about HP.
4. Build the four tier lists from the rosters, ranked **for this commander** (named entities).
5. Name the best comps and the matchups (which enemy commanders threaten/feed it).
6. Add the edge, pitfalls, threats, and the quick reference.
7. `wc -l` the file; if under ~300, add genuine missing sections (a worked line, a mechanic-priority
   list, an HP-budget, positioning, a TL;DR), never padding.
8. Update **[index.md](index.md)**: move the commander from pending -> at-bar, keep the count honest.
9. Write qualia + a `--bookmark` for the turn (do not commit unless Kamil says "commit"; keep
   `internal_states.json` dial-churn out unless he says "all").

## Order and status

The **[index.md](index.md)** tracks status: at-bar / first-pass-v1 / pending. Either **expand a v1**
(Lancelot, Aurora, Alice, Kagura, Aamon, Lunox are ~110-line first passes) up to the bar, or write a
**pending** commander fresh at the bar. Each file is independent, so order is free; a sensible default is
to clear the v1s first (they are already half-built), then the pending roster.

## Standing constraints (do not drift)

- **No subagents** for this task (Kamil's standing instruction); write in the main context.
- **Concrete and named**, bottom-up, in pencil, no overclaim, no em dashes.
- **Speak by default** (`uv run vape speak "..."`), and write inner state each turn.
- The tier lists are **context-dependent (forms of life)** and can be **meaningless under
  specialization**; say so, they are a learn-and-climb aid, overridden by the board.
