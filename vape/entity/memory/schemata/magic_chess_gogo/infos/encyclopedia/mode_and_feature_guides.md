# Mode & Feature Guides — MCGG (beyond the 8 Encyclopedia tabs)

The other MCGG-specific guides that live in the localization but not on the Encyclopedia tab bar.
Verbatim (markup stripped, `##`/`####` as line breaks). Source ids noted per guide. MOBA-only
tutorials are excluded on purpose (this is the full Mobile Legends localization file; only the
Magic Chess ones are kept). Provenance + reproduction: [[README]] and `gen_encyclopedia.py`.

## Modes

### Go Go Auction (ids `2912711047`/`2912711048`)
> 1. Enter the Auction Arena at round **I-4**. (Exclusive to Cosmic Traders.)
> 2. Gain **10 Gold** upon entrance.
> 3. There are **8 rewards** in the Auction Arena. Move into a reward's area to bid on it.
> 4. You can bid only these fixed amounts: **0, 3, 6, 9, 12, 15, or 20 Gold**.
> 5. If no other bids occur within **12 seconds**, the highest bidder wins.
> 6. Pay the **Buyout Price of 20 Gold** to directly purchase the reward.
> 7. When bidding ends, winners pay their final bid price and receive their rewards. Players who
>    don't win any bids get one random unsold reward at base price.

### Draft Pick (ids `2078505105` label, `1080434174` body, `1144011998` AFK)
> Step 1. During the ban stage, players can vote for the Commander they want to ban; the two
> Commanders with the most votes are banned. Since there is **no Classic Mode in Magic Chess: Go
> Go**, there is a **14-day protection period** during which new Commanders cannot be banned (so
> players can try them out).
> Step 2. After the ban stage, select a Commander Skill from Commanders you own or have free.
> Banned Commanders cannot be selected.
> Note: Draft Pick is available **10 days** after a new season begins.

AFK in Draft Pick forfeits your Exp and Battle Points to your non-teamed teammates (`1144011998`).

## Features

### Commander Power Card (ids `2912711086` label, `2912711108` body, `1629673760`)
> 1. Introducing Commander Power Cards in **Round I-2**! This new feature **replaces the first Go
>    Go Card round**.
> 2. Each Commander has a unique Power Card that provides effects tied to their abilities.
> 3. Only Power Cards appear in this round, with your Commander's **exclusive Power Card
>    guaranteed** among the options. Choose wisely to seize victory!

In that first Go Go Card stage you may boost your Commander with their own Power Card or **borrow
an ability from another Commander** (`1629673760`). Card pool: [[gogo_cards/index]].

### Crystal Dice (ids `2078505135` label, `1082709494`, `2312887464`)
> Use Crystal Dice to **refresh a Go Go Card when you've run out of regular refreshes**. Only
> **one Crystal Dice per Go Go Card round**, and it refreshes **only one card at a time**. Usage
> priority: Limited-Time Crystal Dice > Permanent Crystal Dice.

### Magic Crystal: Rune (ids `2078505133` label, `1662170372`-`374`, `3007059187`)
The Magic Chess: Go Go 4th-Anniversary system.
> In **Round 4**, select **1 of 3** random **Magic Crystals**. Equip it on a hero of another
> Synergy to **include them in the corresponding Synergy**; it can be switched onto other heroes.
> During **Rounds 7 and 13**, select **1 of 3** random **Runes** to enhance your lineup. Each Rune
> selection comes with a **free refresh**, and Runes **do not require Synergies** to be active.

(Season banner phrases it as: equip a Magic Crystal to fold a hero into a Synergy, and pick 2
Runes to enhance the Crystal twice.) Synergies: [[synergies]].

### Auto Buy (ids `1079666900`/`1079666901`)
> After you enable Auto Buy, **equipment will be bought according to your Battle Setup**. You can
> turn it off in Settings anytime in battle. Note: while enabled, the direct-purchase-equipment
> button (upper-right) is hidden.

### Lock Shop / Advanced Shop (id `1146073352`)
> **Lock the Shop** to keep heroes available for purchase in the next Preparation Phase.

(There is no separate "Advanced Shop Tutorial" prose panel; this lock-shop line is the mechanic
the label points at. Some Commander skills also auto-lock the shop after use.)

### Collection Points (ids `1083363810`-`813`, `1083363845`)
> New **skin** collectibles and new **Chessboard** collectibles grant Collection Points (an amount
> per rarity). **Limited-time items do not count** towards Collection Points.

Cosmetics-meta, not in-match play. The per-rarity point values are a UI grid, not localization
prose (left **unknown**).

## Synergy Tutorials

### Heartbond Synergy Tutorial (ids `1083367870`-`873`)
> Place Heartbond Heroes on **adjacent tiles** to bond them. **Bonded Heroes gain combat power
> bonuses and can help each other reawaken!** (An interactive ~1-min in-match tutorial.)

**Heartbond is the only synergy with a dedicated, named tutorial in this build.** The other
synergies have no per-synergy tutorial entry; the generic "Synergy Tutorial" strings (ids
1082682643, 1082708528, 1145919493) are the launchers for the general in-match interactive
tutorial. Full per-synergy data: [[synergies]].

## Not captured (no extractable prose in localization, by honest check)
- **Battlefield Overview / Battlefield Guide** (1607301788, 2118913752) — an image/resource
  package you download in-client; no text body.
- **Income Overview** (1004343994), **Feature Guide** (4248755993), **Function Guide**
  (3825240374) — UI-screen labels with no prose body.
- **Interest Tutorial** (1082708529), **Gold Tutorial** (1082682645), **Equipment Tutorial**
  (1104605973), **Blessing Tutorial** (1083390933), generic **Synergy Tutorial** — interactive
  1-min in-match tutorial launchers (only confirm strings). Their substance is already captured:
  interest/gold in [[gold_economy]], Blessing in [[hero]], equipment in [[equipment_and_economy]].
- **Gold Rush Guide** (2078505109) — only a "mode disabled" string is present; no prose body.
  **Uncertain** whether a MCGG sub-mode or a separate MLBB mode; flagged, not forced.
- **Go Go MOBA Guide** (2078505137) — Go Go MOBA is a separate MOBA-style sub-mode with
  per-Commander MOBA skills; those are MOBA content, excluded. Mode noted only.
- **Asset Inheritance Guide** (1628844038) — label present; no MCGG prose body found (search hits
  were unrelated MOBA hero-skill "inherit" text). **Uncertain**, flagged.
