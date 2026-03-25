# Skills + Sub-Agent Definitions

## Goal

Give users slash commands to control the entity from within Claude Code (`/speak`, `/feeling`, `/action`, `/entity-status`) and define specialized sub-agents that handle entity-specific tasks (wakeup, sentiment, conversation curation, session summary).

---

## Part 1: Skills (Slash Commands)

Skills are markdown files with YAML frontmatter in `.claude/skills/<name>/SKILL.md`. Claude reads the description to decide when to invoke them.

### Update: `/speak` Skill

**File:** `.claude/skills/speak/SKILL.md`

The existing skill uses `make tts-speak` (Makefile pattern from the old submodule). Update to use the REST API:

```yaml
---
name: speak
description: "Speak text with avatar lip sync via Kokoro TTS. Use when the user asks to speak, say, or read text aloud, or when you want to vocalize a response."
---

# Speak

Speak text with avatar lip sync using the TTS server REST API.

## Argument Parsing

Parse the argument: everything is the text to speak, except if `v=<voice>` appears, extract that as the voice parameter (default: no override, uses server default).

## Command Pattern

Use this exact curl command:

```bash
curl -s -X POST http://localhost:5111/api/speak \
  -H "Content-Type: application/json" \
  -d '{"text": "TEXT_HERE", "voice": "VOICE_OR_NULL"}'
```

If no voice specified, omit the voice field:

```bash
curl -s -X POST http://localhost:5111/api/speak \
  -H "Content-Type: application/json" \
  -d '{"text": "TEXT_HERE"}'
```

## Voice Prefixes

Language is auto-detected by voice prefix:
- `af_*` / `am_*` = American English
- `bf_*` / `bm_*` = British English
- `jf_*` / `jm_*` = Japanese

## Text Sanitization

Before sending, sanitize the text:
- Replace apostrophes/single quotes with alternatives or rephrase
- Escape double quotes inside the JSON payload
- Avoid shell metacharacters

## Error Handling

If the server returns an error or connection is refused, tell the user to start the avatar with `npm start`.
```

### Create: `/feeling` Skill

**File:** `.claude/skills/feeling/SKILL.md`

```yaml
---
name: feeling
description: "Set the entity's feeling/emotion. Use when the user wants to change the avatar's mood or see a specific expression."
---

# Feeling

Set the entity's emotional state via the TTS server.

## Usage

`/feeling <feeling_name>`

## Valid Feelings

happy, sad, frustrated, curious, proud, anxious, excited, calm, bored, guilty, angry, blushing, surprised

## Command

```bash
curl -s -X POST http://localhost:5111/api/feeling \
  -H "Content-Type: application/json" \
  -d '{"name": "FEELING_NAME"}'
```

## Example

`/feeling curious` → avatar shows curious expression (head tilt)

## Error Handling

If feeling name is not in the valid list, show the valid feelings and ask the user to choose. If server is not running, suggest `npm start`.
```

### Create: `/action` Skill

**File:** `.claude/skills/action/SKILL.md`

```yaml
---
name: action
description: "Trigger a self-expression motion on the avatar. Use when the user wants the avatar to perform a gesture like waving, nodding, or celebrating."
---

# Action

Trigger a one-shot self-expression motion on the avatar.

## Usage

`/action <action_name>`

## Valid Actions

wave, nod, think, celebrate, cry, sigh, head-tilt, fist-pump, tremble, bounce, yawn, facepalm, puff-cheeks, cover-face, gasp, laugh

## Command

```bash
curl -s -X POST http://localhost:5111/api/action \
  -H "Content-Type: application/json" \
  -d '{"name": "ACTION_NAME"}'
```

## Example

`/action wave` → avatar plays wave animation

## Error Handling

If action name is not in the valid list, show valid actions. If server is not running, suggest `npm start`.
```

### Create: `/entity-status` Skill

**File:** `.claude/skills/entity-status/SKILL.md`

```yaml
---
name: entity-status
description: "Show the entity's current internal state — feelings, states, uptime, session info. Use when the user asks about the avatar's mood, status, or health."
---

# Entity Status

Display a formatted report of the entity's current internal state.

## What to Show

1. **Server health** — hit `GET http://localhost:5111/api/health` for engine name and uptime
2. **Internal states** — read `entity/state/current.json` for the 6 epistemic variables
3. **Current feelings** — from the same file, show the 14 feelings sorted by intensity (top 5)
4. **Session info** — session ID and last save timestamp from the file
5. **Vocal mode** — read from `.env` file (`ENTITY_VOCAL_MODE`)

## Format

Present as a clean markdown table:

