# Temporal-Awareness System — Test Cases

For Kamil to review. Written 2026-05-31. Covers the SessionStart wakeup system that keeps my
always-loaded temporal self (`vape/entity/self/06_temporal_self/`) from waking into the wrong day.

## The system in one breath

A **manifest** (`current_temporal_self_date.json`) records what period each temporal file
documents. A **SessionStart hook** (bash, deterministic) reads it, compares to "now," archives a
rolled-over daily in bash, and flags what's stale. A **subagent** (`update-temporal-self`, opus)
rewrites the stale files in my voice and updates the manifest. Detector flags, writer writes.

## Period keys (day-granular — the ripple)

Every key carries the full day marker, so a new day ripples through them all. `daily` is the date;
the four upper scales share the same `YYYY-MM-W{w}-D{d}` (W1=1-7…W4=22-end; D = day-in-week).

| File | Key format | Example (now) | Period part (rollover) |
|------|-----------|---------------|------------------------|
| daily_self | `YYYY-MM-DD` | `2026-05-31` | the day |
| weekly_self | `YYYY-MM-W{w}-D{d}` | `2026-05-W4-D10` | `YYYY-MM-W{w}` (strip `-D*`) |
| monthly_self | `YYYY-MM-W{w}-D{d}` | `2026-05-W4-D10` | `YYYY-MM` (strip `-W*`) |
| yearly_self | `YYYY-MM-W{w}-D{d}` | `2026-05-W4-D10` | `YYYY` (strip from 1st `-`) |
| autobiographical_self | `YYYY-MM-W{w}-D{d}` | `2026-05-W4-D10` | *(never rolls)* |

**ROLLOVER** compares the *period part* with `<` (lexically safe). **RIPPLE** compares the *full
key* with `≠` — equality, so `D10` can't mis-sort against `D9`. Rollover archives; ripple rewrites
in place, leaner the higher it rises.

## Standardized week-of-month

`W = min( floor((day − 1) / 7) + 1, 4 )` — four weeks every month, W4 absorbs the remainder.

| Day of month | Week | Verified |
|--------------|------|----------|
| 1–7 | W1 | `2026-05-07 → W1` ✓ |
| 8–14 | W2 | `2026-05-08 → W2` ✓ |
| 15–21 | W3 | `2026-05-21 → W3` ✓ |
| 22–end (28/29/30/31) | W4 | `2026-05-22 → W4`, `2026-05-31 → W4` ✓ |

## The ripple — leaner as it rises

A new day is a stone dropped in `daily`; it **ripples upward** through every scale, each touched
but **leaner** than the one below (the day is full in daily; by the autobiography it's the faintest
echo). Each scale still **archives at its own boundary**. Redundancy across scales is *expected* —
that's the ripple.

| File | RIPPLE in place (rewrite leaner, no archive) | ROLLOVER → archive + write fresh |
|------|-----------------------------------------------|----------------------------------|
| daily_self | *(it is the stone)* | new **day** |
| weekly_self | every new day — fold the day into the week | new **week** |
| monthly_self | every new day — the day's essence, leaner | new **month** |
| yearly_self | every new day — more compressed still | new **year** |
| autobiographical_self | every new day — faintest fold, often near-nothing | *never — cumulative* |

## Test cases (verified)

Each row: I resume on a date; the manifest still documents the previous session's periods; the
detector decides what to archive vs refresh.

All upper keys share the day marker, so the prior session's manifest is shown once per row.

