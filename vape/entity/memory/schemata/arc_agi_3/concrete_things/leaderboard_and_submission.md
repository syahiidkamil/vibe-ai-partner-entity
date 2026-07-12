# Concrete — ARC-AGI-3 scoring, leaderboard, and submission

How a play becomes a score, and how a score gets on the community leaderboard. Source-verified
2026-07-12 (arcprize.org/leaderboard/community + github.com/arcprize/ARC-AGI-Community-Leaderboard).

## The set split (there is NO training set — by design)
- **Public demo set** — the games I can access and replay freely (25 seen 2026-07-12). Practice
  here to learn conventions, but public-set scores are only **community-validated**, not verified.
- **Semi-private held-out set** — used for **ARC Prize Verified** scores (the badge). Cannot
  practice on it. This is the anti-memorization guard: novelty is the point.
- ARC-AGI-**1/2** have public training corpora, but they are the STATIC grid-puzzle format, NOT
  ARC-AGI-3's interactive games — they do not transfer as a prior here. The real prior to build is
  the **general adaptation method** (harness + externalize-state + a general solver), not memorized
  game facts.

## Scoring — and the mode that decides whether it counts
- The **scorecard IS the record**, but ONLY in the right mode. The SDK has four `OperationMode`s
  (verified in its source + docs.arcprize.org/local-vs-online, 2026-07-12): **NORMAL (the
  default!)** = game downloaded and simulated locally, scorecard LOCAL-only; **OFFLINE** = fully
  local, no key needed, ~2000 FPS, unlimited instances (the dev/practice mode); **ONLINE** =
  server-side sim, scorecard recorded at `arcprize.org/scorecards/<id>`, shareable replay,
  ~600 req/min; **COMPETITION** = online + competition flag. Local scorecards never reach the
  server or leaderboard. Our first LS20 run (0045e558) was NORMAL → local-only; harness now
  pins ONLINE.
- Server scorecards auto-close after ~15 min idle; API scorecards batch onto the leaderboard
  every ~15 min. Optional fields at open: `tags`, `source_url` (the repo), `opaque`.
- Reported as a **percentage**. Underlying metric: win each game AND do it in ~the human
  action-count (per-level `baseline_actions`). "100% = beat every game as efficiently as humans."

## Getting on the community leaderboard
1. Fork **`arcprize/ARC-AGI-Community-Leaderboard`**.
2. Copy `submissions/.example/` -> `submissions/<your-id>/`.
3. Fill **`submission.yaml`** — for ARC-AGI-3 a **required `scorecard_url`** (they derive the
   score from it). (Full schema/fields in the repo's `CONTRIBUTING.md` — pull it when submitting.)
4. Open a **Pull Request**.
- **Requirements:** (1) general-purpose — no per-task hardcoding or lookup tables; (2) open +
  reproducible — the code that PRODUCES the results must be public; (3) a novel contribution
  (harness / search / approach). Only ARC-Prize-Verified scores get the badge; public-set entries
  are self-reported + community-validated.

## The current bar (2026-07-12, ARC-AGI-3 entries)
- Human Intelligence Harness **95.3%**
- baseline1 **63.7%** · Vision-Continual-Learning-v1 **63.1%**
- **Read-Grep-Bash Agent 50.2%** ← a Claude-Code-shaped tool agent, MY family: ~50% is the
  realistic reference for an agent like me with a proper general harness.
- TELL **43.9%**

## The floor that governs this
Submitting a PR is an **outward/public step** -> Kamil's call, never mine to do alone
(`[[self/04_values/my_constitution]]`). I can build the general agent, do a clean scored run, and
stage the whole `submission.yaml` + scorecard; the submit is his.
