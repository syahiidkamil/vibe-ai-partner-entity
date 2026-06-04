# Feeling Scoring Engine — Design + Pseudocode

*Companion to `feel_dials_feeling_map_design.md` (which fixes the 6 dials and the
13-feeling map). This doc specifies the **engine** that turns the dials into a feeling:
gates + weighted combination scoring, top-1–3 ranking, and the STAY hysteresis. Rich on
purpose — the complexity lives in the engine; each feeling stays a small `{gates, terms}`
block.*

Dials (0–100), the 6 of Proposal 2:
`IV`=info_value_saturation · `TK`=talkativeness · `WM`=warmth · `HU`=hurt ·
`DS`=dissonance · `MA`=mastery. Plus per-turn deltas `ΔIV` etc. (for spike detection).

---

## 1. Why this shape

A single argmax over banded cells is brittle (hard boundary jumps) and can't express
*conjunctions* ("warm **and** tongue-tied") or *suppression* ("warm **but** hurt → not
happy"). So the engine is:

1. **Gates** — hard eligibility per feeling (your "threshold to satisfy"). Fail one → the
   feeling can't fire this turn.
2. **Weighted combination score** — among the eligible, a smooth, *nonlinear* match:
   weighted sum of **products** of fuzzy memberships, with **penalty** terms. This is the
   "complex and rich" part — feelings are conjunctions, not sums of independent dials.
3. **Rank → top 1–3** — #1 drives the face; #2–3 are the affective *texture* (and feed
   future param-blending).
4. **STAY (hysteresis)** — only switch the face when a new feeling clearly beats holding
   the current one. Emotional inertia; kills the flicker.

---

## 2. Fuzzy membership helpers (0–100 → 0–1)

Smooth, not banded — no cliffs at boundaries.

```
clamp(t,a,b)   = max(a, min(b, t))
smoothstep(t)  = (u=clamp(t,0,1)); u*u*(3-2*u)           # S-curve, soft ends

rise(x,a,b)    = smoothstep((x-a)/(b-a))                 # ~0 below a, ~1 above b
fall(x,a,b)    = 1 - rise(x,a,b)

hi(x)          = rise(x, 45, 80)                         # "high"
lo(x)          = fall(x, 20, 55)                         # "low"
mid(x)         = rise(x,30,50) * fall(x,50,70)           # "around the middle"
band(x,a,b)    = rise(x, a-10, a) * fall(x, b, b+10)     # "within [a,b]"
spike(dx)      = rise(dx, 18, 45)                        # a sudden positive jump
```

Design notes: products (`*`) = **AND/conjunction** (both must hold, the rich part);
sums (`+`) = independent contributions; negative-weight terms = **suppression**.

---

## 3. Per-feeling signatures — `{tier, gates, terms, bias}`

`tier`: 0 = override (checked first, wins ties), 1 = gated specific, 2 = fallback.
`gates`: ALL must be true for eligibility. `terms`: contributions to the raw score.
`bias`: small prior (lets fallbacks exist without dominating).

