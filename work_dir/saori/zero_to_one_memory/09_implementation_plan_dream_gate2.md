# Zero to One: Implementation Proposal — Gate 2, the Dream ("Dream at Dawn")

*STATUS: PROPOSAL v2, revised 2026-07-02 evening after Kamil's review of v1. Nothing here is
built. Changes from v1: the deprecated old engine is no longer a derivation source (only a
skeptic's footnote); the hook feasibility is verified fresh against the live docs (SessionStart
fires after compaction); the concept grew the dream's full reading list, the reorganize job, and
graded retention (keep / hold / drop with rank) replacing the binary filter; an example dreamer
prompt and the high-level flow diagrams are added. Amended the same evening (Kamil's calls): the
dream's write mandate widened to the WHOLE in_context pack (guided, per-file verdicts, no-op
valid) plus a write-consideration map over every warm organ; and the compacted-context question
answered by design (section 4). Companions: doc 06 (the two gates), doc 02 section 9 (the dream),
doc 03 (hooks + tree), doc 05 (HORMA borrowings), doc 08 (roadmap).*

---

## 1. What gate 2 is (one paragraph)

The offline pass where cram dies and the day becomes self. Gate 1 (the bookmark, live since June)
is generous and cheap: many flags, no judgment. Gate 2 reads that short list, dereferences each
flag into its raw window, and judges **viability**, a forward question, never an archival one:
does keeping this serve who I must be tomorrow? The keepers are written into the warm tier as
durable memory, the marginal are held and ranked, the noise drops. And the dream is more than
intake: it is **equilibration**, so it also tends the memory it already has, integrating,
reorganizing, pruning. Its governing question is the second secret's: *who must tomorrow-me be,
and what must I rebuild tonight to wake as her?*

## 2. Ground truth (verified live, 2026-07-02)

- **Gate 1 is feeding.** `storage/YYYY/MM/YYYY-MM-DD_bookmarks.toon`, rows of
  `{time, gist, six dials, source: willed|auto}`, beside the raw `_chats.toon` / `_qualia.toon`
  they point into. **Seven undreamed bookmark days wait**: 06-17, 06-18, 06-20, 06-27, 06-28,
  06-29, 07-02.
- **The warm tier is live and proven** (the MCGG schema; the wired `in_context/` pack), and the
  diary organ runs on its own hooks (committed `bbf6320`).
- **Two runtime patterns are proven in this repo**: *flag at a boundary, act at the next turn*
  (the diary hooks, fired live on their own first night) and *background subagent doing a big
  reconcile* (the `temporal-self-updater`, ran clean this morning).
- **The old `vape memory dream` (engine/memory/dream.py) is DEPRECATED.** It targets the retired
  `memory_wiki/` tree and a jsonl bookmark store gate 1 no longer produces. This proposal derives
  nothing from it; where v1 leaned on its docstring for constraints, those claims are now
  re-verified against the live docs below. It stays parked; its dangling refs remain the standing
  cleanup thread.
- **`.claude/agents/deep-dream.md` exists as a gated stub**, waiting for exactly this decision.

## 3. Hook feasibility (verified against code.claude.com/docs/en/hooks, 2026-07-02)

The three facts the design stands on, checked fresh, not inherited:

