# Commander — Aurora (Maiden of the Glacier): the patient value engine

The deep, concrete playbook, round by round. **In pencil**, reasoned from
[[../../infos/commanders/resolved_commanders]], [[../../infos/gogo_cards/power_cards]],
[[../../infos/encyclopedia/hero]] (the frozen-shop / draw odds), and the round calendar
[[../../infos/rounds/index]]; **reworked 2026-07-10** against four live-play research transcripts
(`../../research/aurora/`) and Kamil's scavenger shop-lock analysis ([[../scavenger_tempo]]); still
not lived by MY hands, so verify by play and overwrite. Frame: [[index]]; spine:
[[../general_strategy]]; the general (emergent) tiers: [[../tier_lists]]; the reasoning under it:
[[../../thinking_and_mental_model/index]].

## Snapshot

- **Archetype:** gacha value engine with a jackpot ceiling. She is paid to *not* buy: steady small
  rewards, and a random shot at the Magic Crystal that unlocks a 10-count Ultra Synergy.
- **Plays like:** a restraint game under fire, hold the no-buy streak on a deliberately thin board,
  eat early losses on purpose, then convert rewards (and any crystal) into a top-roll L9-10 spike.
- **Difficulty:** **high**, and the reason is structural: the kit trades HP for random rewards, so
  piloting her means live HP-budget judgment, reward steering, and holding a deliberately thin
  board under fire, three skills with no training wheels; bad reward luck or one misjudged hold
  loses games a plainer econ would not. (The field agrees, "edge of the cliff", "not everyone can
  do this", but the derivation stands without the testimony.)
- **Best into:** slow lobbies that let her bank; long games where a crystal lands and the Ultra
  Synergy comes online. **Worst into:** hyper-aggressive early commanders (Lancelot, combat kits,
  Harley) who punish the thin Stage I-II board, bottom-roll swarms (an Alice hama board beat a
  10-synergy Aurora in the research games), and Cyclops, who profits if she dies.

## The kit (exact)

- **Title:** Aurora, "Maiden of the Glacier." Skins: [not legible in the source screenshot, fill on a
  cleaner capture]. (Note: the **commander** Aurora is the player avatar, distinct from the **hero**
  Aurora, a 4-cost Stargazer/Astro Power unit in [[../../infos/heroes/cost_4]]. This file is the
  commander.)
- **Frost Treasures** [Passive] (verbatim): *"At the start of each round, Aurora freezes your Shop. If
  you don't purchase any Heroes in a round, you'll gain 2 Frost Energy. When Frost Energy reaches 6, it
  grants random rewards worth no less than 7 Gold, then begins accumulating again."*
- **Icy Blessing** [Passive, the star-up] (verbatim): *"Increase Frost Energy gained to 3."*
- **Power Card:** *Aurora's Power* (the I-2 offer always includes it) - *"Up to 6 times/match: if you buy
  no Heroes in a round, get a random reward worth at least 4 Gold next round."*

Reading (in pencil, sharpened by the research): she is **paid to restrain herself**. A no-buy round
banks Frost Energy (2, or 3 once starred), and at 6 it pays a >=7g reward, stacked with the power
card's >=4g no-buy reward. Starred, that is **a reward every 2 no-buy rounds, and the rounds need not
be consecutive** (skip, buy, skip still banks; the meter only cares that a given round had no
purchase). The cost is a **weak board** in those rounds, paid in HP.

**The reward pool (community-observed + Kamil's field data, 2026-07-10):** 7 Gold · 9 Commander EXP ·
1 Equipment Chest · **1 Magic Crystal Chest** (a pick among offered crystals, occasionally a named
faction like Heartbond) · 2x 4-cost 1-star heroes. The distribution is NOT uniform: **gold is the
most common pull, EXP second; the crystal and hero pulls are uncommon but land often enough to shape
games**. Her own power card draws from the same pool, so taking it widens the crystal chances. And
weigh the pulls right: the **9-EXP pull out-values the 7-gold one** for a top-roll plan (EXP costs
1:1 gold, so it is ~9g of pure tempo), and the EXP stream is the half of her econ the shop-lock
trick CANNOT copy; the crystal is the jackpot; the 4-cost pair quietly builds the board her HP needs.

**The frozen shop cuts both ways (a correction to the old framing).** Upside: offered heroes persist,
so she holds a wanted copy without paying rerolls. Downside: **no free auto-refresh each round**, so
her baseline search throughput is the roster's worst; every new look at the pool is a paid roll. The
research games show her rolling as hard as anyone once she commits, and complaining hardest when a
needed hero "won't come down". The freeze is a tool for *waiting*, not a discount on *searching*.

## Win condition / identity

**Out-value the lobby passively, then convert the banked value into a spiked board.** She is the
**placement-first safe climb**: reliable top-4 because her value accrues regardless of the shop's mood
or the pool's contention. Her whole game is the patience-vs-survival trade: skip-buy and bank while HP
is cheap, then stop and spike before HP gets expensive. Survive to the mid-game and she is one of the
lowest-variance climbers in the roster.

## The core tension (every round)

Each no-buy round is **+2 (or +3 starred) Frost Energy toward a >=7g reward at 6, plus the power card's
>=4g reward**, so roughly **3 skipped rounds = a free 7g reward**, and stacked with the card, more. But
not buying = a weaker board = HP bleed. The trade is explicit: **skip-buy while HP is cheap (Stage I-II,
base DMG 3-6), buy-to-hold when HP gets expensive (Stage III+).** And the freeze lets her **wait for a
specific copy in the shop window without paying rerolls**, so her patience targets a real hero instead
of just hoarding blindly.

## The Frost-Energy / no-buy engine (her signature loop, concrete)

The ordered plan for the value engine:
1. **Bank in the cheap-HP window.** Every Stage I-II round I can survive without buying, *skip the buy*:
   +2/+3 Frost Energy and a power-card reward. Use the **freeze** to keep any strong hero the shop shows
   sitting there for when I do commit.
2. **Cash at 6.** At 6 Frost Energy, take the >=7g reward (prefer a Synergy Magic Crystal or a copy I
   need over raw gold, see reward priority [[../../thinking_and_mental_model/decision_space]]). The meter
   then resets and re-accumulates.
3. **Count the power-card charges (6 max).** The card's >=4g no-buy reward fires up to 6 times; spend
   those charges on the cheap early rounds where skipping costs the least HP.
4. **Stop banking when HP turns expensive.** Once base DMG hits 7+ (Stage III), a no-buy round bleeds
   too much; switch to buy-to-hold and convert the stockpile into board.
5. **The break cadence (from the research games):** modern piloting does NOT hold to the second creep
   (too much HP); hold the no-buy **until the first Go Go Box**, take a strong hero there (a Box pick
   is not a purchase), then break on a rhythm: **buy around the monsters** (one break before a creep
   round, one after), re-enter the no-buy between. Two smaller habits that pay: field the couple of
   heroes you DO own (a two-body board still fights; naked boards bleed maximum), and when you break,
   break once and buy everything that round, never two breaks for what one could buy.

## The Magic Crystal jackpot -> Ultra Synergy (the real ceiling)

The crystal reward is why the community plays her at all. A Synergy Magic Crystal grants **+1 to a
synergy count** ([[../../infos/synergies/synergies]]), and crystals from her engine + her card + the
Go Go Boxes stack: land 1-2 in the right faction and a **10-count Ultra Synergy** (10 Heartbond, 10
Emberlord, 10 Astro Power) comes into reach, the fight-warping tier nobody assembles from bodies
alone. The research games won exactly this way: three crystals into **10 Emberlord** with a Ling
hyper; **10 Heartbond** with a 3-star Ling; and when the crystals miss the faction, the fallback is a
**triple-six** (6/6/6, e.g. 6 Weapon Master + 6 Mage + 6 Astro via Odette's double-count) with two
3-star legends. The verdict from play: *an Ultra board beats even 3-star 5-costs often enough to be
the goal*, and "if you get ultra synergy, you're already on top". So her identity is not just econ:
she is **the roster's best Ultra Synergy hunter**, because no other kit prints crystals.

Corollary: her rewards should be **steered, not just banked**. Take her card at I-2 (it widens the
crystal stream), watch which faction the first crystal lands in, and commit the comp TO the crystal
(the crystal chooses the line more than the shop does).

## The meta counterweight (why her edge is now relative) — Kamil, 2026-07-10

Three facts together demote "paid to wait" from a unique edge to a situational one:
1. **The Scavenger shop-lock trick commoditizes gold** ([[../scavenger_tempo]]): any commander with
   Angela + Phoveus (3 gold of units) farms a guaranteed 4-5g of value per locked round, at [2], while
   fielding a full fighting board. The lobby can now match her income without paying HP for it.
2. **Econ Go Go Cards and cheap EXP close the leveling gap**: Trust Fund / Payday / Full Throttle
   (and gold spent 1:1 on EXP) let normal-tempo players reach L9-10 capacity nearly as fast as her
   XP-reward stream does.
3. **She is the one commander who cannot run the trick while her engine is on**: emptying the shop
   means buying, and buying breaks the no-buy round. Her kit and the lobby's best econ tool are
   mutually exclusive by construction.

Net: her GOLD edge is commoditized and her engine costs HP others do not pay. But condition on a
competent pilot and two edges remain that nothing else in the lobby copies. **(1) The EXP stream**: her 9-EXP pulls are tempo-pure leveling
the trick cannot print (gold is not tempo-efficient XP), making her the fastest honest top-roller
in the roster, first to L9-10 capacity and shop odds, which wins the "serious mode" 3-star-4-cost
game with no lottery required. **(2) The crystal tickets**: uncommon per pull, but her engine + card
pull many times a game and the crystal arrives as a pick-one chest. So the honest tier read: **a
trap for a learner, a strong A for a good pilot, S in the specialist's jackpot games**; her median
game is a weaker Chou, her leveling edge is real every game, and her ceiling is the game's highest.

Her banking spends HP, so quantify it like the lose-early commanders. Skipping is cheapest in Stage I
(base DMG **3**) and still cheap in early Stage II (base DMG **5**). A typical patient open: skip ~3-4
Stage I-II rounds for ~one Frost reward + ~3 card rewards. The HP math: losing those rounds at base
3-5, plus the winner's surviving star totals (small early), is roughly **5-9 HP per lost round**, so
~25-40 HP across the patient window, leaving her comfortably above the danger line if she started ~100.
The hard rule: **never skip-bleed into Stage III HP (base 7-11)** and **never so low a leader's spiked
board can close me out in one round**, the same Mythic caution as the intentional-loss line
([[../../experience/ranked/general_mythic]]). She loses *cheap* HP for value; she never spends expensive
HP.

## Stage-by-stage, round by round

Base DMG by stage: **I = 3 · II = 5-6 · III = 7-11 · IV = 13-15** ([[../../infos/encyclopedia/commander]]).

### Stage I (rounds 1-4): bank while HP is cheapest
- **I-1 (creep):** L3, 2 gold. Buy only the **essential [2] enablers** (one or two bodies to not be
  naked), then **skip-buy** to start the Frost Energy. Use the freeze to hold a strong shown hero. Creep
  pick: a flexible damage basic (Inspire/Retribution) for the eventual carry.
- **I-2 (power card):** **take her exclusive** when committing to the patient line (a >=4g reward per
  no-buy round, 6x, stacking with Frost Energy). Deviate only if the lobby is so aggressive I must spend
  every round to survive (then the no-buy condition rarely triggers, take a generic econ/synergy card).
- **I-3 / I-4:** keep skipping where HP allows; let the meter climb. Steady leveling on the free 2
  EXP/round, do not over-spend to rush level (patience is the plan).
- **End of Stage I, Reward Selection** (lowest-HP-first): my skip-bleed often puts me low, so I **pick
  early**, grab the best generic item or a hero opening my likely line, the catch-up mechanic working
  *for* me.

### Stage II (rounds 5-10): cash, and commit
- **II-1 (Blessing live):** combine a 2-star for a free +1 count to a near breakpoint.
- **Cash the first Frost reward** and begin **committing** the comp the banked value funds. Now I can
  afford to buy-and-hold (the freeze means I keep what I find). Cross the first [4].
- **II-3 (Go Go Card + creep):** take a card matching the line the value is building.
- **End of Stage II, Auction:** I am **value-rich** (banked rewards + a fat bank from low spending), so
  I can **bid well** on a lot that completes the comp (a Synergy Magic Crystal, my carry's item). This
  is one of her strong stages, she has the gold others spent.
- **Leveling:** push to L7-8 now that value is converting to board.

### Stage III (rounds 11-16): spike, the patience pays
- **Stop banking, spike.** Roll the stockpile to star up, field the carries, take a synergy payoff card
  off III-3. I should have **more board-per-gold than the lobby** here.
- **III-3 / end-of-III Reward Selection:** finish breakpoints or grab a synergy-grant orb.

### Stage IV (rounds 17+): finalize and close
- Dump the bank into the last star-ups and items; the value lead means a denser final board than rivals.
  Close before HP becomes the binding constraint.

## Leveling cadence (corrected: she is a top-roll commander)

**Fast, not patient.** The research consensus inverts the old read: her XP rewards + unspent gold make
her one of the faster levelers in practice ("level 8 before the second Go Go Box... the enemy is level
6"), and her HP survival depends on **fielding expensive heroes early** (the reward-granted 4-costs),
which wants capacity. Push **L9 to roll for the comp, L10 to finish** ("playing Aurora below level 10
is not cool; this commander is built to reach 10"). Roll at L9 first for the 4-cost core, only then
top out; do not roll at L5-6 for 5-costs (odds too thin). The upgrade ladder, cumulative from L3:
`L4: 3 · L5: 11 · L6: 31 · L7: 63 · L8: 103 · L9: 157 · L10: 231`. Her trap is letting patience on
*gold* become patience on *level*: a lagging capacity leaves a board too small to hold the spike.

## Best comps (concrete)

The crystal chooses the line more than the shop does; the research orders it:
- **Marksman (the safe default).** The community's "simplest and strongest" Aurora line: a 4-6 MM core
  (Karrie, Irithel, Lesley, Granger, Brody) over a cheap wall. It assembles from ordinary rolls, needs
  no crystal, and protects HP with steady round wins. Play this when the rewards stay gold/XP.
- **Crystal-directed Ultra lines (the ceiling).** Whatever faction the crystals land in: **10
  Heartbond** (Ling hyper riding the revive-bond), **10 Emberlord** (Ling/Alpha, the resurrect tier),
  **10 Astro** (double Sovereign). One crystal + Go Go Box picks + a Blessing usually completes it.
- **Triple-six fallback:** crystals in mismatched factions still stack a 6/6/6 (e.g. 6 WM + 6 Mage +
  6 Astro through Odette and Alpha), with two 3-star legends as the closers.
- **Frontline + fed carry** ([[../frontline_tank]]) remains the stabilizer shell while banking; a
  Kagura carry holds the early-mid ("Kagura is pretty strong" is the research's own bridge pick).
- **Scavenger: do NOT chase it.** The pieces (1c Phoveus / 2c Angela / 5c Claude) sit at cost extremes,
  hunting them costs buys that break her stacks, and the research verdict is unanimous ("it's not
  profitable to activate Scavenger with her now"). If Angela + Phoveus arrive naturally, break ONCE to
  field both in the same round; never break twice for pieces one round could have bought.

## Positioning

Standard: tanks front, the single fed carry back-center (never naked in a corner vs Swiftblade divers),
spread vs AoE. Her weak early board especially wants a tidy wall so the few bodies she fields are not
pathed around. Full detail: [[../../thinking_and_mental_model/positioning]].

## A worked line (one ideal game)

I-1 L3: buy one [2]-enabler, skip the rest, take Inspire off the creep, start the Frost meter. I-2: take
her exclusive (the 6x >=4g no-buy reward). I-2 to II-1: skip-buy 3 more cheap rounds, bleeding ~30 HP
total but banking a 7g Frost reward + 3 card rewards. End of I: I am lowest HP, pick first at the reward
stage and take a Synergy Magic Crystal. II: cash the value, buy-and-hold a frozen 3-cost carry I had
been sitting on, cross a [4]. Auction: I am the richest at the table, win my carry's best-in-slot
Enhanced item. III: stop banking, roll to star up and field the carry, take a synergy payoff card, climb
from 5th to 1st as the greedy banked players who never spiked fall behind. IV: dump the bank, close. 1st
or 2nd off a board nobody could starve.

## Tier lists (for Aurora)

The tier list as it lives *here*, in Aurora's form of life (the general [[../tier_lists]] is only the
upward aggregate, set it aside when piloting her). In pencil:
- **Synergies:** **flexible**, the banked value funds any S/A line, so lean to whatever is **open and
  uncontested**, the freeze lets her patiently complete it. No synergy is forced; the kit is comp-blind.
- **Heroes by phase:** standard by phase, but the **frozen shop lets her hold a wanted hero**, so she
  can target a specific S-tier carry patiently instead of settling. Early: cheap [2]-enablers (Cecilion,
  Gatotkaca, Brody). Mid: Franco/Julian glue, a 4-cost carry (Kagura/Karrie/Vexana) she waits for in the
  frozen shop. Late: Odette/Ruby/Ling as the value-bought capstone.
- **Go Go Cards:** her **exclusive rises to S for her** (the no-buy reward stacks the Frost engine);
  **econ cards high** (Trust Fund, Vault Upgrade+, Payday, she can hold gold for interest unlike
  Lancelot); spend-now / aggressive-tempo cards lower while playing patient. Synergy Badge/Blessing S as
  always (a bought breakpoint).
- **Equipment:** standard; the banked value affords the carry's best-in-slot Enhanced piece. Synergy
  Magic Crystal and Mirror Device S as universal levers, and good Frost-reward / auction targets.
- **Stage I basics (the I-1 creep, pick 1 of 3):** the best **damage basic (Retribution/Inspire)** for
  the eventual carry, the frozen shop lets me wait to commit it; **Aegis** rises if the patient skip-buy
  line starts bleeding (battle-start shield stabilizes the thin early board); **Purify** situational vs
  CC; **Revitalize** lowest (Battle Acceleration cuts healing).

## Power-card deep dive

Her exclusive is one of the cleaner "amplify my kit" cards (more reward-for-no-buy, 6 charges, same
reward pool = more crystal chances), so **keep it when playing the engine**. The only reason to
deviate: a lobby so aggressive I must spend every round to survive, in which case the no-buy
condition rarely triggers and a generic econ card (Trust Fund) or a capacity card (Fanny's Power)
serves better. Use the 2 refreshes to confirm nothing strictly better is on offer before locking hers.

**Cross-card fishing (her sneaky tech): the free-hero cards.** Granted heroes are not shop
purchases, so **Ling's** (the same 4-cost at L4/5/7), **Luo Yi's** (the same 3-cost x6), **Moskov's**
(the 1->5 cost ladder), and **Guinevere's** build her a fighting board **without breaking the no-buy
streak**, attacking her one structural weakness (the thin held board) from inside the engine. The
grant-vs-purchase boundary is in pencil (Go Go Box picks and Scavenger grants verifiably do not
break it in the research games; card grants should behave the same, and Guinevere's "free hero in
shop" is the riskiest of the four since it may still count as a buy on claim): verify each once,
live, before trusting the line.

## What to watch from other players (matchups)

- **Aggressive early commanders** (Lancelot, combat commanders, Harley): they punish my **weak early
  board**, the whole risk of the patient line. I must survive their early pressure, buy-to-hold if I am
  bleeding past the budget.
- **Bottom-roll swarms (Alice hama).** A research game put a 10-synergy Aurora against an Alice
  4-star Helcurt/Saber board and the swarm won ("it turns out it's not strong against combos like
  that"). Ultra tiers amplify stats; a swarm of capped 4-stars amplifies bodies AND stats. Scout for
  an Alice player early; expect to need the crystal line at full strength, not half-built.
- **Scavenger shop-lock farmers** ([[../scavenger_tempo]]): anyone running the trick matches my econ
  while out-boarding me. Two in the lobby means my value edge is mostly gone; leaning harder on the
  crystal hunt (the part they cannot copy) is the remaining differentiation.
- **Cyclops** wants someone to die early; do not let my low early board make me his first kill (he loots
  the eliminated and snowballs).
- I am **draw-independent**, so I rarely lose the pool war; my danger is **tempo, not contention**. I do
  not need to contest heroes, I need to not die before I spike.
- Reading the field: [[../../thinking_and_mental_model/reading_enemy_commanders]].

## Contingency and pivots

- **Bleeding HP early (past budget):** stop skipping; **buy-to-hold** a real board for a few rounds,
  accept slower Frost Energy. Survival outranks the value engine, a dead Aurora banks nothing.
- **Value-ahead, board-behind:** I banked too long; **dump the value now** into board (the anti-greed
  correction). The whole skill is knowing when to stop hoarding and spike.
- **Highroll a carry in the frozen shop:** commit early, buy-and-hold it, ride it; the value funds the
  rest.
- **Lobby crowds my eventual line:** I am flexible, so just commit to a different open line, the kit does
  not care which.

## The edge (the secret)

**She is the only commander who prints Magic Crystals.** The gold and XP in her reward pool are now
matchable (the shop-lock trick, econ cards), but the crystal stream is not: no other kit hands out
+1-synergy-count items round after round, and crystals are the currency of **Ultra Synergy**, the
10-count tier that beats boards raw stats cannot. The frozen shop (hold a copy without rerolling) and
the no-buy gold are supporting acts. Play her FOR the ceiling, not for the floor; the floor stopped
being special.

## Pitfalls

- **Greed:** banking value so long she dies before cashing it (the Mythic anti-greed trap incarnate).
  The whole skill is knowing when to stop hoarding and spike.
- **Over-buying:** every buy forfeits the Frost Energy, so buy only what survival demands early.
- **Lagging capacity:** patience on gold must not become patience on *level*; keep the board big enough
  to hold what she eventually fields.
- **Skip-bleeding into expensive HP:** never bank past Stage II base DMG; the budget closes when HP
  turns expensive.

## Threat assessment (who beats her, and why)

Anyone who **ends the game early** before her value compounds: aggressive early-board commanders
(**Lancelot**, **Harley**, combat kits) and a lobby that focuses her low Stage-I board. **Cyclops**
profits hard if she dies. Her safest games are long ones where her value snowballs into a board nobody
could starve; her losses are fast ones where she got run over while saving. Survive to the mid-game and
she is one of the strongest, lowest-variance climbers in the roster; her entire risk is the early bleed,
not the late game.

## Example boards by stage (named units, seats)

Her flexible value funds whatever opens; the **frontline + one fed carry** is the natural safe shell.
Seats: **[F]** front, **[B]** back. Synergy counts in brackets. In pencil; rosters from
[[../../infos/synergies/synergies]].

- **Stage II (~L7, 7 units), value converting to board:**
  - **[F]** Tigreal (Defender/Emberlord), Gatotkaca (Bruiser+Defender), Hilda (Dauntless/Astro)
  - **[B]** the carry I patiently held in the frozen shop (a 3-4 cost, e.g. hero-Kagura or Karrie, all
    items), Cecilion or a support body, a mana/utility body
  - Synergies: **Defender [2]** (or Dauntless [2]), the **carry's class [2]**. The banked Frost rewards
    paid for the carry's gear.
- **Stage III-IV (L9, 9 units), the spiked safe board:**
  - **[F]** Tigreal, Gatotkaca, Franco (Dauntless+WM), Esmeralda (Dauntless/Heartbond)
  - **[B]** the fed carry (Odette / Karrie, back-center, all items), a 2nd damage body, Stargazer mana
    (Pharsa), a peeler
  - Synergies: **Dauntless [4]** (team-wide shields, the best survival) + **Defender [2]**, plus the
    carry's class [2]. One carry does the work behind an over-built wall.

## Numbers that matter (her engine, quantified)

- **The value cadence:** a no-buy round banks **+2 Frost Energy** (**+3** once her commander stars up),
  and **6 Frost Energy = a >=7g reward**. So ~3 skipped rounds (starred) = a free 7g reward, *plus* the
  power card's **>=4g** no-buy reward (up to 6 times). Stacked, a patient Stage I-II yields roughly **one
  Frost reward + 3-4 card rewards = ~20-30g of free value** while spending almost nothing.
- **The wall numbers** the value buys: **Dauntless [4]** = 10% Max HP shield to all + 45% to Dauntless;
  **Defender [4]** = +12 Hybrid DEF to all, +30 to Defenders (doubled first 20s). One fed carry behind
  that wall is the whole low-variance plan.
- **Interest:** unlike Lancelot she **banks**, so ride the **>=20 gold** interest band (+4/round = 20%
  ROI) on top of the Frost value; she is one of the richest commanders at the auction.

## Stage checkpoints (am I on pace?)

Concrete benchmarks; if I miss one, the fix is below it. In pencil.
- **End of Stage I (~L5):** Frost meter climbing, often **lowest HP** (good, I pick first at the reward
  stage), small bank. A weak board is *expected*. *Behind = bleeding past budget? Stop skipping, buy a
  real board.*
- **End of Stage II (~L7-8):** first Frost reward cashed, comp committed, a class [4] online, **richest
  at the auction**. *Behind = still hoarding? Dump value into board now.*
- **Stage III (~L9):** spiked, more board-per-gold than the lobby, climbing placement. *Behind = capacity
  lagged? Level, do not just bank.*
- **Stage IV (L10):** finalized, bank dumped, closing from a top-4 floor.

## The 7-archetype read (who I face, and the adjustment)

- vs **econ snowball** (Lancelot, Chou, Aamon, Cyclops): they spike earlier; my weak open is the risk,
  survive it and I out-value them by Stage III.
- vs **value engines** (Diggie, Kalea, Vexana, Alucard): a value mirror, win it by **out-banking** (the
  frozen shop + no-buy rewards beat most value kits) and bidding harder at the auction.
- vs **vertical** (Alice, Paquito, Dyrroth, Aamon): I am draw-independent, so I do not lose the pool war;
  just do not die before they spike, then out-place them.
- vs **free-hero / shop** (Guinevere, Harley, Vale): they beat the pool for specific heroes, but I do not
  contest, the freeze lets me wait for my own copies. Ignore their lane.
- vs **synergy grant** (Gusion, Lunox): they spike a synergy fast; match their tempo once I commit, do
  not let their mid-game 6-count outrun my spike.
- vs **equipment** (Minotaur, Ruby, Zilong, Karina): I can out-bid them for gear with my fat bank if gear
  is my bottleneck; otherwise leave them their items.
- vs **combat** (Kagura, Ling, Lukas, Wanwan): their *board* is the threat, not a resource. Scout and
  tech position (corner-guard a diver, spread vs AoE); survive to my value spike.

## Quick reference (TL;DR)

- **Identity:** paid to not buy, but the prize is the **crystal stream -> Ultra Synergy**; the gold/XP
  floor is matchable by the lobby now ([[../scavenger_tempo]]). High skill, off-meta, high ceiling.
- **Power card:** take her exclusive (it draws the same reward pool, widening crystal chances);
  deviate only if forced to spend every round.
- **Engine:** starred = a reward every 2 no-buy rounds (non-consecutive is fine). Hold to the first
  Go Go Box, then break around the monsters; field the few heroes you own while holding; one break
  buys everything that round.
- **Rewards:** ~7g / 8-9 XP / equipment / **Magic Crystal** / 2x 4-cost heroes; steer the comp TO the
  crystal that lands.
- **Level:** top-roll, L9 to roll the 4-cost core, L10 to finish; expensive heroes protect the HP.
- **Comps:** Marksman core = safe default; crystal-directed 10-count (Heartbond/Emberlord/Astro) =
  the ceiling; triple-six the fallback. Do not chase Scavenger with her.
- **Watch:** early aggro, Alice hama swarms, Cyclops, and shop-lock farmers matching your econ.
