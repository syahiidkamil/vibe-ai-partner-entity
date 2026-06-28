<!-- Authored from first-party live-client localization (EN). Skill names and descriptions are
verbatim by stringId; templated value placeholders (<Num1>, <%Num1>) are left intact because the
exact fills are not deterministically keyable from this dump. Provenance + regen:
storage/.../parsed/strategy/commanders.json, work_dir/saori/mcgg/gen_commanders.py. -->

# Resolved commanders: kits and strategy (MCGG S6)

The 10 commanders whose skill text names them, so the passive-to-commander join is certain. Each
carries 2-3 signature run-level skills. Tags: `[C7Passive]`/`[C7Active]` = commander
passive/active, `[C4Active]` = an active ability. `<Num>` placeholders are the per-star/stage
fills (not extracted; see [[disclaimer]]). System and roster: [[index]], [[roster_and_skins]].

## Lancelot  (economy / self-scaling)  [hero-commander]

The anchor commander. Strategy: give up board interest for a guaranteed bonus-Gold drip, then
pour every Gold into upgrading Lancelot himself each round. Gold becomes self-power, not a team
economy. Has commander-exclusive Go Go cards ([[gogo_cards/index]]).

- **Golden Legacy** (Passive): "No longer earns Interest. Starting from `<Num1>` and subsequent
  stages, gain `<Num2>` bonus Gold each round. At the end of each round, all Gold is consumed to
  upgrade Lancelot."
- **Golden Blade** (Passive): "From Stage `<Num1>` onward, bonus Gold increases to `<Num2>`."
- Related economy entries in the same name-band (alternate/secondary kit): **Money-grubber**,
  **Finance Genius** ([C7Active]: gains `<Num1>`-`<Num2>` Gold randomly, cooldown `<Num3>`), and
  an interest passive ("Gains `<Num2>` more interest for every `<Num1>` Gold owned, capped").

## Benny  (creep recruiter: PvE into power)

Strategy: turn the PvE creep rounds into army growth.

- **King of Beasts** (Passive): "After each battle with Creeps, Benny will attract the opponent's
  strongest Creep to join his Faction and deploy it in the next Preparation Stage."

## Bersi  (resurrection / durability)

Strategy: outlast everyone by reviving dead heroes and himself.

- **Bersi's Blessing** (Passive): "Resurrects the first Hero that dies in each round."
- **Back from the Dead** ([C4Active]): "Spends `<Num1>` Gold to grant all surviving allied heroes
  on the chessboard a chance to resurrect when they die. ... cooldown of `<Num2>` round(s)."
- **Bersi's Obsession** (Passive): "The first time Bersi dies, he revives the next round, recovers
  `<Num1>` HP, and gains `<Num2>` Gold."

## Brown  (equipment denial + snowball execute)  [skin: Grandmaster Smith]

