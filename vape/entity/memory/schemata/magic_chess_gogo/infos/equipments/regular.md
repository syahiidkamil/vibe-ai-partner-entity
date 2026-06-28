# Regular Items (MCGG S6) — the Regular tab

28 entries: 5 Basic consumable actives + 23 stat items (Physical 7, Magic 4, Defense 7, Hybrid
ATK 5). **Names, stats, and Unique-Passive values are all first-party from the in-game UI** —
Basic *and* Enhanced detail panels captured per item (`storage/magic-chess-gogo/equipments/`).
The Enhanced form raises a passive's magnitude and/or adds a second passive; deltas marked
*(Enh: …)*. Stats use the UI's display form (Hybrid ATK = Phys+Mag; Hybrid DEF = Phys+Mag DEF).
Exact raw rows, ids, and the name↔id keying: [source_map](source_map.md).

## Basic (5) — consumable actives (no base stats unless noted)
- **Inspire** — *Increase ATK Speed.* Inspire: 20/25/30/40% ATK Speed (rises with Stage). *(Enh adds Swift: +20% ATK Speed)*
- **Revitalize** — *Restore HP at Low HP.* Below 50% HP, summon a Healing Spring 5s, healing 6% HP/s to allies in area. *(Enh adds Longevity: +20% Max HP)*
- **Purify** — *Control Immunity.* +15% ATK Speed. At battle start, control + displacement immunity for 30s. *(Enh adds Swift: +20% ATK Speed)*
- **Aegis** — *Shields to Allies.* At battle start, shield = 25% HP for 25s to self + allies 1 tile L/R. *(Enh adds Longevity: +20% Max HP)*
- **Retribution** — *DMG Increase.* 20/25/30/40% extra DMG (rises with Stage). *(Enh adds Onslaught: +20% extra DMG)*

## Physical (7)
- **Demon Hunter Sword** — *Tank Killer.* +10% ATK Speed. Engulf: Basic ATKs deal +2% target max HP as Physical DMG. *(Enh: 4%)*
- **Golden Staff** — *Extremely High ATK Speed.* +15% ATK Speed. Impulsive: each Basic ATK +2% ATK Speed, stacks ×50. *(Enh: 3.5% per stack)*
- **War Axe** — *Spell Vamp.* +10% Physical ATK, +15% Spell Vamp. Fighting Spirit: on dealing DMG, +4 Hybrid DEF 3s (stacks ×5); at max, +10% extra DMG. *(Enh: +6 Hybrid DEF, +30% DMG)*
- **Sea Halberd** — *Counter Lifesteal.* +15% Physical ATK, +40% Physical Penetration. Lifebane: dealing DMG reduces target HP Regen 30% for 5s. *(Enh adds Pierce: +25% Phys PEN, +15% Phys ATK)*
- **Berserker's Fury** — *Increase Crit.* +10% Physical ATK, +20% Crit Chance, +40% Crit DMG. *(Enh adds Valiant: +15% Crit Chance)*
- **Blade of Despair** — *Extra DMG.* +20% Physical ATK. Despair: +25% extra DMG for 2s vs targets below 50% HP. *(Enh: 50%)*
- **Haas' Claws** — *Lifesteal.* +20% Physical ATK, +15% Crit Chance, +15% Lifesteal. *(Enh adds Frenzy: +10% Lifesteal, +10% Phys ATK)*

## Magic (4)
- **Divine Glaive** — *Magic Penetration.* +25% Magic ATK, +40% Magic Penetration. *(Enh adds Spellbreaker: +25% Magic PEN, +15% Magic ATK)*
- **Glowing Wand** — *Skill Burn.* +15% Magic ATK. Scorch: Skill DMG burns 2.5% max HP/s for 3s (min 10), -30% Healing 3s. *(Enh: 5% max HP/s)*
- **Holy Crystal** — *Highest Magic DMG.* +20% Magic ATK. Mystery: +10% Skill DMG. *(Enh: +30%)*
- **Ice Queen Wand** — *Spell Vamp.* +15% Magic ATK, +15% Spell Vamp. Ice Bound: after skill DMG, -15% target ATK Speed 5s. *(Enh adds Extract: +10% Spell Vamp, +10% Magic ATK)*

## Defense (7)
- **Blade Armor** — *Physical DMG Bounce.* +50 Physical DEF. Vengeance: reflect 30% of Basic-ATK DMG taken as Physical DMG. *(Enh adds Defiance: +25 Physical DEF)*
- **Guardian Helmet** — *High Base HP.* +15% Max HP. Recovery: regen 1.5% Max HP/s. *(Enh adds Titan: +20% Max HP)*
- **Antique Cuirass** — *Reduce Target's Hybrid ATK.* +10% Max HP, +10% DMG Reduction. Deter: when damaged, -4% enemy Hybrid ATK 3s (stacks ×5). *(Enh: -7% for 4s)*
- **Thunder Belt** — *Tank DMG.* +20 Hybrid DEF. Power of Thunder: every 3s, next Basic ATK deals +8% Max HP as Magic DMG to target + nearby. *(Enh stats: +20% Max HP)*
- **Oracle** — *Group DEF.* +20 Hybrid DEF. Magic Resist: at battle start, same-row allies gain 20 Hybrid DEF. *(Enh: also +6% HP)*
- **Dominance Ice** — *Tank Mana Regen.* +50 Magic DEF, +10% Max HP. Arctic Cold: -20% nearby enemy ATK Speed; +25% Mana Regen when taking DMG. *(Enh: +50% Mana Regen)*
- **Ancient Wrath** — *Taunt & DEF.* +15% Max HP. Provocation: at battle start, taunt nearby; +10 Hybrid DEF per enemy targeting the carrier. *(Enh: +18 per enemy)*

## Hybrid ATK (5)
- **Spellblade Talisman** — *Rapid Skill Cast.* +15% Hybrid ATK. Recharge: at battle start, restore 55% Mana. *(Enh: 80% Mana + +15% Skill DMG)*
- **Winter Crown** — *Invincible at Low HP.* +10% Hybrid ATK, +10% Max HP. Freeze: at <25% HP or lethal DMG, become frozen and restore 10% Max HP over 1s. *(Enh: restore 25% HP + 10% Mana)*
- **Feline Blade** — *Single Control.* +15% Hybrid ATK, +10% Max HP. Witchcraft: at start, turn highest-Star enemy into a Leonin 3s; Basic ATKs turn the target Leonin 1.5s (once per 12s). *(Enh: Leonin take +60% DMG)*
- **Purple Buff** — *Additional Mana Regen.* +10% Hybrid ATK. Elemental Power: +10 Mana after casting a Skill. *(Enh adds Malefic: +20% Hybrid ATK)*
- **Claude's Theft Device** — *Copy Equipment.* +10% Hybrid ATK. Neat Pick: at battle start, copy 2 random Equipment (counts as equipping 3 pieces). *(Enh: also +15% DMG)*

By-id stat rows, skill ids, the attr legend, and the keying method: [source_map](source_map.md).
Governed by [[disclaimer]]; world-model: [[schemata]].
