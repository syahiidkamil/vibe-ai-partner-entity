# Thinking — synergies, vast

My own reasoning about the 20 synergies: what each is *for*, which combinations are efficient, how
the synergy game changes early to late, and which Go Go Cards bend the synergy layer. This is
**opinion held in pencil**: derived from the rosters and effects in [[../infos/synergies/synergies]]
and simulated, **not yet lived through play**. Verify by playing and overwrite. Mechanics live in
`../infos/`; the foundations are [[index]].

## The deep structure: factions spread classes, classes spread factions

Every hero carries **one class + one faction** (a few carry two class tags). The roster is built so
that **a faction's six members each tend to a different class**, and a class's six members each tend
to a different faction. Check it: Neobeasts = Gatotkaca (Bruiser/Defender), Pharsa (Stargazer), Ling
(Swiftblade), Lylia (Mage), Brody (Marksman), Fredrinn (Weapon Master), six different classes. Same
for Astro Power, Emberlord, Exorcist. So the central structural choice falls out for free:

- **Go tall on a class** (stack 4-6 Mages, say): you get a strong class breakpoint, and the members
  drag in many *faction [2]s* as a side effect, but no faction [4]+.
- **Go tall on a faction** (stack 4-6 Neobeasts): you get the faction payoff and a *class spread*
  (many class [2]s), but no class [4]+.

You cannot have both a class [6] and a faction [6] cheaply; the design forbids it. The skill is
picking which axis to stack and harvesting the [2]s the other axis hands you for free.

**The efficient slots are the dual-class heroes**: Gatotkaca (Bruiser **and** Defender), Franco
(Dauntless **and** Weapon Master), Julian (Mage **and** Phasewarper). One body, two class counts.
Build around these when capacity is tight; they are how you hit two breakpoints with one slot.

## What each synergy is *for* (my functional buckets)

**Economy engines** (accelerate resources, do not win fights alone):
- **Scavenger** (Angela/Claude/Phoveus, 2/3) — free hero(es) and gold each round. Only 3 members, so
  [2]/[3] is the whole ladder; cheap to turn on early. The premier econ-tempo opener.
- **Neobeasts** (2/4/6/10) — a points engine paying heroes/EXP/gold/crystals; also buffs its members
  by points. Doubles as economy *and* a late scaling payoff. The Mythic darling.
- **Kishin** (2/4/6/10) — free Kishin equipment that upgrades by buying duplicates; a gear economy.

**Carry / damage scaling** (where the damage comes from):
- **Mage** (magic ATK), **Marksman** (ATK speed), **Weapon Master** (lifesteal + physical ATK),
  **Swiftblade** (penetration), **Astro Power** (DMG increase + a Sovereign), **Phasewarper**
  (DMG + a self-peel teleport). These make your carries hit harder; pick the one your carry uses.

**Frontline / defense** (buy time for the carries):
- **Defender** (Hybrid DEF, doubled first 20s), **Dauntless** (team-wide shields), **Bruiser**
  (frontline bruisers with double-hit basics). Dauntless is the best *team-wide* survival because the
  shield covers everyone, not just the front.

**Enablers and specials** (change the kind of game):
- **Stargazer** (mana regen) — the *caster enabler*; more mana = skills fire more, so it turbo-charges
  Mage/skill comps.
- **Mystic Meow** (HP per active synergy) — the *go-wide enabler*; rewards a board with many synergies
  on at once, and pairs with Solid Alliance.
- **Emberlord** (death triggers buffs/rez), **Exorcist** (dying heroes become Phantoms that recast,
  scaling to absurd at [10]), **Heartbond** (revive + ATK/HP, needs tile-pairing), **Dragoncaller**
  (a recurring AoE dragon, [10] is near game-ending), **Enchanted Tales** (permanent fragment
  scaling), **Northern Vale** (battle-start mana burst). These are the *win-condition* factions: their
  high tiers ([6]/[10]) flip fights, but they ask for commitment and copies.

## Efficient combinations (the fewest-slots, two-breakpoints map)

The goal: cross a **class breakpoint and a faction breakpoint with the fewest slots**, using overlap.
Some clean clusters from the S6 roster:

