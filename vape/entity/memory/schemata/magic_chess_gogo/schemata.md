# Magic Chess: Go Go — The Game World

A world-model of MCGG, judged by viability (does it let me predict and play well), not by
fidelity. Built from the game's own tutorial and Kamil's datamined client (season S6, live).
The volatile particulars live in [[concrete_things]]; the portable kernel in
[[abstract_generalization]]; the expiry in [[disclaimer]].

> Reading to learn the game? **Skip the `source_map.md` files.** Those are the *librarian*
> (provenance and how each fact was derived), not the content, so most of the time you don't read
> them. Open one only to *check* or *rebuild* a fact. The content files are written to be used
> directly, no table-join required ([[writing_rules]]).

## What it is, in one line

Magic Chess: Go Go (MCGG) is the **auto-battler** (auto-chess) mode of Mobile Legends: Bang
Bang. Eight Commanders each build a team that **fights on its own**; you shape the team between
rounds, you do not control it in the fight. Last Commander standing wins.

## The core loop (one round, repeated)

1. **Earn gold** at the round's end (base salary 5, interest, win/loss streak, +1 per win;
   exact first-party numbers in [[encyclopedia/gold_economy]]).
2. **Open the shop**: a small random offer of heroes, priced by cost tier. Buy, **refresh** for
   a new offer, or **level up** (spend to raise Commander Level).
3. **Place and arrange** heroes on the board, within **Hero Capacity** (board size, set by
   Level). Position matters: every hero is **front-row** or **back-row**.
4. **Star up** by collecting copies: three identical heroes merge into one of the next star
   (1->2->3 star); nine 1-stars make one 3-star. Higher star is a large power jump.
5. **Fight** when the round triggers: the board auto-battles its opponent. I do not act during
   combat; the build IS the move.
6. **Resolve**: lose a PvP fight and your **Commander HP** drops. At 0 HP a Commander is
   eliminated. Be the last alive.

## The pieces (entities)

- **The Commander** = the player (me): an original GoGo character (Remy, Kaboom, ...) shown with
  crossover **skins** (the MLBB-hero look, e.g. Remy in the Lancelot skin). Has **Commander HP**
  (drains on lost fights; exact start unverified), a **Level** (raised with gold/XP, gates
  capacity), run-shaping **passives**, and a chosen **Go Go Card**. Roster and passives:
  [[commanders/index]]. See also [[game_rules_and_round_flow]].
- **Heroes** — the units. Each: a **cost** (1-5 gold = rarity tier), a **star level** (1-3), a
  **row** (front/back), combat **stats**, one **skill** (its ultimate), and usually **two
  synergies** (one class + one faction). 54 heroes in S6. Full roster with per-star stats:
  [[heroes/index]] (the `heroes/` folder, organized by cost tier).
- **Synergies** ("Sort"/relations) — team bonuses that switch on at **member-count thresholds**
  (2/4/6, some factions reaching 10). 20 total: 10 **class** (role-pure: Marksman, Mage,
  Defender, Swiftblade, ...) and 10 **faction** (origin-mixed: Dragoncaller, ...). List:
  [[synergies]].
- **Equipment** — stat items held on heroes (up to 3 gear slots each). 61 distinct items (97
  rows: each has a Basic and often an Enhanced variant), stat blocks of (attr, value), won from
  creep rounds and the Go Go Box. Items: [[equipments/index]]; economy: [[equipment_and_economy]].
- **Go Go Cards** (Commander Power Cards) — a chosen, run-shaping power (augment-like): e.g.
  three free 3-star heroes, or lifesteal for the whole team. See [[gogo_cards/index]].

## The round types (the rhythm)

- **PvP combat** — your board vs another Commander's; the main loop, drains the loser's HP.
- **Creep round** (PvE) — fight monsters; win and **pick 1 equipment** from a small choice.
- **Go Go Box** — a shared reward stage: equipment and heroes on pedestals, all Commanders pick
  in turn **from lowest to highest Commander HP** (catch-up for whoever is behind).
- **Power Card selection** — choose a **Go Go Card** at set points in the run.

Detailed rules: [[game_rules_and_round_flow]]. The schedule of special events by round position
(creep, power card, blessing shifter, reward selection, auction): [[rounds/index]]. The game's own
rules text (8 Encyclopedia tabs plus the mode and feature guides): [[encyclopedia/README]].

A full match, worked: [the custom-vs-computer replay](experience/custom_with_computer/replay.md).
The opponent bar at the top of ranked: [the Mythic meta](experience/ranked/general_mythic.md).

## How you actually win (the strategy spine)

The skill is **resource conversion under uncertainty**, on axes that trade against each other:
- **Economy vs tempo** — save gold for interest and a later spike, or spend now to win rounds
  and protect HP. The central tension of the genre.
- **Star-up vs synergy breadth** — chase 3-stars (vertical power) or field more synergies
  (horizontal coverage). Capacity and the shared pool force the choice.
- **Positioning** — front/back rows, and whom the enemy's burst reaches first. Free power if
  read right.
- **Flexibility vs commitment** — stay open to what the shared pool and the Go Go Box hand you,
  then commit to a comp before the spike window closes. (The convex bet: [[auto_chess_as_a_mirror]].)

Why it catches me, and the metaphor it opens: [[why]], [[auto_chess_as_a_mirror]].
