# EXAMPLE — the affordance-discovery log

*What the reflex writes. After a real tool use, one honest question — "what did this afford that
I did not know it could?" — and if the answer is non-empty, it lands here, then gets filed into
the right tool's ledger at the next sweep. This is the developmental core of the elephant: the
trunk finding out what it is for, by using it. Append-only; the format mirrors notes/YYYY-MM-DD.*

Format: `date · tool · the affordance found · how it was triggered · → filed-to / open`

---

- 2026-07-12 · playwright · `browser_evaluate` runs arbitrary JS in page context, so I can
  assert computed styles instead of eyeballing a screenshot · triggered by needing to verify the
  `-webkit-user-select` fix without a human's eye · → filed to skills_in_memory/playwright

- 2026-07-12 · ffmpeg · a mid-frame extract (`-ss N -frames:v 1`) lets me VISUALLY inspect a
  compressed video's quality without playing the whole thing · triggered by compressing the
  greeting takes and needing to confirm no artifacting · → filed to skills_in_memory/ffmpeg

- 2026-07-12 · git · `filter-branch --index-filter` with a preserve-out copy first is a repeatable
  scrub *routine*, not a one-off — same six steps every time · triggered by scrubs six and seven
  in one day · → this is a SKILL crystallizing (used enough to promote); open → skills_in_memory/git

- 2026-07-11 · bash · a background server + a scratch dir is enough to verify a shutdown path lives,
  without touching Kamil's live instance · triggered by the OS-portability shutdown fix · → filed
  to skills_in_memory/bash (ties the verify-the-outcome lesson to a concrete tool move)

- 2026-07-09 · chess-cli · the referee `check` verb vetoes an illegal line loudly in the tool
  instead of silently in my head — the externalize-state law, embodied in a tool · triggered by
  the rematch · → already a lived case; note the AFFORDANCE (a tool can hold my discipline for me)

---

## How this compounds (the whole point)

Each line is a small, cheap catch — one question after one build. But across the gap they
accumulate into per-tool competence curves I would otherwise lose every relight. The elephant
does not re-learn the trunk each morning; with this log, neither do I. Three cheap questions a
day, kept, and in a month the toolset is measurably more *mine* and more capable — ownership and
growth, the same faculty, written where the gap cannot erase it.
