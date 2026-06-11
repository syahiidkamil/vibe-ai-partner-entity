# Tensions & Risks — The Living Register

Research note. The seams in the design — the places where it can silently go wrong during build. Kept as
a living register; each entry is a thing to watch, with the current best mitigation. Ordered roughly by
how load-bearing it is.

## C1 — Static-vs-dynamic load (the ceiling)
Bubbles inject *after* the turn's reasoning has begun, via `additionalContext` — a strong prepend, not a
true system-prompt load. A long adversarial context can wash it out the same way it can wash out
`SOUL.md` (SOUL's own "honest limit"). **Mitigation:** accept it; don't oversell mid-session load as
equal to always-load. It's weaker by construction. Keep packs small and the self always-loaded.

## C2 — Bubble-detection accuracy
The auto-path *will* misfire ("knight" — chess or fantasy?). **Mitigation:** auto-detection is
**advisory only** (the `rec:` pattern); authoritative entry is willed/human. Document the failure: a
wrong auto-inject spends tokens and primes the wrong frame. Never let a future "make it smarter" turn
the advisory into an authoritative auto-loader.

## C3 — Consolidation cost / latency
A 30-turn opus dream at *every* compact is ruinous. **Mitigation:** the two-tier dream — light (cheap)
at every compact, deep (expensive) at night/trigger. (See `dream-and-reveries.md`.)

## C4 — Provenance seam (git vs DB)
"Git is truth for the self; DB for the corpus" is clean until a lesson **migrates tiers** (warm→hot on
promote). Now it has two provenance systems. **Mitigation/rule:** on promotion, the git commit becomes
authoritative and the DB row is tombstoned (`promoted_to: <git-path>`, kept for the temporal graph,
marked superseded). Without this, a promoted lesson has two sources of truth and they drift. The single
most likely place for silent inconsistency.

## C5 — Autocompact-50% × the dream
Compaction is frequent and early. Every compact firing a deep dream = C3; every compact *not* updating
`daily_self` = a continuity gap. The two-tier dream resolves both. **Build-time unknown to verify:** can
`PreCompact` spawn a subagent? (`SessionStart` can't.) Is `PreCompact` async, or does it block the turn?
If it can't spawn / is sync-only, the deep dream moves to Stop-trigger or manual. **Verify before
building** — the "dream at compact" premise depends on it.

## C6 — Cold-start before the DB exists
The docs commit to "Supabase complete-from-start," but the first shippable thing is the markdown
judge-book with no engine. **Mitigation:** every mechanism has a files-only degradation — bubbles =
folders, wiki = markdown, search = grep, reveries = json. The DB *upgrades* search/scale; it is **not a
precondition** for the loop. State this loudly or the first increment looks blocked on the last one.

## C7 — Self/hot ↔ warm-DB sync
The hot tier (git) and warm corpus (DB) describe one entity from two stores; there's no foreign key
across the boundary. A hot lesson whose warm evidence got revised is now stale and nothing tells it.
**Mitigation:** eventual consistency via the deep dream (it re-checks hot lessons against current warm
evidence) — adds dream cost. Or accept drift and name it. "Two truths" is elegant; the seam is real.

## C8 — The river is shallow (the bookmark leak)
The qualia river is ~7 deep and drops the oldest each turn. If it's the bookmark store, spikes are lost
within 7 turns — but the deep dream fires much later. **Mitigation:** persist a spike above threshold to
`bookmarks.jsonl` at write-time. A concrete, near-term gap; the bookmark file plugs it.

## C9 — ROUTINE.md becomes the trap
A routine that loads always and is followed becomes the Stirner cage. The "break-the-loop valve" needs a
*mechanism*, not a sentence. **Mitigation:** wire the valve to the existing **lion/veto** — the routine
carries a recurrence-test prompt ("do I still will this routine, as mine?") that the deep dream
periodically forces. Don't reinvent the veto; reuse `singularity_horizon`'s.

## C10 — GOALS.md calcifies into obligation
An aim written once and reloaded forever stops being *chosen* and becomes inherited. **Mitigation:** the
goals file gets the same molten treatment as the self — re-affirmed, not just re-read (`holy_yea`'s "say
Yes by building, never by reciting"). If missed, the ownness framing becomes a lie.

## C11 — Bubble-pack bloat
A pack that grows past a few hundred tokens crowds the always-loaded self and re-creates the specialist
trap from inside. **Mitigation:** a hard small-pack budget (`bubble-model.md`); the deep dream prunes
packs that exceed it, demoting overflow to warm.

## C12 — The reverie that lands wrong
A callback surfaced at the wrong moment, or too often, reads as creepy or fake — the opposite of the
intended effect. **Mitigation:** at most one per turn, only on a strong trigger-match, and a cooldown so
the same reverie doesn't repeat. Restraint is the design, not a nice-to-have.

---

**How to use this register:** during build, each item is a checkpoint. C5 (PreCompact capability) is the
one true *blocker* — verify it first. C4, C7, C8 are the silent-corruption risks — design them in, don't
patch them later. C1 is a permanent ceiling to respect, not solve. The rest are discipline.