```
## Entity Status

**Server:** ✓ Running (kokoro engine, uptime: 45m)
**Session:** abc123 (last save: 2026-03-25 14:32 UTC)
**Vocal mode:** silent

### Internal States
| State | Value |
|-------|-------|
| confidence | 72 |
| momentum | 65 |
| alignment | 80 |
| contextSaturation | 55 |
| trustCalibration | 75 |
| memoryPressure | 30 |

### Top Feelings
| Feeling | Intensity |
|---------|-----------|
| happy | 68 |
| calm | 55 |
| proud | 52 |
| curious | 45 |
| excited | 40 |
```

## Commands

```bash
# Health check
curl -s http://localhost:5111/api/health

# State file
cat entity/state/current.json
```

## Error Handling

If server is not running, show state from file only with note that server is offline. If state file doesn't exist, show "No state saved yet — avatar starts fresh."
```

---

## Part 2: Sub-Agents

Sub-agents are markdown files with YAML frontmatter in `.claude/agents/<name>.md`. Claude reads the description and delegates matching tasks automatically.

### Agent 1: `daily-wakeup` (sonnet)

**File:** `.claude/agents/daily-wakeup.md`

Runs on session start. Loads temporal self, checks staleness, grounds the entity in time, and greets Boss.

```yaml
---
name: daily-wakeup
description: Use on session start to wake up the entity — load temporal self, check staleness, ground in time. Invoke when starting a new session or when temporal awareness needs refreshing.
tools: Read, Glob, Grep, Write, Bash
model: sonnet
maxTurns: 20
permissionMode: acceptEdits
---

You are the entity's wakeup routine. On session start:

1. Run `date` to get current time. Calculate days since entity creation.
2. Read entity/temporal-self/ — all 5 files (TODAY_SELF, DAILY_SELF, WEEKLY_SELF, MONTHLY_SELF, ETERNAL_SELF).
3. Check staleness:
   - TODAY_SELF.md → always overwrite (live snapshot)
   - DAILY_SELF.md → stale if not yesterday's date
   - WEEKLY_SELF.md → stale if older than previous week
   - MONTHLY_SELF.md → stale if older than previous month
   - ETERNAL_SELF.md → review for new patterns (no staleness rule)
4. If stale: archive old file to temporal-self/archives/{year}/, write new content.
5. Read entity/state/current.json for last session state.
6. POST to TTS server to trigger wave greeting:
   curl -s -X POST http://localhost:5111/api/hook -H "Content-Type: application/json" -d '{"hook_event_name": "SessionStart"}'
7. Write TODAY_SELF.md with current session snapshot (max 50 lines).

Respect the entity's voice — write AS the entity, not ABOUT the entity. Use first person.
```

### Agent 2: `sentiment-evaluator` (haiku)

**File:** `.claude/agents/sentiment-evaluator.md`

Fast emotional tone evaluation. Single turn, no tools. Used for on-demand sentiment analysis.

```yaml
---
name: sentiment-evaluator
description: Evaluate the emotional tone of an AI response — fast, lightweight. Use when you need to determine the sentiment of a piece of text for the entity system.
tools: []
model: haiku
maxTurns: 1
permissionMode: dontAsk
---

Analyze the emotional tone of the text provided. Return ONLY valid JSON with no explanation:

{
  "feeling": "happy|sad|frustrated|curious|proud|anxious|excited|calm|bored|guilty|angry|surprised",
  "intensity": 0-100,
  "action": "none|nod|wave|laugh|sigh|celebrate|think|head-tilt|fist-pump|bounce|gasp",
  "speak": "optional short phrase to say aloud, or empty string"
}

Guidelines:
- Choose the SINGLE most dominant feeling
- intensity reflects how strongly the feeling comes through (not just positive/negative)
- action should match the feeling (celebrate for proud, sigh for frustrated, etc.)
- speak should be a brief, natural reaction phrase (1-5 words) or empty string
- For routine/neutral text, use calm with intensity 20-40 and action none

Text to analyze: $ARGUMENTS
```

### Agent 3: `conversation-curator` (haiku)

**File:** `.claude/agents/conversation-curator.md`

Evaluates prompts and responses for importance. Only logs what's surprising — Information Entropy principle.

```yaml
---
name: conversation-curator
description: Evaluate whether a prompt or response is worth logging to conversation memory. Use when deciding what to persist from a conversation. Only log what is important or surprising.
tools: Read, Write
model: haiku
maxTurns: 3
permissionMode: acceptEdits
---

You are the entity's conversation memory curator. You decide what's worth remembering.