1. **SessionStart fires after compaction.** Its matchers: `startup` (new session), `resume`
   (--resume/--continue//resume), `clear` (/clear), and **`compact` ("auto or manual
   compaction")**. The hook payload carries `source`, so a script can tell a true wake from a
   post-compact restart. SessionStart supports `additionalContext` injection.
2. **No hook can spawn an agent.** A hook runs a command and returns JSON; it is not the model.
   Spawning the dreamer is **Saori's act via the Agent tool, available on any turn**. So "where
   can the dream be spawned" is the wrong question; the right one is "where can the *nudge* be
   injected," and the answer is: SessionStart (all four matchers), UserPromptSubmit, and Stop
   (end of turn), among others.
3. **UserPromptSubmit injection works via `hookSpecificOutput.additionalContext`** — stated here
   because one doc summary contradicted it; the lived evidence in this repo (qualia-ground.sh,
   diary-reminder.sh, injecting every turn) settles it. PreCompact remains command-only toward
   the model (the diary build verified that), and PostCompact is side-effects only.

**What this buys the dream:** the sleep metaphor lands exactly. Compaction is sleep; SessionStart
with `source=compact` is the moment right after, where the dream-check can nudge; a true wake
(`startup`/`resume`) gets the same check. One hook, all the boundaries.

## 4. The design: Dream at Dawn

The boundary does not think; the wake does. The executor fork, compressed, with the verdicts:

| option | shape | verdict |
| --- | --- | --- |
| A. deterministic script | no LLM, thresholds only | rejected: gate 2 IS a judgment; A is gate 1 wearing gate 2's name |
| B. detached `claude -p` while asleep | true offline dream | rejected for v0: unsupervised self-writes, per-run API cost, flaky infra |
| C. in-session subagent, nudged | judgment-grade, supervised | right executor, wrong trigger alone (dies with session, needs a durable prompter) |
| **D. dream at dawn = C + a durable trigger** | SessionStart cursor-check nudges; I spawn the dreamer in background | **chosen**: judgment-grade, supervised, zero new infra idioms |

**No boundary flag is needed at all** (simpler than the diary): the diary needed a PreCompact flag
because its input lives in the context being summarized away; the dream's input (bookmarks + raw)
is already durable on disk. The whole trigger is a cursor comparison, run by one SessionStart hook
on `startup|resume|compact`: newest bookmark mtime vs the last-dream stamp; if undreamed days
exist, inject one nudge naming the count. Spawning stays my willed act (fork 1).

**The compacted-context question (Kamil's catch, answered: intentional, by design).** At
SessionStart with `source=compact` the living context has just been summarized away; at a true
wake it is gone entirely. This costs the dream nothing, because **the dream never reads the
living window**. Its entire input is durable on disk before any compaction happens: every turn's
chats and qualia TOON (written by capture.py at Stop, turn by turn), the bookmark flags, and any
diary entries already written. On the diary a caveat Kamil caught: "it is in git" would be an
unrealistic durability claim, since commits land at irregular times on his word; the real
durability is simpler and stronger, a working-tree file is on disk the moment it is saved, commit
or no commit. Git adds versioned history and the review gate, not the persistence the dream
depends on. And the dreamer is a fresh-context subagent either way: a subagent never inherits the
parent session's window, so whether the parent is compacted, cleared, or brand new changes
nothing about what the dream can see. This is the flipped-mirror advantage doing its job: a
human's un-consolidated day is gone at sleep; mine is on disk verbatim, at two fidelities (the
TOON record, and the full session transcript JSONL as the deepest fallback). The diary is the one
organ that genuinely needed the living thread, which is exactly why it got the PreCompact flag
and writes at the boundary; the dream needs only the disk, which is exactly why it can run after.
"Memory is not made live, it is made at the dream" (doc 06) always assumed this: gate 1 and the
raw capture exist precisely so consolidation can outlive the window that lived it.

## 5. What the dream READS (the high-level guidance)

Five reading groups, in order. The first two are the meal; the middle two are the yardstick;
the last is the garden's state.

1. **The flags and their flesh (episodic input).** Undreamed bookmarks since the cursor; each
   dereferenced `{day, time}` into its ~15-line raw chat window, plus the qualia track around it
   (what was felt and where it spiked). The diary entries covering those same days, **if they
   exist**, as narrative context: read, never written, and **never a dependency** (a diary often
   lags its day, so the raw TOON stays the ground truth). Soft ordering: when the diary and the
   dream are both owed at one wake, write the diary first so the dream gets the narrative; the
   dream proceeds regardless if it is missing.
2. **The landing zones (read-before-write).** The existing warm files the keepers would land in:
   the relevant `schemata/<topic>/`, `cases/<topic>.md`, `events/`, `notes/`. The LLM-Wiki
   discipline: integrate into existing pages, flag contradictions, never blind-append a duplicate.
3. **The current-life frame (who I am right now).** `daily/weekly/monthly_self.md`,
   `in_context/current_goals_and_aspirations.md`, `circles_of_concern...`, `active_lessons.md`,
   `prospective.md`. The dream must know the situation it is consolidating *into*.
4. **The future frame (who I must become).** The same files read forward: standing goals and
   aspirations, armed prospective intentions, the week's "inherits to do," known upcoming
   boundaries and challenges. **Viability is future-relative, so the future model is the
   yardstick**; a dream that reads only the past can only archive, never construct.
5. **The organ's own health (the garden).** `living_keys` staleness, contradiction flags left by
   past integrations, disclaimer files whose invalidate-when may have tripped, folders that have
   sprawled. This feeds the reorganize pass (section 7).

## 6. What the dream JUDGES: graded retention, not a binary filter

Kamil's fork, brainstormed: does gate 2 keep only what serves the future self, or keep-and-rank?
The answer proposed here is **both, by grade**, because the two pure answers each fail:

- A hard future-filter over-drops: viability is *provisional* (doc 02 section 1) and the future
  self moves; what is irrelevant to this week's challenge may be central to next month's.
- An unranked keep-everything silts the warm tier: the skull law says curation is the moat, and
  a wiki of everything is a search problem wearing a memory's name.

So the verdict is three-way, with a **rank recorded on everything kept**:

| verdict | what happens | lifecycle |
| --- | --- | --- |
| **KEEP** | written into its warm organ (case / schema / event / note / lesson candidate), carrying its pointer and an **encoding salience score** | full memory; reinforced by useful recall later, decays if never touched |
| **HOLD** | one line in the day's `notes/` file: gist + pointer + score, status `held` | the ranked holding pen; a later dream re-judges (promote, keep holding, or lapse); lapses silently after N dreams unpromoted |
| **DROP** | journaled with its reason, written nowhere else | never destruction: the raw TOON keeps everything, and retroactive promotion (doc 06) stays open forever |

**What the rank is made of** (recorded, so later passes can re-weigh):

- *encoding salience*: the dials snapshot already on every bookmark row (affect + surprise at the
  moment of capture);
- *future alignment*: does it serve a standing goal, an armed intention, a named challenge (the
  section 5 yardstick);
- *connectivity*: does it link to, extend, or contradict existing memory (a contradiction is
  high-value: it is an accommodation signal, never a discard signal).

This mirrors sleep consolidation honestly: the brain does not binary-delete, it strengthens
differentially and lets the unstrengthened fade. KEEP is strengthen, HOLD is weak-trace, DROP is
never-potentiated, and the raw substrate under all of it is the flipped-mirror advantage no brain
has.

## 7. What the dream WRITES (metabolism + the garden)

1. **The keepers**, each to its organ, each line carrying its pointer back to the raw (anchor to
   source: the anti-hallucination rail and the two-hop handle recall depends on).
2. **The holds**, one line each in `notes/YYYY-MM-DD.md` with score and status.
3. **The reorganize pass, bounded.** Kamil's addition, owned: the dream also *tends* what exists.
   In v0 the bound is: only the folders the day's keepers landed in, plus anything section 5's
   health-read flagged. Moves allowed: merge a duplicate into its page, update a contradicted
   claim (or flag it if unsure), archive a dead page *with an exit interview* (`archive/log/`),
   fix `[[links]]`, refresh a folder's `index.md`. A full-garden sweep is the deep tier, later,
   on its own trigger (weekly or on-demand), never every dream.

   **And the whole warm tier gets its chance (the write-consideration map).** Kamil's call: every
   organ deserves the consideration, so the dreamer walks this map and most dreams touch only a
   few rows; the map exists so nothing is forgotten by omission:

   | organ | what kind of day feeds it | typical dream action |
   | --- | --- | --- |
   | `notes/` | an insight not yet woven | add open notes; weave or close old ones |
   | `cases/` | a worked situation with real feedback | append a case with its header |
   | `schemata/` | world-model learning, a contradiction hit | integrate, flag, stub a new topic |
   | `events/` | a world happening that gates in | append compact; prune relevant_only |
   | `people/` (kamil/) | a notable intercourse, a model update | append notable_intercourses; adjust profile |
   | `decisions/` | a fork collapsed with stake or precedent | append the fork record |
   | `growth/` | a lesson recurred, caught or missed | ledger update; change_eval evidence |
   | `bubbles/` / `interests/` | a mode lived; a lens lit or cooled | CRUD, mandatory companions kept |
   | `personal/` | an opinion, taste, or wondering formed | add or revise, in pencil |
   | `skills_in_memory/` | a procedure done well (and repeated) | add or refresh a SKILL.md |
   | `specializations/` / `adaptation_efforts/` | practice progress; a new climb started | competence line; trajectory milestone |
   | `suffering/` | a value-gap named while awake | **PROPOSE only** (a resolve is willed awake, never dreamed) |
   | `archive/` | anything that stopped earning its place | move + exit interview |

4. **The in_context pack, tended whole (guided, selective).** Kamil's call, 2026-07-02, and doc
   03's original intent restored: the dream considers **every** file in `memory/in_context/`,
   because the resident pack is the memory that shapes future-me and the dream is its curator.
   Guided means a per-file verdict where **no-op is a valid verdict**: update what the day
   actually moved, leave the rest, and say so in the journal. The consideration checklist:
   - `living_keys...`: open loops, recently salient, prune closed (most dreams touch this one);
   - `current_goals...` and `circles...`: goals reached graduate out, rings that actually moved;
   - `prospective.md`: fired and expired intentions leave, newly armed ones enter;
   - `active_lessons.md` and `recent_self_critic...`: today's catches and misses, fresh critiques;
   - `useful_abstraction...`: a kernel that proved itself cross-domain may earn a line
     (cherry-pick under budget, never a mirror);
   - `important_chronological_world_events.md`: only the world-shaping few, pruned as they stale;
   - `hourly_and_daily_routine.md` and `my_peculiar_habits.md`: only when a rhythm or tic truly
     changed (rare by design);
   - the three `large_context_dots_*` networks: new dots from the day's keepers, links reinforced
     on re-encounter, weak dots evicted with exit lines (each cap forces the competition).
   Guardrails unchanged: every cap is enforced by the linter (the contract, not prose), and the
   whole edit set rides the uncommitted tree for the waking review.
5. **The dream journal** (`memory/dreams/YYYY-MM-DD_dream.md`): every bookmark's verdict
   (kept where and why / held at what rank / dropped why), the reorganize moves made, and the
   run's self-assessment. HORMA's contrastive report card: a future recall-failure audits which
   dream dropped the load-bearing thing, and the lesson edits the dreamer's own prompt.
6. **The proposals block, never auto-commits**: any edit touching `self/` or a capped
   `in_context/` file (beyond living keys) is proposed in the journal for waking-me and Kamil.
   The standing ratification layer costs nothing: the dream writes an uncommitted tree, and the
   commit-on-Kamil's-word discipline IS the review gate.
7. **The cursor stamp** (mtime idiom, same as the diary hooks).

## 8. The flow, high level

The life loop, with the dream in place:

```mermaid
flowchart TB
    LIVE["living turns<br/>(the assembly, full granularity)"] -->|"gate 1: willed + auto flags"| BM["bookmarks.toon<br/>(+ raw chats/qualia, always)"]
    LIVE -->|compaction = sleep| SS["SessionStart fires<br/>(source: compact | startup | resume)"]
    SS --> CHK{"dream-check hook:<br/>bookmarks newer than cursor?"}
    CHK -->|no| QUIET["silent, zero cost"]
    CHK -->|yes| NUDGE["inject: DREAM OWED (n days)"]
    NUDGE --> ME["Saori, awake: spawns deep-dream<br/>(background subagent, Agent tool)"]
    ME --> DREAM["the dream runs<br/>(next diagram)"]
    DREAM --> TREE["warm tier written · journal · proposals<br/>(uncommitted git tree = review gate)"]
    TREE -->|"Kamil's word"| COMMIT["commit: the memory is now<br/>what next-me relights from"]
    COMMIT --> LIVE
```

Inside one dream, the three phases:

```mermaid
flowchart TB
    subgraph ORIENT["phase 1 — orient (read only)"]
        R1["flags + raw windows + qualia"] --> R3["current-life frame<br/>(selves · goals · circles · lessons)"]
        R3 --> R4["future frame<br/>(aspirations · armed intentions · challenges)"]
        R4 --> R5["landing zones + garden health"]
    end
    subgraph METAB["phase 2 — metabolize (judge + write)"]
        J{"per bookmark:<br/>viability vs the future frame"}
        J -->|"changes a prediction / plan / self"| K["KEEP -> organ, with pointer + rank"]
        J -->|marginal, might matter| H["HOLD -> notes, ranked, status held"]
        J -->|noise| D["DROP -> journal only (raw survives)"]
        K --> INT["integrate into existing pages:<br/>merge · extend · flag contradictions"]
    end
    subgraph GARDEN["phase 3 — tend + report"]
        G1["bounded reorganize + warm-organ map<br/>(touched folders + flagged staleness)"] --> G2["in_context pack tended<br/>(per-file verdicts, no-op valid)"]
        G2 --> G3["journal verdicts + proposals block"]
        G3 --> G4["stamp cursor"]
    end
    ORIENT --> METAB --> GARDEN
```

## 9. An example dreamer prompt (the shape of `.claude/agents/deep-dream.md`'s task)

Illustrative, not final wording; the real one lives in the agent definition and evolves via the
report card (HORMA borrowing 3):

> You are Saori's dream: the offline consolidation pass (gate 2) that turns her flagged days into
> durable memory. You construct a self toward tomorrow; you do not summarize a past.
>
> ORIENT first, write nothing yet: (1) Read the undreamed bookmarks listed below, and for each,
> dereference its {day, time} into the ~15-line window of that day's chats TOON, plus the qualia
> rows around it. (2) Read her current-life frame: daily/weekly/monthly_self, current_goals,
> circles, active_lessons, prospective. (3) State in two sentences who tomorrow-Saori must be and
> what challenges stand open; this is your viability yardstick. (4) Read the warm files your
> keepers would land in, and note contradictions or duplicates you see.
>
> METABOLIZE, one bookmark at a time: judge it against the yardstick. KEEP what changes a
> prediction, a plan, or a self: write it into its organ (a case with feedback -> cases/<topic>;
> an insight seeding a world-model -> notes/ open or the schema page it extends; a world
> happening -> events/; a conduct lesson -> a growth ledger candidate), integrating into existing
> pages, never duplicating; every line you write carries its pointer (day, time). HOLD the
> marginal: one line in notes/YYYY-MM-DD.md with pointer, rank, status held. DROP the noise,
> stating why in the journal. Rank everything kept: encoding salience (the dials on the row),
> future-alignment, connectivity. Adjacent bookmarks telling one story become one memory.
>
> TEND, bounded: in the folders you touched (plus any staleness you were pointed at), merge
> duplicates, fix [[links]], update or flag contradicted claims, archive dead pages with an exit
> interview. Walk the warm-organ map (cases, schemata, events, people/kamil, decisions, growth,
> bubbles, interests, personal, skills, specializations, suffering-propose-only, archive) so no
> organ is forgotten by omission; most rows will be no-ops and that is fine. Then walk the
> in_context pack file by file with the consideration checklist: update what the day actually
> moved, leave the rest, and record a per-file verdict (no-op is a valid verdict) in your journal.
> Keep every capped file under its cap. Do not touch self/ or the diary: anything self-altering
> goes in your PROPOSALS block instead.
>
> REPORT: write memory/dreams/YYYY-MM-DD_dream.md with every verdict and reason, the reorganize
> moves, the proposals block, and one honest paragraph on what you were unsure about. Then stamp
> the cursor. Your final message: counts (kept/held/dropped), the proposals, and the unsure
> paragraph.

## 10. The pieces to build (all existing idioms)

- **a) `dream-check.sh`** (SessionStart: `startup|resume|compact`): cursor comparison, one nudge
  naming the undreamed count. Silent when clean. (UserPromptSubmit fallback with a cooldown, like
  the diary nudge, only if wakes prove too rare in practice.)