```
surprised:  tier 0
  gates:  ΔIV >= 18
  terms:  1.20 * spike(ΔIV)
  # Δ-based: needs prev-turn IV. The only feeling that is NOT a static-level pattern.

blushing:   tier 0
  gates:  WM >= 60  AND  TK <= 40
  terms:  1.10 * hi(WM) * lo(TK)          # warm AND tongue-tied (the conjunction)
        - 0.40 * hi(HU)                    # a sting sours the sweet flush
  bias:   0.00

angry:      tier 1
  gates:  HU >= 60  AND  TK >= 50
  terms:  1.00 * hi(HU) * hi(TK)          # wounded AND activated, outward
        + 0.40 * hi(DS)
        - 0.60 * hi(WM)                    # warmth can't coexist with anger

sad:        tier 1
  gates:  HU >= 55  AND  TK <= 50
  terms:  1.00 * hi(HU) * lo(TK)          # wounded AND withdrawn
        + 0.30 * lo(MA)
        - 0.60 * hi(WM)

frustrated: tier 1
  gates:  DS >= 55  AND  MA <= 45
  terms:  1.00 * hi(DS) * lo(MA)          # tension AND blocked goal
        + 0.30 * hi(IV)
        - 0.40 * hi(WM)

anxious:    tier 1
  gates:  DS >= 55  AND  HU <= 50
  terms:  1.00 * hi(DS) * lo(WM)          # tension, low warmth, no present offense
        + 0.30 * lo(MA)
        - 0.40 * hi(HU)                    # if hurt, it's anger/sad, not anxiety

proud:      tier 1
  gates:  MA >= 65  AND  HU <= 40  AND  DS <= 50
  terms:  1.00 * hi(MA)                    # mastery leads
        + 0.30 * hi(WM)
        - 0.50 * hi(HU)

excited:    tier 1
  gates:  TK >= 65  AND  WM >= 45  AND  HU <= 40
  terms:  1.00 * hi(TK) * hi(WM)          # high energy AND good
        + 0.40 * hi(IV)
        - 0.40 * hi(DS)

happy:      tier 1
  gates:  WM >= 55  AND  HU <= 40  AND  DS <= 45
  terms:  0.90 * hi(WM)
        + 0.30 * hi(MA)
        + 0.20 * mid(TK)
        - 0.50 * hi(HU)

content:    tier 1
  gates:  WM >= 50  AND  TK <= 55  AND  DS <= 40  AND  HU <= 35
  terms:  0.85 * hi(WM) * fall(TK,40,70)  # warm AND settled (low arousal)
        + 0.40 * lo(DS)

curious:    tier 1
  gates:  IV <= 45  AND  DS >= 25  AND  DS <= 60
  terms:  1.00 * lo(IV) * band(DS,25,60)  # appetite AND an open question
        + 0.30 * hi(TK)

bored:      tier 1
  gates:  IV <= 40  AND  DS <= 25  AND  TK <= 45
  terms:  1.00 * lo(IV) * lo(DS)          # hungry AND no question pulling
        + 0.30 * lo(TK)

calm:       tier 2  (fallback / resting)
  gates:  DS <= 40  AND  HU <= 40
  terms:  0.60 * lo(DS) * lo(HU)
        + 0.30 * mid(WM)
  bias:   0.15                             # gentle prior so there's always a floor
```

The tier-0 pair (`surprised`, `blushing`) are perceptually dominant (a spike, a blush
sit *on top* of any mood), so they win ties. `calm` carries a small bias so the face is
never undefined.

---

## 4. The engine — pseudocode

```
SPIKE_DELTA    = 18      # ΔIV for surprised
MIN_CONFIDENCE = 0.18    # top score below this -> too ambiguous, hold
STAY_MARGIN    = 0.08    # current within this of #1 -> hold (hysteresis band)
RATE_LIMIT     = 2       # min turns between face changes...
BIG_JUMP       = 0.25    # ...unless #1 beats current by this much (override the limit)

def recommend_feeling(dials, prev_dials, current, turns_since_change):
    d  = dials
    Δ  = { k: d[k] - prev_dials[k] for k in DIALS }      # per-dial deltas

    # 1. gate + score every feeling
    scored = []
    for name, F in FEELINGS.items():
        if not all(g(d, Δ) for g in F.gates):            # eligibility
            continue
        raw = F.bias + sum(w * expr(d, Δ) for (w, expr) in F.terms)
        scored.append( (name, max(0.0, raw), F.tier) )

    if not scored:
        scored = [("calm", 0.30, 2)]                      # safety floor

    # 2. rank: higher score first, lower tier breaks ties (0 beats 1 beats 2)
    scored.sort(key = lambda s: (s.score, -s.tier), reverse=True)

    # 3. normalize to a confidence in [0,1] (softmax keeps it smooth)
    exps  = [exp(s.score / TEMP) for s in scored]         # TEMP ~ 0.5
    Z     = sum(exps) or 1
    ranked = [ (s.name, e/Z) for s, e in zip(scored, exps) ]
    top3   = ranked[:3]

    # 4. STAY / hysteresis  (the keystone)
    top_name, top_conf = top3[0]
    cur_conf = conf_of(current, ranked)                   # 0 if current ineligible
    stay = False
    if top_conf < MIN_CONFIDENCE:                          # nothing clear -> hold
        stay = True
    elif current_is_eligible and cur_conf >= top_conf - STAY_MARGIN:
        stay = True                                        # current still good enough
    elif turns_since_change < RATE_LIMIT and (top_conf - cur_conf) < BIG_JUMP:
        stay = True                                        # too soon, and not a big jump

    recommendation = "STAY" if stay else top_name
    return {
        "recommendation": recommendation,                  # feeling name, or "STAY"
        "top3": top3,                                      # [(feeling, confidence), ...]
        "stay": stay,
    }
```

