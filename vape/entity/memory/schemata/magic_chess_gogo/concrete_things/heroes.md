# Heroes — MCGG S6 roster (concrete rung)

The most volatile rung: the 54-unit S6 roster. Source: Kamil's `dataset_s6.json` (the
consolidated join), cross-checked against `MCHero_S6.json` (all 54 costs verified, 0 mismatches).
Full per-star stat blocks live in that raw file; this is the gist (two-hop, dereference storage
for the numbers). Each hero carries its synergies as **relIds**, because synergy *names* are
mostly unresolved in the client (only 3=Defender, 5=Marksman, 6=Mage confirmed). The relId axis
and rosters are in [[synergies]].

## Cost distribution
cost 1: 8 · cost 2: 11 · cost 3: 12 · cost 4: 13 · cost 5: 10 · **total 54**.
Two are **non-shop special units**: id **179 Dragon** (a summon from the Dragon Altar faction
r51; 4 star tiers; no synergies of its own) and id **180 a special Claude** (no synergies).
Normal shop roster excluding those: c1:8 c2:11 c3:12 c4:12 c5:9 = **52**.

## Per-star upgrade
Each hero has 3 star tiers, each a full stat block (hp, phys/mag atk, def, atk-speed, dps, ehp,
mp). Merge 3 copies to climb a star; HP scales ~1.8x per step, so a 3-star is a major spike. The
Dragon summon is the lone 4-tier unit.

## Roster by cost — `hero (classRelId / factionRelId)`
Names from the lang table; ~ marks a name resolved manually or a special unit.

**Cost 1:** Alucard (4/52) · Eudora (7/54) · Minotaur (3 Defender/53) · Dyrroth (1/56) ·
Silvanna (2/58) · Cecilion (6 Mage/50) · Brody (5 Marksman/55) · Phoveus (9/51)

**Cost 2:** Balmond (2/54) · Fanny (10/52) · Gatotkaca (1+3 Defender/55) · Angela (9/56) ·
Martis (4/53) · Selena (7/57) · Hanzo (8/50) · Belerick (1/57) · Granger (5 Marksman/51) ·
Lylia (6 Mage/55) · Joy (8/59)

**Cost 3:** Miya (5 Marksman/52) · Saber (8/51) · Tigreal (3 Defender/50) · Franco (2+4/56) ·
Clint (10/54) · Hilda (2/53) · Helcurt (8/53) · Khufra (3 Defender/52) · Masha (1/50) ·
~Luo Yi (7/59) · Julian (6 Mage+10/58) · Fredrinn (4/55)

**Cost 4:** Kagura (6 Mage/51) · Aurora (7/53) · Vexana (6 Mage/57) · Karrie (5 Marksman/56) ·
Irithel (5 Marksman/50) · Pharsa (7/55) · Gusion (8/54) · Leomord (4/57) · Lunox (7/56) ·
Esmeralda (2/52) · Terizla (3 Defender/54) · ~Yu Zhong (1/51) · ~Dragon (id 179, summon, no syn)

**Cost 5:** Bane (3 Defender/59) · Alpha (4/50) · Ruby (2/51) · Odette (6 Mage/53) ·
Lancelot (10/56) · Lesley (5 Marksman/58) · Claude (9/52) · Badang (1/54) · Ling (8/55) ·
~Claude special (id 180, no syn)

## Reading notes
- A hero usually has exactly one class synergy and one faction synergy; a few carry two class
  synergies (Gatotkaca 1+3, Franco 2+4, Julian 6+10).
- Hero id = the real MLBB global hero id, so this roster doubles as a bridge into MLBB itself.
- The strongest comps cluster heroes that share a faction *and* stack a class, to cross
  [[synergies]] breakpoints with the fewest board slots.