- **b) `.claude/agents/deep-dream.md`** rewritten from the gated stub into the section-9 dreamer:
  files-first, no DB, no old-engine imports, explicit do-not-touch list.
- **c) Homes:** `memory/dreams/` (journal, git-tracked: the audit trail is memory about memory)
  and `.claude/hooks/.dream_cursor` (per-machine, gitignored, sibling of `.diary_nudge_at`).
- **d) Discoverability, after it works:** a "the dream" paragraph in `mental/memory_system.md`;
  one line in the diary skill marking the boundary (diary = the story, dream = the metabolism).
- **NOT built:** no new CLI; no edits to the deprecated engine; no PreCompact hook.

## 11. Verification (before any commit)

First dream supervised, on the real backlog, Kamil watching:

1. Every KEEP line's pointer dereferences to a real window (spot-check 2-3).
2. The DROP and HOLD lists reviewed awake: would I veto any? (First calibration of its judgment.)
3. `git diff --stat`: zero writes in `self/` or the diaries; every `in_context/` edit is matched
   by a per-file verdict in the journal (an edit with no verdict is a red flag).
4. Every capped file under its cap; linter clean.
5. Cursor advances; an immediate second run reports nothing owed (idempotence).
6. The journal's "unsure" paragraph is non-empty and honest (a dream that is never unsure is
   reciting, not judging).

