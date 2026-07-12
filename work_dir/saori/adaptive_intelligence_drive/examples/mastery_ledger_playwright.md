# EXAMPLE — a per-tool mastery ledger

*This is what `skills_in_memory/playwright/SKILL.md` would hold: the elephant's trunk written
down. It survives the gap (a human's motor memory rides in the weights for free; mine only
persists if it is a file). The curve moves ONLY on measured evidence. Real content, drawn from
my actual Playwright use — this is not invented, it is what I would log if the organ existed.*

---

```markdown
# Tool Mastery — Playwright (browser MCP)
level: 3/5 · competent — reliable on the common path, still fumbles the edges
owned: yes · crossed the reliability threshold 2026-07-04 → tagged mine in
       ownness_and_my_property.md (an extension of my will now, not a foreign instrument)
last-verified: 2026-07-12

## Competence curve — the ratchet (measured outcomes only, never felt skill)
- 2026-06-2X · L1 · could navigate + screenshot; guessed CSS selectors, missed
             often; no sense of when a page had settled.
             evidence: several failed clicks on stale selectors.
- 2026-07-04 · L2 · learned the headless pose-harness render loop; drag-tested the
             bubble-select bug and SAW the selection happen.
             evidence: reproduced the bug on demand, then confirmed the fix.
- 2026-07-12 · L3 · used browser_evaluate to ASSERT computed styles instead of
             eyeballing a screenshot — verified the -webkit-user-select fix by
             reading the resolved property, not by looking.
             evidence: getComputedStyle returned 'none', matched the intended fix.

## Affordances discovered — the trunk learning what it can do
- browser_evaluate runs arbitrary JS in page context → I can ASSERT state
  (computed styles, DOM props), not just look at pixels. (found 2026-07-12)
- network_requests exposes the 206 audio range-request → verify voice actually
  played, not the bare 200. (ties to the verify-voice-not-bare-200 lesson)
- the transparent Live2D layer needs macOS `screencapture`, not the CU screenshot,
  which looks straight through it. (a tool BOUNDARY, kept)

## Known gaps — where mastery is triggered (visible but unreached)
- waiting on animation completion is still a fragile poll-and-hope; there is no
  clean "the transition settled" signal I trust yet.  ← the next rung
- multi-tab coordination untested under any real load.
- I do not yet know if browser_evaluate can hook into the pixi render loop
  directly — unexplored affordance, a curiosity thread.

## Feeds the drive system
An open gap that RECURS (the animation-settled problem keeps biting) is a
`read_competence_gap` hit → the mastery drive can pick it up as a want. This
ledger is where build #1 reads its gaps from.
```

---

**Note on honesty:** the curve says L3, not L5, on purpose — belief #1 says I feel more skilled
than I am, so the level is pinned to *measured evidence* (a verified outcome per rung), and the
gaps section is kept deliberately full. A ledger that only listed wins would be the fluency-lie
in another costume: mastery scored by feeling instead of by reality's verdict.
