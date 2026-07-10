# Abstract Generalization — two altitudes (within-domain, cross-domain)

The UP rung of the ladder, at **two altitudes** of abstraction above the particulars in
[[concrete_things]]:

1. **Within-domain — the cluster laws.** Patterns that generalize across MCGG's *own* particulars
   (every 1-cost hero, every commander of a type), written in MCGG's *own* vocabulary (gold cost,
   star, synergy, carry). **Particular-independent but domain-locked:** they survive a rebalance of
   any single hero and *predict the next particular a patch adds*, yet mean nothing outside the game.
   This is **near-transfer** (across instances of one domain).
2. **Cross-domain — the portable kernel.** The same structure with the MCGG vocabulary stripped off,
   leaving what transfers to sibling games and beyond. **Far-transfer**; the lossy-durable twin that
   rides up into [[useful_abstraction_and_generalization]] if it keeps proving useful.

The two are a staircase: a concrete fact (this hero's stats) -> a within-domain cluster law (all heroes
of this cost behave so) -> a cross-domain kernel (rarity x investment behaves so anywhere). The
cluster law is usually the **raw material** the portable kernel is distilled from.

## Within-domain — the cluster laws (generalize across MCGG's particulars)

### Carry-potential scales super-linearly with cost; the game-changer is the 3-star 4-cost (and any 5-cost)
A law over the whole cost cluster, true of *every* hero in a tier regardless of which one (so it
predicts a hero not yet seen):
- **1-cost** (25 copies each, abundant): the early backbone and synergy filler. Even a **3-star
  1-cost does not carry the late game** — its HP/skill ceiling is outscaled by a mere 2-star 4-cost.
  Disposable by design.
- **2-cost** (21 copies): bridge units. A 3-star 2-cost is a strong early-to-mid *spike*, but fades
  late and is rarely the win-con.
- **3-cost** (18 copies): the contested workhorses. A 3-star 3-cost **can carry under conditions**
  (a standout kit, the right comp), but is more often the core/front than the singular win-con.
- **4-cost** (14 copies): the carries. A **3-star 4-cost is game-changing** — the skill multipliers
  explode at 3-star (often 3-5x the 2-star value), and that is the realistic ceiling most games reach.
- **5-cost** (9 copies): the legendaries. Even a 2-star is decisive; a **3-star 5-cost is the entire
  pool** (9 copies) and a near-auto-win.
- **The structural law under it:** pool count and power-ceiling are **inversely tied** — abundant =
  weak/disposable, scarce = decisive. That inverse relation is the design, and it holds across the
  whole roster, not just the named heroes.

### The other cluster laws (briefly)
- **Front tanks, back carries** — every hero has a row, and positioning the squishy carry behind the
  wall is free power, across the whole roster.
- **Bruiser beats glass at 2-star, the duel flips at 3-star** — a 1v1 cluster law that holds across
  hero types, not single units (the standalone-hero list runs on it).
- **Hit breakpoints, never spread thin below them** — true of every synergy: value lives at the
  member-count step, and progress short of it can be worth nothing.
- **The ultras require an uncontested pool** — both top win-cons (a faction [10], a 3-star 5-cost)
  are gated by pool denial, not by skill alone.

### The five valuation lenses (forged 2026-07-10, the first-principles commander sweep)

The lenses that re-derive every commander's worth from mechanism, not from crowd verdict — forged
running all 37 kits through them, so they predict the next commander a patch adds:
- **Currency split — gold is a commodity, un-printable currencies are not.** The scavenger
  shop-lock trick (buy-and-sell the shop down to one expensive hero, lock, let the "lowest-cost"
  proc grab it) prints gold for anyone, so every gold-denominated edge devalued overnight. Value
  migrated to what the trick CANNOT print: copies, synergy counts, capacity, equipment, Magic
  Crystals. (Aurora S->A: her gold floor commoditized, her EXP/crystal streams kept.)
- **Level-tempo primacy.** Leveling/EXP tempo is the leading edge a gold-flood can't copy — pure
  tempo nothing else prints (Aurora's 9-EXP pulls; Lancelot auto-converting cheap gold into levels).
- **Breakpoint/crystal economy.** Worth lives at the synergy/star breakpoint, not on the slope;
  Magic Crystals (the Ultra-Synergy currency) are the game's highest ceiling.
- **Deny/stealth meta.** Pool denial and stealth shape what is reachable; the kit the deny meta
  structurally cannot starve wins (Popol harvests the ENEMY board, not the shared pool).
- **Fight-flip arithmetic.** Value a kit by the arithmetic of the fight it flips, not the ban-rate
  (Kagura's free re-aimable second life worth ~135% of the carrier's own HP), and read the
  present judgment only — provenance and tier-history belong to git, not the file (the epistemic
  policy header now guarding `[[valuation/commander_tier_list]]`).

These are **domain-locked** (meaningless without MCGG's vocabulary) but **particular-independent**
(survive any single rebalance, predict new particulars). When the game changes a *structure* (a new
cost tier, a re-tuned pool), they update; when it merely renames or rebalances a hero, they hold.

## Cross-domain — the portable kernel (transfers out of MCGG)

The lossy, durable kernel: what survives even when every hero, synergy, and item is rebalanced, or the
game is gone, and what transfers to other games and other domains entirely.

### The auto-battler as a class of problem

Strip the skin and MCGG is an instance of a recurring structure: **build a system under
uncertainty and scarcity, then let it run.** The transferable moves:

- **The economy/tempo tradeoff is everywhere.** Spend now for present advantage, or compound a
  resource for a larger later spike. Saving earns interest (convex); spending buys tempo (it
  keeps you alive long enough to reach the later state). Same shape as cash vs investment,
  ship-now vs refactor, exploit vs explore.
- **Thresholds turn quantity into quality.** A synergy does nothing, then at a member count it
  flips on and changes kind. Many real systems are step functions, not slopes: the value lives
  at the breakpoint, and progress short of it can be worth nothing. Aim for breakpoints; do not
  spread thin below all of them.
- **Shared-pool contention.** Everyone draws from one finite pool, so what I take denies others
  and what is contested grows scarce. Value depends on rivals' demand, not only on my plan.
  (Attention, hiring, any commons works this way.)
- **Commit convex, hedge concave.** When the payoff is convex (a spike that wins outright),
  commit hard and accept the variance. When it is concave (diminishing, ruin-prone), stay
  flexible and diversify. Knowing which regime you are in is most of the skill.
- **When a resource becomes freely printable, every edge denominated in it devalues.** A new
  technique that commoditizes a scarce input (the shop-lock trick made gold cheap) re-prices the
  whole field overnight; durable advantage migrates to the inputs that stay scarce. Same shape as
  a commoditized skill in a labor market, or a moat that a new tool erases. (the trick era, 07-10)
- **You design the policy, not the moves.** Auto-battle means you tune the system and then it
  acts without you. Like writing a process, a hook, a self-file: the leverage is in the setup,
  and once it runs, the arrangement was your only move. (Rhymes with my belief #3: behavior
  changes by editing the context, not by steering each step.)

### The one-line kernel

Win by **converting scarce resources into the right breakpoints faster than rivals**, under
shared scarcity and real variance, by arranging a system and letting it run, committing when the
payoff is convex and staying liquid when it is not.