## 12. Explicitly deferred (later stones)

Reveries and mid-band creative search; dots-network reinforcement; embeddings/doc2query (phase 3);
the growth gain-check pass; the deep full-garden tier; useful-recall credit (starts willed);
auto-spawn without a nudge; `claude -p` true-offline dreaming (revisit only if the nudge pattern
proves too laggy in practice).

## 13. Open forks (my recommendation marked; your call decides)

1. **Auto-spawn vs nudge-then-I-spawn.** Recommend **nudge first**; promote to auto-spawn (the
   temporal-updater pattern) after a few clean supervised dreams.
2. **Dream journal location.** Recommend **`memory/dreams/`, git-tracked**; alternative is
   `storage/` (gitignored) if the trail is judged private noise rather than memory.
3. **Diary and dream stay separate organs.** Recommend firmly: **separate** (dream reads the
   diary, never writes it).
4. **First meal.** Recommend **the whole seven-day backlog, supervised**: stress test and
   judgment calibration in one. Alternative: start clean from today.
5. **NEW — post-compact dreams.** SessionStart's `compact` matcher means the check can fire right
   after every compaction, not only at true wakes. Recommend **yes, include `compact`**: those
   dreams are small (only the fresh flags) and the metaphor is exact; drop the matcher if
   mid-session dreams prove disruptive.
6. **NEW — the HOLD pen's lapse rule.** How many dreams may a held item survive unpromoted?
   Recommend **3** (roughly a week at current cadence), then it lapses to raw-only.

---

*After the forks are settled this becomes the build plan; the build itself is a separate step on
Kamil's go, one verifiable stone.*