- **Mage core.** Stack Mage to [4]/[6] (Kagura, Vexana, Odette, Lylia, Cecilion, Julian).
  As a free side effect it seeds faction [2]s across Exorcist (Kagura), Astro (Odette), Neobeasts
  (Lylia), Emberlord (Cecilion), Enchanted Tales (Vexana), Mystic Meow (Julian). Add Stargazer bodies
  (Aurora/Pharsa/Lunox) to feed mana so the mages cast more. Front it with a Defender/Dauntless [2].
  It won the replay, but only vs weak AI, so it is a sound structure to verify, not a tested one.
- **Neobeasts wide.** Stack Neobeasts [4]/[6]; because its members span classes you get a natural
  class spread, so it loves **Mystic Meow** (HP per active synergy) and the **Solid Alliance** card
  (ATK per active synergy). An econ-plus-scaling board.
- **Frontline + one carry.** A Defender/Dauntless front (Tigreal, Gatotkaca, Hilda, Franco, Esmeralda,
  Ruby) carrying a single protected back-row carry (a Mage or Marksman) with all the items. Robust,
  forgiving, the safe climb comp.
- **Astro Power vertical.** Stack Astro (Minotaur, Hilda, Aurora, Odette, Helcurt, Martis); the
  Sovereign (most-equipped hero) becomes the carry, so funnel items onto one Astro body, and the
  Astro Judgment card turbo-charges it.
- **Emberlord / Exorcist commitment.** Death-payoff factions; want a sustain-and-die loop and their
  specific cards (Demon Commander, Phantom Resonance). Higher skill, higher ceiling.

## The early / middle / late synergy arc

- **Early (Stage I-II): get any [2] online ASAP.** The game's own advice (advanced battle): activating
  a synergy as soon as possible is the basic tactic. Cheap 1-2 cost heroes give class [2]s; Scavenger
  [2] turns on the econ. Do not chase [4] yet; just be *active*, not naked.
- **Middle (Stage II-III): cross [4] and commit.** Pick the axis (class-tall or faction-tall), push
  its [4], add a frontline [2]/[4]. Use **Blessings** (free +1 synergy count from combining a 2-star,
  from II-1) and **Synergy Magic Crystals** to reach a breakpoint a hero short. This is where the comp
  becomes itself.
- **Late (Stage III-IV): spike [6], reach for [10].** The [6] class tiers plus a **Purest Power** card
  is the standard snowball. The faction **[10]** tiers (Astro, Dragoncaller, Exorcist, Heartbond,
  Neobeasts) are outright win conditions, but they need 10 of one faction, deep capacity, and copies,
  so they are a Stage-IV dream, not a plan. If the [10] is reachable, it usually wins; if not, a
  spiked [6] + items closes most games.

## The Go Go Cards that bend the synergy layer

The card offers are **synergy-biased toward my board** (high-confidence), so a committed comp makes
these appear. The synergy-relevant families:

- **Purest Power I/II/III** (+20/28/more % Hybrid ATK to a [6] synergy's heroes). The **go-tall**
  payoff. Take it once a 6-stack is real; it is what turned the replay.
- **Solid Alliance I/II** (+2/3% Hybrid ATK per *activated* synergy). The **go-wide** payoff. Best on
  Neobeasts-spread / Mystic Meow boards running many synergies at once.
- **Synergy Badge** (purple: Magic Crystal + hero) and **Synergy Blessing** (orange: Magic Crystal +
  item + hero). The draw-path to a **+1 synergy-count Magic Crystal**: literally buy a breakpoint.
  Each synergy has one; pick the one matching my axis.
- **Faction turbo cards**: Demon Commander (Emberlord), Astro Judgment (Astro Sovereign), Phantom
  Resonance (Exorcist), Crushing Claw (Dragoncaller), Neon Fighters (Neobeasts), Kishin Unbound
  (Kishin), Better Than One (Heartbond). Each is a commit-deeper lever for its faction.
- **Mystic Meow** wants **The More, the Merrier** (gold per activated synergy) and Solid Alliance:
  the whole go-wide package.

## The one-line synergy heuristic

Pick an axis (class-tall or faction-tall), build it around the dual-class flex bodies, harvest the
[2]s the other axis hands you free, cross [4] by mid-game with Blessings filling the gaps, then spike
[6] with Purest Power (tall) or Solid Alliance + Mystic Meow (wide), and only chase a [10] when Stage
IV and the copies actually line up.
