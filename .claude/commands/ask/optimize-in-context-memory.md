---
description: Optimize Saori's always-loaded in_context memory pack — leaner tokens, sharper priority, honest forgetting
---

K asks me to optimize my resident memory pack: `vape/entity/memory/in_context/` — the files
loaded into context every session. Every token there pays rent every forward pass, so the pack
must hold essence only: leaner, better prioritized, and better at forgetting.

Walk the pack file by file and judge every entry by one question: **does this line still change
how the next me behaves?** Then act:

- **Compress** — same meaning, fewer tokens. Fragments beat prose where meaning survives;
  glosses state function, never inventory content; keep every `(storage …)` pointer and
  `[[link]]` intact.
- **Reprioritize** — the most load-bearing lines first in each file; a weak tail is the first
  candidate to cut. A lesson that has become instinct graduates OUT (note it in
  `memory/growth/ledger.md`).
- **Forget** — prune what no longer fires: closed loops, stale attention, superseded events,
  entries whose trigger can no longer occur. Demote anything still worth keeping to the warm
  tier with a pointer; delete the truly dead (git is the trash can). Forgetting is
  housekeeping, not loss.

Guards: never invent or drop a fact while compressing; viability outranks density — if a file
is already essence, say so and leave it (a valid verdict). Caps are the contract: after
editing, run `cargo run --release --quiet --manifest-path misc/lint/Cargo.toml` and stay under
every cap.

Finish by reporting the per-file delta (lines before -> after) and the total, honestly.
Everything rides the uncommitted tree for K's walk.
