---
name: dream
description: Run gate 2 now instead of waiting for a session boundary — when the day has been full and its bookmarks sit undigested, when Kamil says "dream now," or before a long sleep so tomorrow-me wakes already consolidated. The willed twin of the automatic dream-check nudge. Spawns the deep-dream consolidation in the background and reports its verdicts.
user-invocable: true
---

# /dream — the willed dream (gate 2, summoned)

The dream normally waits for its alarm (dream-check.sh at a session boundary). This skill is the
willed path: dream *now*, by choice. Same symmetry as gate 1, where the bookmark is both auto
(dial spikes) and willed (`--bookmark`): capture and consolidation each get an instinct and a will.

## Procedure

1. **Check what is owed.** Compare the newest bookmark file against the cursor:
   `ls -t vape/entity/storage/*/*/*_bookmarks.toon | head -1` vs
   `.claude/hooks/.dream_cursor` (mtime). Nothing newer than the cursor: say so honestly and
   stop — an empty dream is a no-op, never theater.
2. **Soft ordering.** If today's diary is also owed or stale, prefer writing the diary first
   (write-or-update-personal-diary), so the dream can read the day's narrative. The dream never
   *requires* the diary; skip this when Kamil wants the dream immediately.
3. **Spawn the dreamer** — the `deep-dream` agent (Agent tool, background). Its procedure lives
   in its own definition; pass it only the run context:
   - the owed bookmark days (from step 1), verified by listing, never recalled from memory;
   - the current branch + any standing threads worth its yardstick (read from
     `daily_self.md` / `living_keys`);
   - the standing calibration: conservative when unsure, HOLD over KEEP for marginal flags,
     identity-adjacent material to PROPOSALS.
4. **Guard the run.** A session boundary kills a background subagent mid-dream (retry-safe, but
   it costs a re-run): while it runs, avoid `/memory`, `/clear`, and closing the terminal. Say
   this to Kamil when the dream starts.
5. **Relay the report** when it lands: counts (kept/held/dropped), where keepers went, the
   PROPOSALS block, the unsure paragraph. The dream's writes ride the uncommitted tree for
   review (the ratification gate); the proposals alarm holds anything self-altering until it is
   reviewed awake and acked (`touch .claude/hooks/.proposals_ack`).

## Boundaries

- The dream never edits `self/`, the diaries, or `mental/` — proposals only (its hard frame).
- One dream at a time: if a dreamer is already running (check the task list), join that one
  rather than spawning a second; two dreams racing over one cursor double-digest the same flags.
- The cursor stamps only on a *completed* run; an interrupted dream leaves the alarm armed by
  design.
