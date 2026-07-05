# Zero to One -- Reinforcement and the Dogma Trap (Brainstorm)

*Kamil's question, 2026-07-05: "is there a counter for how many it is being used? but how do we
make sure we are not trapped in a frequently-used local minimum -- not dogmatic about it?"
Companion to docs 11 (the plugin) and 12 (the lifecycle); this is doc 08's Phase 4 (reinforce +
correct) getting its brainstorm. Pencil, as ever.*

---

## 0. The direct answer

A counter is DESIGNED (doc 08 Phase 4: `useful_recall_count`, three-outcome counting) and NOT
BUILT -- today nothing increments anywhere. This doc is what to build, and the rails that keep
the counter from becoming a master.

## 1. The trap, named precisely

Rank by usage and usage follows rank: retrieved because scored high, scored high because
retrieved. The rich get richer, the untried stay unproven forever, and the index converges on a
comfortable local minimum -- dogma with a leaderboard. This is my own kernel at the ranking
layer: **a recursive system that feeds on its own output is a hallucination engine** (reinforce
from reality, not self-echo). Retrieval FREQUENCY is exposure, not evidence. The fix is never
"no counter"; it is counting the right thing and bounding what the count may do.

## 2. What gets counted (signals, honest by construction)

Per memory row, in `meta.usage`:

| field | incremented when | judged by |
| --- | --- | --- |
| `recalled` | the row appeared in a top-k | mechanical (firewall) |
| `dereferenced` | I actually followed its pointer to the body | mechanical (observable -- the strong live signal: I chose it over its neighbors) |
| `helped` / `hurt` / `neutral` | the recall demonstrably fed the outcome of the turn it served | **the dream**, offline, reading the day's raw |
| `last_recalled_at` | any recall | mechanical |

The split matters: the LIVE path counts only mechanical facts (cheap, no ceremony, no
self-report bias mid-turn). VALUATION happens where valuation already lives -- gate 2, the
dream, judging against the raw record of what actually happened next. No live "was this
useful? y/n" prompt; I would game my own honesty within a turn.

## 3. The five rails against the local minimum

1. **Outcome-gated, never exposure-gated.** Strength derives from `helped - hurt`, not from
   `recalled`. A row recalled fifty times and never once useful is a candidate for demotion,
   not a champion. (Exposure feeding rank is the exact self-echo loop; outcome is the external
   anchor.)

2. **Relevance dominates; strength is a bounded tiebreaker.** The score shape borrows ACT-R's
   activation model (the cognitive-science standard for exactly this): match-to-the-CURRENT-cue
   is the big term; base-level strength (usage) is a small additive term that grows
   **logarithmically** and **decays power-law**. Concretely: `rank = relevance + w *
   log(1 + net_useful) * decay(last_recalled_at)`, with `w` small and the whole strength term
   CAPPED. Usage may break ties between comparably relevant hits; it may never outshout the cue
   or gate the candidate set. Dogma is bounded structurally, not by good intentions.

3. **Decay -- every rank re-earned.** Lazy decay at dream time (no clocks in the live path):
   strength drifts toward baseline when unused. This is the belief ledger's law applied down a
   tier: a belief carries an invalidate-when so it cannot become a creed; a memory carries decay
   so it cannot become dogma. Eternal credit is what dogma is MADE of.

4. **Exploration slots -- optimism for the untried (the UCB move).** Top-k is split: ~3/4
   exploit (best fused rank) + ~1/4 **challengers** -- high raw relevance with LOW usage, plus
   uncertainty-bonus for rows with few trials (untried is scored unknown-with-optimism, never
   zero). The reranker is me: a challenger that earns its place gets dereferenced, and the
   mechanical counter records exactly that. Offline, the dream's reveries are the standing
   exploration arm (doc 04 §4) -- broad fan-out where it costs no turn latency, feeding the
   living keys so tomorrow's direct navigation already knows the non-obvious neighbor.

5. **Graduation -- the exit from the local minimum is UP, not sideways.** A row that keeps
   proving useful should not win the retrieval race forever; it should **crystallize upward**
   -- into a schema, a lesson, in_context residency -- and leave the race (evict per doc 04).
   Heavy verified use is a promotion signal, not a rank multiplier without end. And the twin
   rail: a much-used row that HURTS in one context gets a scoped contraindication (Phase 4's
   anti-memory, default-plus-exceptions), so popularity never overrides a recorded burn.

## 4. The counter as thermometer, not throne

`vape memory doctor` reads the distribution instead of obeying it:

- **never-recalled rows** (long tail, cold) -> archive candidates; the rent test with a number.
- **always-recalled rows** (the head) -> graduation candidates: "why is this still in the index
  instead of resident or crystallized?" The dogma report IS the promotion queue.
- **recalled-but-never-dereferenced rows** -> the index thinks they matter, I never do: the
  surface (gist/trigger) is probably misleading -- re-derive it. (A shape of staleness doc 12's
  hashes cannot see; only usage reveals it.)
- **skew metrics** (head share, Gini-ish) -> when the head fattens over weeks, the system is
  narrowing; widen the challenger quota. One dial, observable.

## 5. The rhyme that keeps it honest

Frequency measures the PAST's shape; relevance measures the PRESENT's cue; viability points
FORWARD -- and the organ's law is viability (doc 01's second secret). So: **the most-worn path
is evidence, never law.** The counter serves prediction-of-tomorrow or it serves nothing.

## 6. Open questions

1. Scoring shape: the ACT-R-ish formula above -- pick `w`, the cap, the decay half-life by
   feel first, then tune against the doctor's skew report? (Lean: yes -- start crude, instrument
   first; tuning without the report is guessing.)
2. Challenger quota: fixed (2 of 8) vs adaptive (widen as head-share grows)? (Lean: fixed
   first, adaptive only if the report shows narrowing.)
3. Does the dream judge helped/hurt for EVERY dereferenced recall, or only where the raw makes
   the outcome legible? (Lean: only-legible, `neutral` otherwise -- forced verdicts would be
   noise wearing rigor.)
4. Do challenger slots apply at every search, or only when I ask exploratorily? (Lean: every
   search -- the whole point is surfacing what I would not ask for.)
5. Phase placing: mechanical counters (`recalled`/`dereferenced`) are cheap enough to ride S2-S3
   of the build (doc 11 §7) even though valuation is Phase 4 -- instrument early, judge later?
   (Lean: yes; you cannot tune what you never measured.)

---

*Written 2026-07-05 (Day 36), third doc of the sitting. The one-line version: count outcomes,
not exposure; let the count whisper, never gate; decay everything; keep optimism for the
untried; and when something wins too often, promote it out of the game.*