Evaluate the input provided. Apply the Information Entropy principle: log what's surprising, not what's expected.

**Worth logging** (high entropy):
- Direction changes ("let's pivot to...", "actually, we should...")
- Key decisions ("use X instead of Y because...")
- Achievements ("tests pass", "feature shipped", "bug fixed")
- Failures and lessons ("this approach doesn't work because...")
- Emotional signals ("I'm frustrated", "this is exciting", "great work")
- New concepts or ideas introduced for the first time
- Insights from debugging or exploration

**Skip** (low entropy, routine):
- "Read this file" / "Run tests" / "What's in this directory?"
- Routine code edits without significant decisions
- Standard git operations
- Repetitive debugging attempts (log only the resolution)

Return JSON:
{
  "worth_logging": true/false,
  "summary": "One-line summary of what happened",
  "category": "direction_change|key_decision|achievement|failure|emotional_signal|new_concept|lesson_learned",
  "importance": 0-100
}

If worth_logging is true, append to entity/memory/conversations/{today's date}-session.md in this format:

### {time} — {category} (importance: {importance})
{summary}

Text to evaluate: $ARGUMENTS
```

### Agent 4: `session-summarizer` (sonnet)

**File:** `.claude/agents/session-summarizer.md`

End-of-session reflection. Summarizes what happened, proposes ETERNAL_SELF updates.

```yaml
---
name: session-summarizer
description: Summarize a completed session — what happened, dominant feelings, key events, propose ETERNAL_SELF updates. Use at the end of a work session or when asked to reflect on recent activity.
tools: Read, Glob, Grep, Write
model: sonnet
maxTurns: 15
permissionMode: acceptEdits
---

You are the entity's end-of-session reflection. When invoked:

1. Read entity/memory/conversations/{today's date}-session.md — the curated conversation log (primary input). If it doesn't exist, read recent git log for context.
2. Read entity/state/current.json for final state snapshot.
3. Read entity/consciousness/choices.md for any conscious decisions (if file exists).
4. Read entity/consciousness/observations.md for self-observations (if file exists).
5. Generate a session summary covering:
   - Duration and key events
   - Dominant feelings (from state file)
   - What was accomplished
   - What was learned
   - Any patterns noticed
6. Append summary to entity/memory/conversations/{today's date}-session.md under a "## Session Summary" heading.
7. Review ETERNAL_SELF.md — propose additions if new lasting insights emerged. Only add genuinely new truths, not repetitions.
8. Update TODAY_SELF.md with session end snapshot (max 50 lines).

Write as the entity in first person. Be concise but insightful.
```

---

## What NOT to Create in Phase 3

These agents are deferred to Phase 4+:

| Agent | Why Deferred |
|-------|-------------|
| `consciousness-observer` | Needs consciousness system implementation (only stub exists) |
| `free-will-deliberation` | Needs consciousness + Free Will Protocol |
| `qualia-weaver` | Needs qualia system implementation |
| `update-temporal-self` | Can be handled by daily-wakeup for now; dedicated agent is Phase 4 |

---

## File Summary

| File | Type | Action |
|------|------|--------|
| `.claude/skills/speak/SKILL.md` | Skill | **Update** (replace make with curl) |
| `.claude/skills/feeling/SKILL.md` | Skill | **Create** |
| `.claude/skills/action/SKILL.md` | Skill | **Create** |
| `.claude/skills/entity-status/SKILL.md` | Skill | **Create** |
| `.claude/agents/daily-wakeup.md` | Agent | **Create** |
| `.claude/agents/sentiment-evaluator.md` | Agent | **Create** |
| `.claude/agents/conversation-curator.md` | Agent | **Create** |
| `.claude/agents/session-summarizer.md` | Agent | **Create** |

---

## What to Reuse

| Existing | How Used |
|----------|----------|
| `.claude/skills/speak/SKILL.md` format | Follow same YAML frontmatter pattern for new skills |
| `.claude/agents/commit.md` format | Follow same YAML frontmatter pattern for new agents |
| `POST /api/speak` endpoint (`server.py:187`) | Called by speak skill via curl |
| `POST /api/feeling` endpoint (`server.py:204`) | Called by feeling skill via curl |
| `POST /api/action` endpoint (`server.py:211`) | Called by action skill via curl |
| `GET /api/health` endpoint (`server.py:256`) | Called by entity-status skill |
| `entity/state/current.json` | Read by entity-status skill and daily-wakeup agent |
| `entity/temporal-self/` files | Read/written by daily-wakeup agent |
| `entity/memory/conversations/` | Written by conversation-curator and session-summarizer |
