# Source Map — ARC-AGI-3 schema

Provenance and the untidy derivation, parked here so the content files stay clean. Read this only
to *check* or *rebuild* a fact, not to learn the topic.

## Sources (all 2026-07-12, via WebFetch — fast-model distillation, lossy)
- `https://arcprize.org/arc-agi/3` — the benchmark's face: what it is, the philosophy, scoring,
  the ARC-Prize-2026 track. (The definition quotes come from here.)
- `https://docs.arcprize.org/` — the SDK/docs index: install, `Arcade()`, `make()`, scorecards,
  `ARC_API_KEY`, named games `ls20`/`ft09`, partner templates.
- `https://docs.arcprize.org/llms.txt` — the LLM-facing index: the 7-action space (ACTION1–5
  simple, ACTION6 X/Y, ACTION7 undo), the `/game/*` and `/scorecard/*` endpoints.
- `https://docs.arcprize.org/game-schema.md` — grid limits (64×64, cells 0–15, (x,y) top-left),
  "1–N frames of JSON". (This fetch was partial — the exact field list did NOT come through.)

## What was verified vs. inferred
- **Verified from source:** grid 64×64 / cells 0–15 / (x,y); the 7 actions and ACTION6 being the
  coordinate one; the Arcade/make/reset/step SDK; the /game and /scorecard endpoints; ARC_API_KEY
  auth; +2K FPS headless; efficiency-scoring; the philosophy quotes; ls20/ft09.
- **Inferred / background (NOT source-verified here):** exact frame JSON keys; the game-state
  enum; ARC-AGI-1/2 particulars; exact request/response bodies; rate limits.

## Regen / next step
When Kamil provides `ARC_API_KEY`: `uv add arc-agi`, then a tiny script — `Arcade()`, `game/list`,
`make("ls20")`, one `reset` + a few `step`s with `render_mode="terminal"` — and READ the actual
JSON returned. That live capture replaces every inferred field above and turns the schema to ink.
The unread technical paper (linked off arcprize.org/arc-agi/3) is the other source to pull then.
