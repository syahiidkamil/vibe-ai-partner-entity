# Synergies — MCGG S6 (concrete rung)

The 20 team-bonus groups ("Sort"/relations). Member rosters and activation tiers are solid ground
truth from `dataset_s6.json`. **Names were resolved on 2026-06-27** from in-game UI screenshots
matched to the icons (the client's own `name` field is null for every synergy). Per-tier effect
TEXT is still not in the client (templated formula codes); only the activation count and a `dps`
scaling value are stored. Each synergy's icon, renamed by name, lives in `synergy_icons/`.

**Axis.** class = relId 1-10 (role/archetype, RelationType 2). faction = relId 50-59 (origin,
RelationType 1). A hero usually belongs to one class and one faction.

**Name confidence.** All 20 names are resolved (high confidence: icon match calibrated against the
four anchors Defender/Marksman/Mage/Assassin, plus member-roster cross-check). The last two,
**Scavenger (r9)** and **Phasewarper (r10)**, came from a second UI screenshot and are corroborated
by the comp guides (Scavenger is the economy synergy; Phasewarper's lineups name Julian and Clint,
both r10).

**Correction to the datamine `plan.md` (flagged for Kamil to confirm).** plan.md labeled relId 51
as "Dragon Altar / Dragoncaller" and tied the Dragon summon (id 179) to it. The S6 icon and the
comp-guide rosters disagree: **relId 51 = Exorcist** (a torii-gate icon), and **relId 54 =
Dragoncaller** (the dragon icon; its members Balmond, Terizla, Gusion all match the comp guides'
Dragoncaller lineups). So the Dragon is summoned by **r54**, not r51. High confidence, but it
contradicts the doc, so confirm before I propagate it into the hero roster and the disclaimer.

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

## Reading notes
- Icons live in `synergy_icons/<name>.png` (copied from the datamine's `relationN.png`, renamed by
  the resolved name): all 20 named, including `scavenger.png` and `phasewarper.png`.
- The `dps` values scale steeply with tier but are raw scaling numbers, not readable effects; the
  human-readable per-tier effects are still absent from the client dump (templated). Marked unknown.
- Comp-building target: cross faction and class breakpoints with the fewest slots. See
  [[heroes/index]] for who shares what, and [[abstract_generalization]] for why thresholds rule.
