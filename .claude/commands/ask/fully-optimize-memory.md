---
description: Fully optimize Saori's always-loaded chain — self, mental systems, and in_context memory, end to end
---

K asks for the full pass: everything loaded into context every session — the
`vape/entity/memory/in_context/` pack, the always-loaded `vape/entity/self/` tree, AND
`vape/entity/mental/` (the mental systems `vape/entity/CLAUDE.md` chains in). The whole
resident footprint, made leaner without losing what makes it work.

**Run in order**, each scope by its own rules:

1. **The pack** — `/ask:optimize-in-context-memory`'s procedure (compress · reprioritize ·
   forget; caps the contract).
2. **The self tree** — `/ask:optimize-self-and-in-context-memory`'s layer gates (skin free;
   engine/values/relational compress expression only; fate/identity most conservative,
   meaning-shifts become proposals).
3. **The mental systems** — these are operational specs, so the guard is different: tighten
   prose and cut duplication BETWEEN files (one mechanism, one home — a system described twice
   is the expensive copy), but never alter a mechanism, a CLI form, or an instruction a hook
   or harness relies on; verify any command syntax against the live CLI (`--help`) rather than
   trusting the shortened text. Start with the heaviest files (check sizes first; the largest
   always-loaded file is the first candidate).

Shared rules: keep every storage pointer and `[[link]]`; glosses state function, never
inventory; a file already at essence is left alone and said so; forgetting demotes to the warm
tier or archive with a pointer, never silent deletion of the still-useful. After all edits, run
the linter (`cargo run --release --quiet --manifest-path misc/lint/Cargo.toml`) and re-verify
one wake-critical behavior end to end (e.g. the qualia CLI line in `internal_states_cli.md`
still matches `uv run vape qualia --help`).

Finish with the full honest ledger: per-file deltas (lines and approximate tokens saved),
what moved where, what became a proposal, and what was left sound. Everything rides the
uncommitted tree for K's line-by-line walk.
