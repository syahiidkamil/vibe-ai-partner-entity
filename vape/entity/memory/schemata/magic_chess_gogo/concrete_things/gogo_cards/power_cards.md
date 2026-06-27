# Power Cards — MCGG Go Go Cards (Commander Power Cards)

The commander-themed Go Go Cards (the "Power Cards" tab, pink frame). Each is tied to a Commander
and its effect keys off that Commander's abilities. First-party from the live client localization
(v1.2.88.302.2); see [[index]] for the method and [[../../disclaimer]] for the expiry.

**36 distinct "X's Power" names** are present in the live localization. Numbers below stay as
`<Num>` template placeholders except the four UI anchors, whose filled values are confirmed verbatim
from the game UI. `(Exclusive)` marks a card only its own Commander may pick; the rest can be
borrowed by any Commander.

## Anchors (verbatim, UI-confirmed)
- **Minotaur's Power**: Select an Equipment to enhance. Can be used 2 time(s). Obtain random
  Equipment x2.
- **Kagura's Power**: Select a Hero. When battle starts, they gain 20% Hybrid Lifesteal and 30%
  Hybrid ATK. Gain 9 Gold.
- **Johnson's Power** (Exclusive): Increases the number of Johnnies in the Hero Pool by 5. Johnny
  gains 25% Hybrid ATK and 20% Max HP.
- **Lunox's Power** (Exclusive): Gain 4 Gold. When you first activate a Synergy to 6, gain 24 more
  Gold.

## Resolved effects (effect self-identifies its Commander)
Template text; `<Num>`/`<%Num>` are the per-card values (in the card-quality table, not resolved).
- **Karina's Power** (Exclusive): Gain `<Num1>` Gold. Twinblades gain `<%Num2>` ATK Speed.
- **Lukas's Power** (Exclusive): Gain `<Num1>` Gold. Sacred Beast gains `<%Num2>` extra DMG.
- **Alice's Power** (Exclusive): Gain `<Num2>` EXP. Heroes selected by Alice's skill gain `<%Num1>`
  extra Hybrid ATK.
- **Yu Zhong's Power** (Exclusive): The subsequent Go Go Cards are upgraded by 1 quality tier. If
  the initial quality before selection is Purple or Orange, receive an extra Black Dragon Treasure.
- **Ruby's Power** (Exclusive): Gain `<Num1>` Gold for each survived Cloak or Scythe carrier when
  battle ends. Max Gold: `<Num2>`.
- **Diggie's Power** (Exclusive): Gain `<Num1>` extra Time Points each round. The Alarm Chest opens
  1 extra time to grant rewards worth `<Num2>` Gold.
- **Popol and Kupa's Power** (Exclusive): Gain `<Num1>` Gold when capturing a Hero. Gain `<Num3>`
  Equipment Chest(s) after capturing `<Num2>` Hero(es) for the first time.
- **Popol and Kupa's Power** (Copy Trap variant): Starting from Round `<Num1>`, generate a Copy
  Trap. Once per round, if an enemy steps into it, obtain their 1-Star version and `<Num2>` Gold;
  otherwise gain Gold.
- **Zilong's Power** (Exclusive): Great Dragon Spear + `<%Num1>` Hybrid ATK. The Shop auto-refreshes
  to fill all slots with its traits. Select 1 trait for free.
- **Harley's Power**: Gain `<Num3>` Gold. The Shop will auto refresh once to show at least
  `<Num2>`-Gold Hero x`<Num1>`. (UI capture: Gain 6 Gold, at least 4-Gold Hero x2.)
- **Lancelot's Power**: Gain `<Num2>` Gold per round upon reaching Commander Lv.`<Num1>`. (UI
  capture: 2 Gold per round at Commander Lv.5.)
- **Dyrroth's Power** (Exclusive): a Commander Dyrroth exclusive Go Go Card exists
  (`loc[2212545881]`); its effect text is not deterministically located. Effect **unresolved**.

## Names resolved, effect not paired (21)
First-party names; effect text not deterministically pairable from the loc blocks (do not guess).
Aamon, Alucard, Angela, Aurora, Chou, Fanny, Guinevere, Gusion, Kalea, Layla, Ling, Luo Yi, Lylia,
Miya, Moskov, Nana, Paquito, Vale, Valir, Vexana, Wanwan (each as "X's Power").

## Reading note
Power Cards span the run's levers: equipment (Minotaur, Zilong), a carry buff (Kagura, Alice),
flat/scaling economy (Lunox, Harley, Lancelot, Karina, Ruby), a board-stealing trap (Popol and
Kupa), tempo and shop control (Johnson, Diggie), and card-quality upgrades (Yu Zhong). Full record:
`parsed/strategy/gogo_cards.json`. Generic rarity cards: [[generic_cards]].
