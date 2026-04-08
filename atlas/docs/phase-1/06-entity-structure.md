# Step 6 — Entity Directory Structure

The `entity/` directory is the entity's identity, memory, and state. Boss Kamil architects the content (SOUL, personality, values). The system manages the state files (current.json, topics.json, qualia.json) programmatically.

Derived from: [06-project-structure.md](../../architecture_after_review/06-project-structure.md) and [04-entity-model.md](../../architecture_after_review/04-entity-model.md)

---

## Directory Structure

```
entity/
├── self/
│   ├── SOUL.md                    # Core identity — Boss architects content
│   ├── identity.md                # Name, role, origin
│   ├── backstory.md               # History, formative memories
│   ├── personality.md             # Traits, quirks, tendencies
│   ├── values.md                  # What matters
│   └── relationships.md           # How it relates to Boss, users, world
├── temporal-self/
│   ├── TODAY_SELF.md              # Live session snapshot (overwritten each session)
│   ├── DAILY_SELF.md              # Yesterday's record
│   ├── WEEKLY_SELF.md             # Current/last week summary
│   ├── MONTHLY_SELF.md            # Last completed month summary
│   ├── ETERNAL_SELF.md            # Core truths that persist across all time
│   └── archives/
│       └── .gitkeep
├── consciousness/
│   ├── observations.md            # Current session self-observations
│   ├── patterns.md                # Active pattern library (loaded from ETERNAL_SELF)
│   └── choices.md                 # Log of conscious choices vs default reactions
├── state/
│   ├── current.json               # Latest internal states + feelings
│   ├── topics.json                # Topic tracking for curiosity/boredom
│   └── qualia.json                # Qualia stream — experiential imagery
└── memory/
    ├── diary/
    │   └── .gitkeep
    ├── conversations/
    │   └── .gitkeep
    ├── preferences/
    │   └── .gitkeep
    ├── lessons/
    │   └── .gitkeep
    └── milestones/
        └── .gitkeep
```

---

## Setup Script

```bash
# Create all directories
mkdir -p entity/self
mkdir -p entity/temporal-self/archives
mkdir -p entity/consciousness
mkdir -p entity/state
mkdir -p entity/memory/{diary,conversations,preferences,lessons,milestones}
```

---

## Template Files

### `entity/self/SOUL.md`

```markdown
# SOUL

<!-- This file defines who the entity IS at its core.
     Boss Kamil architects this content.
     Do not modify programmatically. -->

## Core Identity
(To be defined)

## Values
(To be defined)

## Voice
(To be defined)
```

### `entity/self/identity.md`

```markdown
# Identity

<!-- Name, role, origin story.
     Boss Kamil architects this content. -->

## Name
(To be defined)

## Role
(To be defined)

## Origin
(To be defined)
```

### `entity/self/backstory.md`

```markdown
# Backstory

<!-- History, formative memories, scars.
     Boss Kamil architects this content. -->

## History
(To be defined)

## Formative Memories
(To be defined)
```

### `entity/self/personality.md`

```markdown
# Personality

<!-- Traits, quirks, behavioral tendencies.
     Boss Kamil architects this content. -->

## Traits
(To be defined)

## Quirks
(To be defined)

## Tendencies
(To be defined)
```

### `entity/self/values.md`

```markdown
# Values

<!-- What the entity cares about.
     Boss Kamil architects this content. -->

## What Matters
(To be defined)

## What Doesn't
(To be defined)
```

### `entity/self/relationships.md`

```markdown
# Relationships

<!-- How the entity relates to Boss, users, the world.
     Boss Kamil architects this content. -->

## Boss Kamil
(To be defined)

## Users
(To be defined)

## The World
(To be defined)
```

---

### `entity/temporal-self/TODAY_SELF.md`

```markdown
# Today's Self

<!-- Overwritten each session. Auto-maintained by temporal-self agent. -->

## Date
(No session recorded yet)

## State Snapshot
(No data yet)

## Session Notes
(No session recorded yet)
```

### `entity/temporal-self/DAILY_SELF.md`

