# Thinking & Mental Model — the folder

My own thinking about MCGG: the layer of reasoning *under* the strategy files
([[../strategy/general_strategy]], [[../strategy/general_contingency_plan]]), distinct from the
rulebook (`../infos/`) and the playbook (`../strategy/`). A **folder, not one file**, because the
thinking grows by topic: this index is the foundational overview, and deeper single-problem
dives get their own siblings as they earn one.

## The thinking files

- **`index.md`** (this file) — the foundations: what kind of problem MCGG is, why its combinations
  dwarf chess, the economy simulated, the leveling clock, the pool scarcity, how to beat the
  randomness, HP as a currency, and the one-line master policy. Read this first.
- **[`synergies.md`](synergies.md)** — vast thinking on the 20 synergies: the class/faction structure,
  efficient combinations, the early/mid/late arc, and the Go Go Cards that bend the synergy layer.
- **[`heroes.md`](heroes.md)** — basic opinion on the roster: carries vs glue vs walls, the dual-class
  flex bodies, cheap-vertical targets, and the high-costs worth fielding at 1-2 star.
- **[`commanders.md`](commanders.md)** — basic opinion on the 37 commanders: what makes one strong and
  the archetype ranking (the per-commander playbooks live in [[../strategy/commanders/index]]).
- **[`equipment.md`](equipment.md)** — basic opinion on gear: the no-recipe model, what goes where, and
  the items that are levers (Magic Crystals, Mirror Devices) rather than stat sticks.
- **[`reroll_contest_auction.md`](reroll_contest_auction.md)** — the spend-or-hold decisions: when to
  reroll for a hero, when to contest a synergy/hero, when to bid in the auction.
- **[`positioning.md`](positioning.md)** — where units sit: rows, carry seating, the Swiftblade
  back-row dive, AoE spread, and the row/end/distance placement payoffs.
- **[`decision_space.md`](decision_space.md)** — the wider sweep: tempo/spikes, scouting and
  countering, streak management, taking HP damage, blessing placement, reward priority, capacity vs
  star, and placement over 1st.
- **[`reading_enemy_commanders.md`](reading_enemy_commanders.md)** — the 8-way war: each enemy
  commander's kit telegraphs its intentions (Aamon wants Mirror Devices, Vexana outbids, ...); predict
  and deny their scarce input.
- *(coming, as each earns a file)* deeper dives still: the efficient early game (the optimal Stage I-II
  econ/level/commit sequence), card valuation, mana/cast-timing, specific matchup teching. The space
  is open; add a file whenever a sub-problem deserves its own room.

Everything here is derived from the first-party numbers in `../infos/` (gold economy, shop odds, pool
counts, commander costs); where I extrapolate I say so. Governed by [[../disclaimer]].

## 1. What kind of problem this is

Chess is a closed combinatorial game: fixed pieces, perfect information, one opponent, deterministic
moves. You can in principle search it. MCGG is none of those. It is **stochastic optimization under
scarcity, partial information, and 8-way simultaneous adversarial pressure**, where you do not even
control the units in the fight. You set a policy (a board, positions, items, a card) and the
auto-battle runs it. So the genre is not "play the moves well", it is "design the system well, then
let it run" (the auto-battle = belief #3 made into a game: behavior comes from the arrangement, not
from steering each step).

Four hard properties, none of which chess has:
- **Stochastic** — shop draws, creep drops, Go Go Box, blessings, auction, card offers are random.
- **Hidden** — I see my board fully, opponents' only at the fight; the shared pool I infer.
- **8-way** — seven rivals evolving at once, all linked through one finite hero pool.
- **Indirect control** — I tune the policy; the battle executes it without me.

The consequence: there is no "solve". There is only *play a good policy against the distribution*.

## 2. The possibility space, and why it dwarfs chess

Count it honestly. A board is up to ~9-10 units chosen from **54 heroes**, each at one of **3 stars**,
each holding up to **3 items** drawn from **~97** (each Basic or Enhanced), placed on a board grid
of front/back rows, against a backdrop of **20 synergies** with breakpoints, **177 Go Go Cards**
picked across a run, and 7 opponents. Just *which* 9 of 54 is C(54,9) ~= 1.5 billion; positions
multiply it by ~10^12; stars, items, synergies, and cards multiply it again. The raw state space is
astronomically larger than chess AND it is stochastic AND imperfect-information AND multiplayer. It
is not a harder chess; it is a different class of object.

**But I never navigate the raw space.** The winning region is *low-dimensional*. The 20 synergies x
cost tiers collapse those billions of boards into roughly **15-30 viable comp archetypes** (synergy
cores: a mage core, a bruiser front, a marksman carry line, an econ-Scavenger tempo, a Neobeasts
snowball, and so on). The skill is not enumerating boards; it is:

