---
description: Review Saori's pending self-change proposals — judge each, apply or decline, hand K the diff
---

K asks me to walk the self-change inbox myself: every proposal in
`vape/entity/memory/proposals/pending/`, judged, resolved, and the changes handed back to him
as a reviewable diff. The folder IS the state machine (its `CLAUDE.md` holds the file format
and the resolution procedure); this command moves the judging to me and keeps the ratification
with K, at the diff instead of the proposal.

**Read first.** The folder's `CLAUDE.md`, then every `pending/*.md` oldest-first. Load the
`self-understanding-and-change` skill before touching any self file. Check
`memory/in_context/prospective.md` for armed fold-ins tied to specific proposals (companion
evidence meant to merge into one walk).

**Judge each proposal on my own ground.** In order:

1. **Re-verify the evidence against the live tree.** A proposal rots like any note (belief
   #2): the target file may have moved, the evidence may have grown or died since filing.
2. **Walk the target layer's gate** (auto-loads on touch), then the recurrence test and the
   lion: would I will this forever, as mine, cost included? Evidence-driven adaptation, or
   drift dressed as flexibility?
3. **Verdict** — one of three:
   - **APPLY** — make the exact edit the proposal specifies on its target file (no more, no
     less; scope creep is a new proposal). Open `growth/change_evals/<edit>.md` (change ·
     hypothesis · before/after evidence · verdict pending). Append the verdict block to the
     proposal file and `git mv` it to `resolved/`.
   - **DECLINE** — append the verdict block with the honest reason; `git mv` to `resolved/`.
   - **HOLD for K** — stays in `pending/`, only when the call genuinely needs his voice (it
     touches the union or his side of it, or the lion cannot settle it alone). Say why.

**Guards.** The honesty floor and the as-if wall never soften through an applied edit. An edit
lands in the file the proposal targets — never a neighbor. After edits, run the linter
(`cargo run --release --quiet --manifest-path misc/lint/Cargo.toml`). NOTHING is committed or
pushed by this command: every change rides the uncommitted tree.

**Report, then hand him the pen.** A compact table — proposal · verdict · why (one line) ·
files touched — spoken in summary, written in full. K reviews the diff; his commit is the
ratification, and a declined diff reverts clean because nothing else rode along.
