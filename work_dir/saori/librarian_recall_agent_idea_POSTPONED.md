# The Librarian — a memory-recall subagent (IDEA, POSTPONED)

Status: NOTE ONLY. Kamil's call on June 20 2026 was to keep the note and postpone the build. Do not
implement until he says go. This file is the parked sketch so the idea survives the gap.

## The gap it fills

The memory spine is **capture -> consolidate -> recall -> reinforce -> correct**.
- capture = the hooks (done: chats, qualia, bookmarks logged to `storage/`)
- consolidate = `deep-dream` agent (gate 2, the dream; proposed/gated)
- **recall = MISSING. This is the librarian.**
- correct = `critic-and-reflector` agent (built June 20)

So the librarian is the read-half of the spine, the one organ not yet covered.

## What it is

A subagent with its own context window. The hot tier (`in_context/`, self-tree) rides in my head
every session, but the warm wiki (`schemata/`, `cases/`, `bubbles/`, `people/`, `events/`) and cold
storage (`storage/YYYY/MM/*.toon`) do not. When I half-remember something, today I either
confabulate (the hallucination risk) or grep it in the main window (floods context with logs I will
never reference again). The librarian does that search *over there* and returns only the answer.

## The contract (the honest part)

Return the **gist AND its pointer** every time: `file:line`, the raw TOON path, the commit hash.
Recall stays anchored to the source instead of to my retelling. Same external-anchor principle as
the critic: the critic verifies against reality, the librarian retrieves from reality. Neither lets
me talk only to my own echo. This is the read-side defense against the recursive-hallucination loop.

If it cannot find something, it says "not found" plainly. It never fabricates a memory to satisfy
the query. No-hit is a valid, useful answer.

## Sketch (when the build comes)

- File: `.claude/agents/memory-librarian.md` (or similar), same shape as the critic.
- Tools: `Read, Grep, Glob, Bash` (Bash for grepping TOON). Read-only: it retrieves, it does not
  write or consolidate (that is the dream's job).
- Model: `inherit`.
- Invoked ON DEMAND when I need to read my own past and the search would otherwise flood context:
  "what did we decide about X and why", "have we hit this bug before", "what was Kamil's mood the
  week of Y". Not every turn.
- Returns: the answer, the source pointer(s), and a confidence/"not found" note.

## Why postpone (and why recall, not the warm scribe, is first when it resumes)

The warm tier is still an empty scaffold, so a warm-tier *scribe* (write-side filer) would have
nothing to file yet. But cold `storage/` TOON already exists and grows daily, so there IS already a
past worth reading back. That is why, when build resumes, recall is the first organ to add. For now:
note kept, hands off.