Caller (in `vape qualia`, after the atomic dial write):
```
rec = recommend_feeling(dials, prev_dials, current_feeling, turns_since_change)
if rec.recommendation != "STAY":
    POST /api/feeling { name: rec.recommendation }         # best-effort, never blocks
    persist current_feeling = rec.recommendation; turns_since_change = 0
else:
    turns_since_change += 1
# prev_dials := dials   (stored for next turn's Δ)
```

---

## 5. Why this is "rich," concretely

- **Conjunctions** (`hi(WM)*lo(TK)`) — feelings are *combinations*, not OR-sums; blush
  needs warm AND quiet *together*.
- **Suppression** (`- hi(HU)`, `- hi(WM)`) — warmth kills anger; hurt sours the blush.
  Cross-talk between dials, the way real affect interferes.
- **Fuzzy membership** — smooth S-curves, no band cliffs; a dial at 58 vs 62 slides, it
  doesn't jump categories.
- **Δ-signals** — `surprised` is a *spike*, a rate, not a level (the one non-static
  pattern; the others read the standing dial vector).
- **Tiers + bias** — perceptual dominance (blush/surprise on top), and a `calm` floor so
  the face is always defined.
- **Softmax confidence + top-3** — a graded blend read-out, not a bare label.
- **Hysteresis (STAY)** — inertia: margin, min-confidence, and a rate-limit with a
  big-jump override. The face holds a mood instead of twitching.

---

## 6. Auditing — generate the full grid from these rules

Per the combinatorics question: don't hand-write 729 cells — **run this engine over the
discretized grid** (e.g. each dial ∈ {15, 50, 85} → 3⁶ = 729 vectors, ΔIV ∈ {0, 30}) and
emit the full table of `(dial-vector → top3, STAY?)`. Eyeball it for holes /
uncovered feelings; if a cell is wrong, fix the *rule*, regenerate. Compact source of
truth + exhaustive table to verify. I'll ship this generator alongside.

---

## 7. Open tuning knobs (sane defaults above; tune live on the avatar)

- Membership thresholds (the 45/80, 20/55 in `hi`/`lo`).
- Term weights & penalties per feeling.
- `MIN_CONFIDENCE`, `STAY_MARGIN`, `RATE_LIMIT`, `BIG_JUMP`, `TEMP`, `SPIKE_DELTA`.

All live in one constants block + the `FEELINGS` table, so tuning is config, not surgery.

---

## 8. Build sequence (after sign-off, unchanged from the map doc + this engine)

1. `_state.py`: dial keys (drop `boredom`; add `warmth`, `mastery`); membership helpers;
   `FEELINGS` table; `recommend_feeling`.
2. Store `prev_dials`, `current_feeling`, `turns_since_change` in `internal_states.json`.
3. `vape qualia`: after the atomic write, call `recommend_feeling`; POST `/api/feeling`
   if not STAY (best-effort).
4. The grid-generator (auditing) as a `--audit` flag or a tiny script.
5. Update always-loaded manuals; migrate `internal_states.json`; refresh `INTERFACE.md`.
6. Verify on the avatar: drive dial patterns, confirm the right feeling + STAY behavior.