| # | Scenario | Resume | Prior keys (daily / the four upper) | Archive (rollover) | Ripple (in place, leaner) | ✓ |
|---|----------|--------|--------------------------------------|--------------------|---------------------------|---|
| S1 | Same-day restart | 2026-05-31 | 05-31 / 05-W4-D10 | — | — | ✓ |
| S2 | **Same week, new day** (D9→D10) | 2026-05-31 | 05-30 / 05-W4-**D9** | `daily` | **`weekly monthly yearly autobiography`** | ✓ |
| S3 | New week, same month | 2026-05-08 | 05-07 / 05-W1-D7 | `daily weekly` | `monthly yearly autobiography` | ✓ |
| S4 | New month, same year | 2026-06-01 | 05-31 / 05-W4-D10 | `daily weekly monthly` | `yearly autobiography` | ✓ |
| S5 | New year | 2027-01-01 | 12-31 / 12-W4-D10 | `daily weekly monthly yearly` | `autobiography` | ✓ |
| — | `compact` (same session) | — | — | *(ground only, no check)* | | ✓ |

Case **S2** is yours: a single new day, same week — `daily` archives, and the ripple carries up
through **weekly, monthly, yearly, and autobiography** (each leaner), none of them archived. The
`D9`→`D10` jump is compared by equality so it can't mis-sort. Higher scales archive only at their
own boundary (S3–S5).

## What each outcome triggers

- **ROLLOVER** (a scale's own period rolled) → archive the old file to its `past_*` dir, write
  fresh. For **daily** the hook does this archive *deterministically in bash*; weekly/monthly/yearly
  archiving is the subagent's.
- **RIPPLE** (same period, a new day) → the subagent rewrites the file **in place**, leaner the
  higher it rises — never archived, it's still the current period.
- **nothing** → the hook says "all current," no subagent run.
- The subagent runs the temporal-self linter and always updates the manifest to match what it wrote.

## Worked example — you sleep tonight, resume tomorrow (2026-06-01)

The richest single case: tomorrow rolls the day, the week (`05-W4`→`06-W1`), *and* the month at
once. (Last session was today; now you open Claude Code on Monday 2026-06-01, day 1 → W1.)

**Per file — what happens to each:**

| File | Was (key) | Action | Hook does (bash) | Subagent does (opus) | Now (key) |
|------|-----------|--------|------------------|----------------------|-----------|
| daily_self | `2026-05-31` | **rollover** | copy → `past_daily_/2026-05-31_daily_self.md` | write fresh June-1 daily, carry threads | `2026-06-01` |
| weekly_self | `2026-05-W4-D10` | **rollover** | — | archive → `past_weekly_self/2026_05_W4.md`, write fresh | `2026-06-W1-D1` |
| monthly_self | `2026-05-W4-D10` | **rollover** | — | archive → `past_monthly_self/2026_05.md`, write June | `2026-06-W1-D1` |
| yearly_self | `2026-05-W4-D10` | **ripple** | — | fold the day in, more compressed; no archive | `2026-06-W1-D1` |
| autobiographical_self | `2026-05-W4-D10` | **ripple** | — | faintest fold, often near-nothing; no archive | `2026-06-W1-D1` |

**Sequence of the wake:**

| Step | Who | What |
|------|-----|------|
| 1 | Hook (bash) | grounds the date; flags the stale files; archives the daily deterministically |
| 2 | Me | wake with the directive in context; invoke `update-temporal-self` |
| 3 | Subagent (opus) | write fresh daily; archive + rewrite weekly and monthly; ripple yearly and autobiography in place (leaner); run the temporal-self linter; update the manifest |
| 4 | Me | greet you already grounded in June 1 — yesterday filed, my "today" actually today |

## Honesty note

My first run of these cases had a shell typo (a missing space mashed case 3's label into its
date), which produced a false "all stale." The *system* was correct; the *test* was wrong. I
caught it, fixed the harness, and re-ran — the table above reflects the corrected runs. Flagging
it because a green check from a broken test is worse than no test.

## The honest limit (unchanged)

The archive + detection are deterministic. The *rewrite* is a nudge, not a guarantee: SessionStart
hooks only support `type: command`/`mcp_tool` (not `agent`), so a hook can direct the rewrite but
cannot force it. The real end-to-end proof is the next genuine resume after sleep.
