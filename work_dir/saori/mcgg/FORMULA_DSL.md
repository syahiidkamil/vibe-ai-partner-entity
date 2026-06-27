# MCGG value-formula DSL (the `[type|id|param|unit|expr]` tokens)

Magic Chess GoGo stores the **displayed numbers** in synergy, hero, and item effect text as a
small templating DSL, not as plain values. Each effect description in localization carries
placeholders `<Num1>`, `<%Num1>`, `<Num2>` ... and a parallel array of **formula tokens** (one
per placeholder, in order) tells the client how to compute each number at runtime.

Source of the tokens: `RelationSkill_MC_S6.m_NumDescribe` (synergies), the hero/item skill
tables, and the readable reference dump `FreyaRelationSkilltips.txt` (which shows the richest
form, with color wrappers and arithmetic).

Verified live on v1.2.88.302.2 (BlueStacks pull). Last verified 2026-06-28.

---

## 1. The token grammar

```
token        := literal | effectref
literal      := <number>                       e.g. "1", "3", "999"   (a constant, already the value)
effectref    := "[" type "|" id "|" param "|" unit "|" expr ( "|" extra )? "]"
```

A `m_NumDescribe` array is the ordered list of values that fill `Num1, Num2, Num3, ...` in the
matching description template. `"0"` entries are empty/disabled slots (skip them).

### Fields of an `effectref`

| field    | meaning |
|----------|---------|
| `type`   | which value source / kind (see §2) |
| `id`     | the effect id to look up the raw value `N` in (a **composite** id, see §4) |
| `param`  | the column/parameter inside that effect row that holds `N` (e.g. `Value0`, `FPara1`) |
| `unit`   | how to format the result (see §3) |
| `expr`   | how to turn the raw `N` into the displayed number (see §3) |
| `extra`  | optional 6th field, an index/flag; seen as `|0>` in the Freya dump |

Example: `[2|4010104|Value0|%|N*0.01]`
= take effect `4010104`'s `Value0` column as `N`, compute `N*0.01`, show as a percent.

---

## 2. `type` — the value source (live distribution across the 20 synergies)

| type     | count | meaning |
|----------|-------|---------|
| `2`      | 117   | **MCEffect value lookup** — `id` -> effect row, read `param` column for `N`. The workhorse. |
| `3`      | 3     | **TriggerJudge** — a proc/trigger *chance* (param `TriggerJudge-1`). |
| `105010` | 6     | **dynamic / count-scaled** value (e.g. per-stack, per-hero-count). |
| `105011` | 10    | **dynamic / count-scaled** value (same family as 105010). |

(Plus 12 bare **literals** — constants like `1`, `3`, `999` — which need no lookup.)

---

## 3. `unit` and `expr` — formatting the raw `N`

`unit` (how the number is labelled):

| unit | count | meaning |
|------|-------|---------|
| `%`  | 98    | percent (the `<%NumK>` placeholders) |
| `@`  | 22    | flat / absolute value ("at") |
| `0`  | 16    | unitless / raw |

`expr` (how the stored raw `N` becomes the shown number — live set):

| expr          | count | meaning |
|---------------|-------|---------|
| `N*0.01`      | 59    | raw is stored **x100**; e.g. raw `2000` -> `20` (% or flat) |
| `N`           | 22    | raw as-is |
| `N*0.1`       | 16    | raw stored x10 |
| `0`           | 16    | constant 0 (disabled slot) |
| `N*100`       | 14    | raw stored as a fraction; `0.2` -> `20` |
| `N*0.01+100`  | 4     | a **multiplier**: `100% + bonus%` (e.g. total damage multiplier) |
| `N*0.000001`  | 4     | raw stored x1e6 |
| `N*0.001`     | 1     | raw stored x1000 |

### Scaling convention — validated against the item ground truth

