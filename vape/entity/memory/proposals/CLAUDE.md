# Proposals — The Self-Change Inbox

One file per proposed change to the **gated self only** (`vape/entity/self/` layers 01-05, plus
the other hard-frame files: `vape/entity/CLAUDE.md`, `mental/`). Explicitly NOT for
`memory/in_context/` or the warm tier: those are the memory organ's own domain — the dream and
awake-Saori tend them directly, guarded by the linter caps and the uncommitted-tree review
(Kamil's call, 2026-07-03: rigid where identity lives, fluid where memory lives). The folder IS
the state machine, so no regex and no ack stamp are needed anywhere:

- `pending/` — open proposals. The ratification alarm (`self-proposals-check.sh`) fires at every
  session boundary while ANY file sits here; it silences itself the moment the folder is empty.
- `resolved/` — where a reviewed proposal moves (created on first use), with its verdict block
  appended: `APPLIED` (what was edited, which change_eval opened) or `DECLINED` (the reason).
  Nothing is deleted; the inbox empties, the paper trail accumulates.

## Who writes here

- **The dream** (deep-dream agent): anything identity-adjacent it meets goes here as a file,
  never into `self/` (its hard frame). Its journal narrates and references the filename; the
  journal itself stays immutable.
- **Awake-Saori** may also file one directly (a lived insight worth a gated change, parked for
  a proper review rather than edited in the moment's heat).

## File format (compact)

```
# Proposal: <title>
- born: YYYY-MM-DD (<by: first dream | saori | ...>) · journal: <path, if dream-born>
- target: <file path> (layer NN)

## Proposal
<what should change, concretely>

## Evidence
<pointers: cases, diaries, storage timestamps>
```

## Resolution (the awake review, Saori + Kamil)

Walk the target layer's gate (auto-loads on touch) + the recurrence test + the lion; then either
apply (edit the self file by hand, open `growth/change_evals/<edit>.md`) or decline; append the
verdict block; `git mv` the file to `resolved/`. The alarm quiets itself when pending/ is empty.