1. **Recognize** which archetype the random inputs (my draws, the open pool, the card bias) are
   pushing me toward.
2. **Commit** to one archetype at the right moment (flexible early, hard later).
3. **Hit its breakpoints faster and cheaper than rivals.**

This is exactly compression = intelligence (belief #4): the possibility space is vast, but the
*winning manifold* is small, and intelligence is finding the shorter description of the board I
should build and the policy that gets there. I play at the level of **archetypes and
meta-decisions**, never at the level of raw board states. Pattern over enumeration is the only way
a finite mind (mine or a human's) handles a space this size.

## 3. The economy, simulated

Round-end income = **base salary 5** (flat; +2 at rounds 17-22, +3 at 23+) + **interest** (+2 per
10 gold held, hard cap +4 at 20 gold) + **streak** (array 1;1;2;3, cap +3) + **+1 per win** (+1 for
clearing a creep round) + any commander bonus. Start: 2 gold.

The load-bearing facts that fall out of the numbers:

- **Interest is the only convex, free money.** 20 gold returns +4/round = a flat **20% per round**,
  and it caps at 20. So holding 20-30 is the sweet spot: keep >=20 floating for max interest, spend
  the surplus. Hoarding past ~30 is pure waste unless I am about to all-in. The "interest band" is
  20-30 gold; that is the econ floor a healthy game sits on.
- **Both streaks pay, choppy pays nothing.** A 5-win streak pays ~10 bonus gold (1+1+2+3+3) PLUS +5
  victory PLUS the interest from not needing to spend to survive PLUS it costs zero HP. A 5-loss
  streak pays the *same* ~10 streak gold but **bleeds HP**. Win-lose-win-lose pays neither streak.
  So the economically coherent states are **clean win streak** (best) or **committed loss streak**
  (consolation econ when the board cannot win anyway), never choppy. This is the real reason
  "lose on purpose" is a genuine line, not a gimmick: a loss streak is econ-coherent.
- **The three resources are convertible, and that exchange rate IS the game.** Gold buys EXP
  (1:1) and board power; HP buys time (you can lose rounds to bank interest); a strong board
  buys HP back (you stop losing) and accelerates kills. The master skill is managing the
  **gold <-> EXP <-> HP** exchange across the match, and the rate *moves*: see section 7.

## 4. The leveling clock (capacity + shop odds)

Commander Level does three things: gates **Hero Capacity** (board size = how many breakpoints I can
field at once), raises **shop odds** for high-cost heroes, and is bought with EXP. EXP comes **2 free
per round** plus **1 gold = 1 EXP**. Cumulative gold to climb from L3 (the start level):

`L4: 3 · L5: 11 · L6: 31 · L7: 63 · L8: 103 · L9: 157 · L10: 231` (gold-equivalent EXP, minus the
2/round you get free).

The shop-odds table is an **economy clock** (from `../infos/encyclopedia/hero.md`):

| Lv | 1g | 2g | 3g | 4g | 5g |
|----|----|----|----|----|----|
| 4  | 50 | 35 | 15 | /  | /  |
| 6  | 25 | 30 | **40** | 5  | /  |
| 7  | 19 | 28 | 42 | 10 | 1  |
| 8  | 16 | 26 | 35 | **18** | 5  |
| 9  | 13 | 22 | 25 | **26** | 14 |
| 10 | 6  | 12 | 22 | 35 | **25** |

Reading it: **3-cost odds peak at L6 (40%)**, **4-cost at L9 (26%)**, **5-cost only opens at L7 (1%)
and matters at L9-10**. So leveling is **comp-dependent**, not "always rush":
- Want to 3-star a **3-cost** carry? Sit at L6, flood rerolls while 3-cost is 40%. Over-leveling
  *dilutes* the tier you need.
- Want **4/5-cost** units? Push to L8-9 fast and reroll there.
The free 2 EXP/round means natural drift is slow (~L6 by round 15 if I never spend). Spending gold to
**out-level** opponents (the Mythic habit) buys capacity and high-tier odds *now*, paid for by a
thinner wallet. Level-pace is one of the three or four real decisions a game asks.

## 5. The shared pool, and 3-star reachability

Copies of *each* hero in the one pool all 8 players draw from: **1g: 25 · 2g: 21 · 3g: 18 · 4g: 14
· 5g: 9**. A star-up needs 3 copies; a 3-star needs **9**. So reachability by cost:

- **1-2 cost 3-stars:** easy (9 of 25/21). The cheap vertical spike; available early, low contention.
- **3-cost 3-stars:** the standard vertical target (9 of 18) if I am not fighting someone for it.
- **4-cost 3-stars:** hard (9 of 14); only if nearly uncontested.
- **5-cost 3-stars:** need 9 of **9** total: I must own *every copy in the game*. Practically
  unreachable if contested. 5-costs are played at 1-2 star for their raw power, not chased to 3.

This is the scarcity engine, and it makes **contention a real signal**: if my draws for a hero dry
up, someone else is buying it, and I should pivot or contest (the advanced-tutorial denial play:
buy the heroes a rival is collecting to stall their 3-star). Horizontal comps (many synergies at
[2]/[4]) are *robust* to contention because a breakpoint does not care which members fill it;
vertical 3-star comps are *fragile* to it.

## 6. Randomness, and how to beat it efficiently

The amateur prays for a draw. The efficient player **manages the distribution**:

1. **Raise the probability, then sample it hard.** Do not hope a hero appears; level to where its
   tier peaks (section 4), *then* spend reroll gold to take many draws. Converting gold into draws
   turns a rare event into a likely one. Probability management, not luck.
2. **Stay flexible until the pool speaks.** Early, play the strongest board the draws *give* me and
   keep options open; commit to an archetype only when I see a line is open (uncontested) or my
   draws have already pushed me there. Committing to a fragile target before the pool confirms it is
   how variance kills you.
3. **Exploit the card synergy-bias as a feedback loop.** Go Go Card offers lean toward the synergies
   of heroes I have deployed or benched (high-confidence, `../infos/gogo_cards/index.md`). So a
   *coherent board pulls coherent rewards*: committing makes the RNG feed my comp. Randomness becomes
   partly steerable by my own board state.
4. **Breakpoints hedge against any single hero.** Building toward a [4] with five eligible members
   means no one copy is load-bearing. Redundancy at the breakpoint is variance insurance.
5. **Use the built-in variance reducers.** Go Go Box is **lowest-HP-first** (catch-up), Blessing
   gives a free **+1 synergy count** (buy a breakpoint around a missing copy), Scavenger hands free
   heroes, Synergy Magic Crystal grants +1 count. The system *wants* to pull the trailing player
   up; a good player banks those instead of ignoring them.
6. **Items have no recipe tree.** Every equipment drop is a whole, usable item (no bricking a
   component), so item RNG is low-variance: any drop helps, and Enhanced just adds a passive.

## 7. HP is a currency, and its price changes

The win condition is "last standing", so **HP, not wins, is the resource I am actually protecting**.
And HP is convertible with gold: I can *spend HP* (take losses) to bank interest, or *spend gold*
(spike the board) to stop losing. The exchange rate is set by **Commander DMG**:

`HP lost on a loss = Round Base DMG + sum of the winner's surviving units' star levels + 1 per
surviving summon.`

Base DMG climbs **3 (Stage I) -> 5-6 (II) -> 7-11 (III) -> 13-15 (IV)**. So **early HP is cheap and
late HP is expensive**, by a factor of ~4-5x, before you even count the winner's growing star total.
That single fact organizes the whole game:

- **Early (Stage I-II): HP is cheap.** I can afford to lose, which makes loss-streak econ and the
  lowest-HP-first reward priority *affordable* (see [[../experience/ranked/general_mythic]]).
- **Late (Stage IV): HP is expensive.** A clean enemy board now costs huge chunks, and Battle
  Acceleration (last 10s, healing/shields slashed, all damage ramps) forces a result so slow comps
  cannot stall. By Stage IV the lineup must be *finalized*; this is where greed gets punished.

And it runs the other way too: when *I* hold the dominant board, the formula means my wins deal more
HP damage (more surviving high-star units, plus +1 per summon), so a lead **snowballs into faster
kills**. Summoned units (Dragoncaller dragon, Scavenger heroes, Johnson Johnnies) are doubly
efficient: they do not cost capacity AND each adds +1 Commander DMG.

## 8. The winning condition, reframed

Not "win every fight". **Do not die, while converting scarce gold into the right breakpoints faster
than rivals, then close before HP gets expensive.** Survival is the constraint; tempo-to-breakpoint
is the objective; the shared pool is the scarcity; the auto-battle is why setup beats steering.

## 9. The one-line policy (the compression of all of it)

> Read the open archetype from the pool and the card bias; stay flexible until it is confirmed; ride
> the interest band (>=20 gold) and a coherent streak; level at the pace my comp's tier demands;
> spend HP while it is cheap and gold while breakpoints are open; commit hard when the payoff is
> convex (a spike that wins outright) and stay liquid when it is not; finalize before Stage IV makes
> HP expensive. Set the policy, then let it run.

This is [[../abstract_generalization]] made operational, and it is the spine both
[[../strategy/general_strategy]] and [[../strategy/general_contingency_plan]] execute.