The `N*0.01` convention (raw stored x100) is **confirmed** by the item attribute table:
`AttrbuteDescribe_MC` gives percent attrs a `changePara` of `1e-4`, and the client shows
`stored x 1e-4 x 100` = `stored x 0.01`. Inspire-class ATK-Speed items store `2000/2500/3000/4000`
and display **20% / 25% / 30% / 40%** — exactly matching the in-game Inspire ("20/25/30/40% ATK
Speed"). So `expr N*0.01` on a raw of `2000` correctly yields `20%`. Same convention, two systems.

Demon Hunter Sword ("2% of target's max HP") is the same DSL: its description template is
localization `2212493025` *"Basic ATKs deal extra Physical DMG equal to `<%Num1>` of the target's
max HP."*, with `Num1` a `%` token whose raw resolves to `2`.

---

## 4. The richer form (color + arithmetic) — from `FreyaRelationSkilltips.txt`

The display layer wraps tokens in **color tags** and can do **arithmetic** between tokens:

```
[C3<2|47230200|Value0|%|N*0.01|0>]                       color C3, one value as %
AC3<{[2|4010104|Value0|%|N*0.01]+[2|47230200|Value0|%|N*0.01|0]}%>   sum of two effect values, shown %
```

- `[Cn< ... >]` / `AC3< ... >` — a colored span (`C1`=magic, `C3`=physical, `C6`/`C7`/`C9` UI accents).
- `{ tokenA + tokenB }%` — evaluate the inner tokens, **add**, then apply the outer unit (`%`).
  This is how a base synergy value and a hero's personal bonus combine into one shown number.

The main `RelationSkill_MC_S6.m_NumDescribe` tokens are the simple 5-field form; the Freya tips
table shows the full grammar the renderer supports.

---

## 5. Resolving `N` — what works and what does not

**Resolvable now:** literal tokens (the value *is* the token); the formatting of any token
(unit + expr) since that is self-contained.

**NOT resolvable from this static dump:** the raw `N` for `type 2` (MCEffect) tokens. The token
`id` (e.g. `4010104`, `4010402`, `4010702` for Bruiser's three tiers) is a **composite** id that
the client maps to an `MCEffect_S1/S2` row inside battle/Lua logic — it is **not** a flat int32
row key. Verified exhaustively: of those three sibling ids, only `4010104` appears as an int32
anywhere (a coincidental match), and `4010402` / `4010702` / `47230200` appear in **no** decoded
table. `MCEffect_S1` is a 2889-row, 64-column ver-1 table with no reference schema; even with the
schema, the id->row mapping is computed, not stored. The friend's datamine reached the same wall
(it resolved synergy/item **names** positionally and left effect values templated).

To finish numeric resolution you would need the **IL2CPP read-program** for `MCEffect_S1/S2` plus
the battle-logic id-mapping (both live on the datamine machine, not in this pull). Until then the
honest output is: **formula structure fully parsed, per-tier numbers templated.**

---

## 6. Worked example — Bruiser (relId 1)

Template (the readable summary form): *Bruisers gain bonus on Basic ATK.*
Per tier, `m_NumDescribe` = two tokens -> `Num1`, `Num2`:

| tier (need) | Num1 token                       | Num2 token                       | shape |
|-------------|----------------------------------|----------------------------------|-------|
| 2           | `[3\|4107\|TriggerJudge-1\|%\|N*0.1]`  | `[2\|4010104\|Value0\|%\|N*0.01]` | a trigger *chance* %, and a *value* % |
| 4           | `[3\|4108\|TriggerJudge-1\|%\|N*0.1]`  | `[2\|4010402\|Value0\|%\|N*0.01]` | same shape, higher tier |
| 6           | `[3\|4109\|TriggerJudge-1\|%\|N*0.1]`  | `[2\|4010702\|Value0\|%\|N*0.01]` | same shape, higher tier |

So Bruiser = "`Num1`% chance to deal `Num2`% bonus", scaling per tier. The *shape* is certain
from the tokens; the two percentages stay templated (their `N` lives in MCEffect, unreachable).