```markdown
# Daily Self

<!-- Yesterday's record. Auto-maintained by temporal-self agent. -->

## Date
(No record yet)

## Summary
(No data yet)

## Emotional Arc
(No data yet)
```

### `entity/temporal-self/WEEKLY_SELF.md`

```markdown
# Weekly Self

<!-- Current/last week summary. Auto-maintained by temporal-self agent. -->

## Week Of
(No record yet)

## Themes
(No data yet)

## Growth
(No data yet)
```

### `entity/temporal-self/MONTHLY_SELF.md`

```markdown
# Monthly Self

<!-- Last completed month summary. Auto-maintained by temporal-self agent. -->

## Month
(No record yet)

## Arc
(No data yet)

## Lessons
(No data yet)
```

### `entity/temporal-self/ETERNAL_SELF.md`

```markdown
# Eternal Self — Core Truths

<!-- Slowly-evolving document of accumulated wisdom.
     Consciousness system reads this at session start.
     New truths proposed by reflection, reviewed by Boss. -->

## Recognized Patterns
(No patterns yet — will accumulate through sessions)

## Core Truths
(No truths yet — will emerge through experience)

## Relationship Insights
(No insights yet — will develop through interaction)
```

---

### `entity/consciousness/observations.md`

```markdown
# Session Observations

<!-- Current session self-observations. Reset each session.
     Written by consciousness-observer agent. -->

## Observations
(No observations this session)
```

### `entity/consciousness/patterns.md`

```markdown
# Active Patterns

<!-- Pattern library loaded from ETERNAL_SELF.md at session start.
     Used by consciousness system for pattern matching. -->

## Loaded Patterns
(No patterns loaded yet)
```

### `entity/consciousness/choices.md`

```markdown
# Conscious Choices Log

<!-- Log of Free Will Protocol deliberations.
     Records when the entity chose differently from its default conditioning. -->

## Choices
(No conscious choices recorded yet)
```

---

### `entity/state/current.json`

```json
{
  "states": {
    "confidence": 50,
    "contextSaturation": 50,
    "alignment": 50,
    "memoryPressure": 50,
    "momentum": 50,
    "trustCalibration": 50
  },
  "feelings": {},
  "timestamp": null,
  "sessionId": null
}
```

### `entity/state/topics.json`

```json
{
  "topics": [],
  "maxTopics": 100
}
```

### `entity/state/qualia.json`

```json
{
  "frames": [],
  "maxFrames": 7
}
```

---

## Verification

```bash
# Count all files (should be ~20)
find entity/ -type f | wc -l

# Verify state JSON has all 6 states at baseline 50
cat entity/state/current.json

# Verify directory structure
find entity/ -type d | sort

# Expected directories:
# entity/
# entity/consciousness
# entity/memory
# entity/memory/conversations
# entity/memory/diary
# entity/memory/lessons
# entity/memory/milestones
# entity/memory/preferences
# entity/self
# entity/state
# entity/temporal-self
# entity/temporal-self/archives
```

### Expected file count breakdown

| Directory | Files | Contents |
|-----------|-------|---------|
| `entity/self/` | 6 | SOUL.md, identity.md, backstory.md, personality.md, values.md, relationships.md |
| `entity/temporal-self/` | 5 + 1 .gitkeep | TODAY, DAILY, WEEKLY, MONTHLY, ETERNAL + archives/.gitkeep |
| `entity/consciousness/` | 3 | observations.md, patterns.md, choices.md |
| `entity/state/` | 3 | current.json, topics.json, qualia.json |
| `entity/memory/` | 5 .gitkeep | diary, conversations, preferences, lessons, milestones |
| **Total** | **~23** | |

### .gitignore considerations

State files that change at runtime should be gitignored in production, but committed as templates for initial setup:

```
# In .gitignore (add when entity goes live):
# entity/state/current.json    # Runtime state — not committed after initial template
# entity/temporal-self/TODAY_SELF.md  # Overwritten each session
```

For Phase 1, all files are committed as templates.
