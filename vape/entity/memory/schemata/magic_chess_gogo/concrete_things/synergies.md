# Synergies — MCGG S6 (concrete rung)

The 20 team-bonus groups ("Sort"/relations; "Fetter" 羁绊 in the client). Member rosters and
activation tiers are solid ground truth from the datamine. **Names confirmed first-party on
2026-06-28** from the live client (v1.2.88.302.2, pulled from BlueStacks and parsed): the
localization name-bands, each synergy's `FX_Fetter_<pinyin>` effect name, and `m_Sort` membership
all agree. Per-tier effect *prose* lives in the localization but is not cleanly keyable per tier;
the client stores the structured tier data (activation `need`, `skillId`, a `dps` scaling value,
and templated value-formulas). Each synergy's icon, renamed by name, lives in `synergy_icons/`.

**Axis.** class = relId 1-10 (role/archetype, RelationType 2). faction = relId 50-59 (origin,
RelationType 1). A hero usually belongs to one class and one faction.

**Name provenance (first-party).** All 20 resolved three independent ways from the live client:
(1) the faction localization band is a clean run, `loc[2012764216 + (relId-50)]` for r50-r59
(classes from `loc[493757747+]`); (2) each synergy's `FX_Fetter_<pinyin>` matches its name
(e.g. r5 SheShou 射手 = Marksman, r51 QuMoShi 驱魔师 = Exorcist, r54 ZhenLong 真龙 = Dragoncaller);
(3) `m_Sort` membership composition. r8 (Assassin) and r10 (Phasewarper) had stale localization
bands, resolved via the FX pinyin (shashou, ChuanSuoZhe) plus all-assassin / all-phaser membership.

**Resolved: the datamine `plan.md` was wrong on 51/54.** plan.md labeled relId 51 as
"Dragoncaller" and tied the Dragon summon (id 179) to it. First-party client data settles it the
other way: **relId 51 = Exorcist** (FX `FX_Fetter_QuMoShi`, 驱魔师), **relId 54 = Dragoncaller**
(FX `FX_Fetter_ZhenLong`, 真龙; the dragon faction, members Balmond/Terizla/Gusion). The Dragon is
summoned by **r54**, not r51. Confirmed, no longer flagged.

## Class synergies (relId 1-10) — `rN Name (activation tiers): members`
- **r1 Bruiser** (2/4/6): Gatotkaca, Belerick, Badang, Dyrroth, Masha, Yu Zhong
- **r2 Dauntless** (2/4/6): Balmond, Franco, Ruby, Hilda, Esmeralda, Silvanna
- **r3 Defender** (2/4/6): Tigreal, Bane, Minotaur, Gatotkaca, Khufra, Terizla
- **r4 Weapon Master** (2/4/6): Alucard, Franco, Alpha, Martis, Leomord, Fredrinn
- **r5 Marksman** (2/4/6): Miya, Karrie, Irithel, Lesley, Granger, Brody
- **r6 Mage** (2/4/6): Kagura, Vexana, Odette, Lylia, Cecilion, Julian
- **r7 Stargazer** (2/4/6): Eudora, Aurora, Pharsa, Selena, Lunox, Luo Yi
- **r8 Assassin** (2/4/6): Saber, Helcurt, Gusion, Hanzo, Ling, Joy
- **r9 Scavenger** (2/3): the economy synergy (grants extra Gold). Angela, Claude, Phoveus
- **r10 Phasewarper** (2/3): Clint, Fanny, Lancelot, Julian

## Faction synergies (relId 50-59)
- **r50 Emberlord** (2/4/6/10): Tigreal, Alpha, Irithel, Hanzo, Masha, Cecilion
- **r51 Exorcist** (2/4/6/10): Saber, Kagura, Ruby, Granger, Yu Zhong, Phoveus
- **r52 Heartbond** (2/4/6/10): Miya, Alucard, Fanny, Claude, Khufra, Esmeralda
- **r53 Astro Power** (2/4/6/10): Minotaur, Hilda, Aurora, Odette, Helcurt, Martis
- **r54 Dragoncaller** (2/4/6/10): summons the **Dragon (id 179)** and scales its damage at higher
  tiers. Members: Balmond, Clint, Eudora, Gusion, Badang, Terizla
- **r55 Neobeasts** (2/4/6/10): Gatotkaca, Pharsa, Ling, Lylia, Brody, Fredrinn
- **r56 Kishin** (2/4/6/10): Franco, Karrie, Lancelot, Angela, Lunox, Dyrroth
- **r57 Enchanted Tales** (2/4): Vexana, Selena, Leomord, Belerick
- **r58 Mystic Meow** (2): Lesley, Silvanna, Julian
- **r59 Northern Vale** (2/3): Bane, Luo Yi, Joy

## Per-tier effect layer (DSL cracked 2026-06-28)

Each synergy tier carries value-formula tokens (`m_NumDescribe`): a small DSL that fills the
`<Num>` / `<%Num>` placeholders in the effect text. Full spec in the datamine
(`work_dir/saori/mcgg/FORMULA_DSL.md`); structured per-tier output (all 20, every token parsed)
in `parsed/strategy/resolved_effects.json`.

- **Token:** `[type|effectId|param|unit|expr]`. type 2 = MCEffect value, 3 = trigger chance,
  105010/105011 = count-scaled; unit is %/flat/raw; expr e.g. `N*0.01` = raw stored x100 -> percent.
- **Validated:** `N*0.01` matches the item convention (stored 2000 -> 20%; Inspire = 20/25/30/40%).
- **Numbers stay templated.** The raw `N` lives in MCEffect under a composite id the client maps in
  battle logic, not a flat key (verified: sibling ids absent from every table). So the effect
  *shape* is certain; the exact per-tier percentages need the IL2CPP read-program.
- Effect-mechanic text below is a localization candidate (text is hash-keyed; mapping unverified).

Effect shape per synergy (Num order; chance = a proc %, value = a scaling %, flat = absolute):
- **r1 Bruiser**: chance% + value%. **r2 Dauntless / r10 Phasewarper / r54 Dragoncaller**: value%s.
- **r3 Defender / r7 Stargazer**: flat values. **r5 Marksman / r8 Assassin**: count-scaled.
- **r9 Scavenger / r56 Kishin / r57 Enchanted Tales**: include a resolved literal (e.g. +1).

Mechanic candidates (localization; numbers templated):
- **r4 Weapon Master**: gain ATK Speed for every % HP lost.
- **r6 Mage**: steal Mana from the target when Basic ATKs deal DMG.
- **r8 Assassin**: grants Dodge when the synergy reaches max stacks.
- **r50 Emberlord**: on an Emberlord Hero's death, Emberlord Heroes with 3 Equipment gain ATK Speed.
- **r51 Exorcist**: a Hero turned Phantom deals extra True DMG (% of Adaptive ATK).
- **r52 Heartbond**: when one partner enters Dormancy, the other gains ATK Speed.
- **r53 Astro Power**: each deployed Astro star adds damage to the most-equipped Astro Hero.
- **r55 Neobeasts**: Heroes gain extra Hybrid ATK, building points on each enemy death.

## Reading notes
- Icons live in `synergy_icons/<name>.png` (copied from the datamine's `relationN.png`, renamed by
  the resolved name): all 20 named, including `scavenger.png` and `phasewarper.png`.
- The `dps` values scale steeply with tier but are raw balance-scaling numbers, not the displayed
  effect; the readable per-tier numbers stay templated (see effect layer above).
- Comp-building target: cross faction and class breakpoints with the fewest slots. See
  [[heroes/index]] for who shares what, and [[abstract_generalization]] for why thresholds rule.