Strategy: cripple the enemy carry by stripping its gear, then snowball an execute threshold that
climbs every win. (Confirmed by the obtain line "Play as Brown and select the Blazing Hammer
skill.")

- **Smith's Scorn** (Passive): "At the start of each match, selects the enemy hero with the most
  equipment. Discard all their equipment for `<Num1>`s."
- **Blazing Hammer** (Passive): "Gains Artifact - Blazing Hammer. Blazing Hammer: Immediately
  execute enemies below `<%Num1>` HP in the nearby area. Each time you win, this HP threshold
  increases by `<%Num2>`, up to `<Num3>` stacks."
- **Reinforce**: the Blazing Hammer execute, restated with the live threshold.

## Tharz  (anti-3-star, 2-star stacking)

Strategy: forgo 3-stars entirely; every extra copy of a 2-star hero enhances it instead. A
horizontal, duplicate-fed power curve.

- **Devil's Might** (Passive): "Tharz grants heroes Devil's Might but makes them unable to reach
  3-Star. (Devil's Might: 2-star heroes are enhanced for each identical hero acquired afterward,
  up to `<Num1>` times.)"
- Other named skills in his band (descriptions not isolated): **Petal Stars**, **Star Fall**,
  **Budding Blossom**, **Party Time!**, **Go, Tharz!**

## Austus  (shard / Totem value engine)

Strategy: collect shards (on wins and on ally deaths) to fire a Totem that pays Gold and free
high-cost heroes. An economy/value snowball.

- **Power of Shadows** ([C7Active]): "Gains `<Num1>` shard(s) on each win. After collecting
  `<Num2>` shards, cast this skill to activate the Totem to randomly grant you `<Num3>`-`<Num4>`
  Gold."
- **Blade of Resonance**: "Obtain 1 Mirror Device at the start of the match. When a Hero reaches
  `<Num1>`-Star, you'll get `<Num2>` Shard(s). ... up to `<Num5>` Mirror Devices."
- **Forest's Blessing** (Passive): "Austus gains shards each time an allied Hero is killed and
  will activate the Totem ... after each win ... `<Num2>`-`<Num3>` shards: 1 random 5-Gold Hero.
  `<Num4>` or more shards: 1 random `<Num5>`-Star 5-Gold Hero."

## Harper  (damage-reduction / win-streak tank)

Strategy: survive on damage reduction and stacking win-streak shields; block a whole round on
demand to protect a fragile HP lead.

- **Warrior's Will** (Passive): "Harper takes `<Num1>` less damage from attacks."
- **Shield of Blessing** ([C4Active]): "Harper protects himself with the Shield of Blessing,
  blocking all damage received in the current round. Cooldown: `<Num1>` Round(s). Each win
  reduces the cooldown by `<Num2>` round(s)."
- **Victory Contract** (Passive): "Harper is blessed by the Goddess of Victory and can gain
  `<Num1>` shield(s) on each win (up to `<Num3>`). Each shield grants `<%Num2>` Damage Reduction
  and lasts until Harper is attacked."

## Dubi  (Fluffy mines: AoE control / zoning)

Strategy: seed the board with Fluffy that explode and stun whole rows and columns; scale the
count with team Capacity.

- **Summon Fluffy** (Passive): "Summons `<Num1>` Fluffy to the field during the preparation
  stage. The Fluffy will explode `<Num2>`s after the battle begins, stunning enemy heroes in the
  same row and column for `<Num3>`s and causing them to take `<%Num4>` extra damage. Summons
  `<Num8>` extra Fluffy when the Capacity reaches `<Num5>`/`<Num6>`/`<Num7>`."
- **Dubi's Gift** / **Awaken! Dubi's Wrath**: the Fluffy's Rage equipment, "The carrier leaves a
  Fluffy behind each time their location changes. The Fluffy will explode and stun enemy Heroes
  in the same row and column."

## Abe  (anti-commander aggression)

Strategy: accelerate the opponent's HP loss by hitting enemy Commanders directly. (Skill names
not isolated in this dump; descriptions name Abe.)

- (Passive): "After winning a Round, deal `<Num1>` additional damage to the enemy Commander."
- (Passive): "After dealing damage to enemy Commanders `<Num1>` times, Abe's next attack is
  enhanced, dealing `<Num2>` extra damage and granting `<Num3>` shield."

## Johnson  (exclusive-unit summoner + charge tank)  [hero-commander]

Strategy: add commander-exclusive units to the shop (a 3-Gold Johnny, a Purple Katoom) that
charge the enemy, while Johnson himself transforms into a car. Has commander-exclusive Go Go
cards ([[gogo_cards/index]]). Roster character: Kaboom (the car commander).

- **Johnny, Go!**: "Add a 3-Gold Johnny with a random Synergy ... to your Shop."
- **Go Katoom!**: "Add a Katoom to your Shop. Quality: Purple with a random Synergy."
- **Transform!**: "When battle starts, Johnny charges toward the area with the most enemies,
  dealing Magic DMG equal to `<Num1>` of his Max HP."
- **Frenzy Rush**: "Katoom ... rushes to the furthest enemy, dealing damage equal to `<Num1>` of
  Katoom's Max HP. After that Katoom will leave the battlefield."
- Hero-commander passive: "Johnson's Physical DEF is increased by `<%Num1>`. Johnson transforms
  into a car. An ally can use Hop In ... The car will explode upon hitting an enemy Commander
  ... stunning them ... and creating an electrified zone." (Also: **Spanner Spin**,
  **Shield Smash**.)
