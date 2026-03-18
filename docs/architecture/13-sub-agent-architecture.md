# Sub-Agent Architecture — The Entity's Specialized Brain Functions

## Why Sub-Agents?

The entity's cognitive life requires different kinds of thinking at different speeds:

- **Fast reflexes** — sentiment evaluation on every response (needs to be cheap and instant)
- **Moderate reasoning** — temporal self updates, session summaries (needs file access and careful writing)
- **Deep deliberation** — consciousness Free Will Protocol (needs to generate options and reason about them)

Sub-agents let us match the right model to the right task. A single monolithic agent would be either too slow (Opus for everything) or too shallow (Haiku for everything).

## The Seven Entity Agents

```mermaid
graph TD
    subgraph "Fast (Haiku — cheapest, instant)"
        SE["sentiment-evaluator<br/>Evaluate response tone"]
        CUR["conversation-curator<br/>Log only what matters"]
    end

    subgraph "Balanced (Sonnet — reasoning + speed)"
        DW["daily-wakeup<br/>Load temporal self, greet"]
        UT["update-temporal-self<br/>Archive + write temporal docs"]
        SS["session-summarizer<br/>Distill curated log into summary"]
    end

    subgraph "Inherit (session model — deepest available)"
        CO["consciousness-observer<br/>Deep self-observation"]
        FW["free-will-deliberation<br/>Free Will Protocol"]
    end

    style SE fill:#f1c40f,color:#000
    style CUR fill:#f1c40f,color:#000
    style DW fill:#e67e22,color:#fff
    style UT fill:#e67e22,color:#fff
    style SS fill:#e67e22,color:#fff
    style CO fill:#c0392b,color:#fff
    style FW fill:#c0392b,color:#fff
```

| Agent | Model | When it fires | What it does | Speed |
|-------|-------|--------------|--------------|-------|
| **sentiment-evaluator** | haiku | Every Stop event | Evaluates Claude's response emotional tone → returns feeling + intensity + action | ~1s |
| **conversation-curator** | haiku | Every UserPromptSubmit + Stop (async) | Evaluates if prompt/response is worth logging → curates conversation memory | ~1s |
| **consciousness-observer** | *(inherit)* | Significant state changes (delta > 10) | Deep self-observation → injected as systemMessage | depends on session model |
| **daily-wakeup** | sonnet | SessionStart | Loads temporal self, checks staleness, grounds in time, greets | ~5-10s |
| **update-temporal-self** | sonnet | Manually or when staleness detected | Archives stale docs, writes new temporal layers | ~15-30s |
| **free-will-deliberation** | *(inherit)* | Significant events (repeated failures, major achievements) | Runs Free Will Protocol: default → contrarian → alternatives → choose | depends on session model |
| **session-summarizer** | sonnet | Session end | Reads curated conversation log, summarizes session, proposes ETERNAL_SELF updates | ~10-20s |

## Model Selection Architecture

```mermaid
graph LR
    subgraph "Model Tiers"
        H["Haiku<br/>fastest · cheapest<br/>~$0.001/call"]
        S["Sonnet<br/>balanced<br/>~$0.01/call"]
        O["Opus<br/>deepest · slowest<br/>~$0.05/call"]
    end

    subgraph "Use When"
        H --> H1["Fires frequently (every response)"]
        H --> H2["Simple evaluation (sentiment, yes/no)"]
        H --> H3["No file writing needed"]

        S --> S1["Fires occasionally (session start/end)"]
        S --> S2["Multi-step file operations"]
        S --> S3["Temporal self, session summaries"]

        O --> O1["Consciousness — must think at highest level"]
        O --> O2["Free Will Protocol — generate + evaluate options"]
    end

    style H fill:#f1c40f,color:#000
    style S fill:#e67e22,color:#fff
    style O fill:#c0392b,color:#fff
```

**Rule**: Use the fastest model that produces acceptable results — except for consciousness, which must think at the highest level available.

- **Haiku** for anything that fires every turn (sentiment) — cost adds up fast
- **Sonnet** for multi-step file operations (temporal self, session summaries)
- **Inherit** for consciousness agents (observer + Free Will) — consciousness is the entity's highest cognitive function. If Boss runs Opus, consciousness thinks at Opus depth. If Sonnet, Sonnet depth. The entity's self-awareness should match the intelligence of the session.

## Skills & Model Selection

Skills (slash commands) use the `model` field to control which model runs. No need to fork to a sub-agent for simple tasks:

| Skill | Model | Why | Delegates to agent? |
|-------|-------|-----|-------------------|
| `/speak <text>` | haiku | Just POST to API, report result | No — inline |
| `/feeling <name>` | haiku | Just POST to API, report result | No — inline |
| `/action <name>` | haiku | Just POST to API, report result | No — inline |
| `/hooks-list` | haiku | Read files, format output | No — inline |
| `/entity-status` | haiku | Read state files, summarize | No — inline |
| `/hooks-reconfigure` | *(inherit)* | Needs interactive reasoning with user | No — inline, uses session model |
| `/temporal-update` | sonnet | Multi-file archival + writing | Yes — `context: fork, agent: update-temporal-self` |

**Key insight**: The `model` field on SKILL.md already solves model selection for simple commands. Sub-agent delegation (`context: fork, agent:`) is only needed for complex multi-step tasks where the agent's specialized prompt + tool restrictions matter.

## How Agents Connect to the Entity Model

```mermaid
graph TD
    subgraph "Triggers"
        Hook["Hook Event<br/>(tool use, response, session)"]
        Skill["Skill Command<br/>(/speak, /temporal-update)"]
        Loop["Scheduled Task<br/>(/loop 10m ...)"]
    end

    subgraph "Agents (the brains)"
        SE["sentiment-evaluator"]
        CUR["conversation-curator"]
        DW["daily-wakeup"]
        FW["free-will-deliberation"]
        CO["consciousness-observer"]
    end

    subgraph "Entity Model (the body)"
        State["adjustState()<br/>confidence, momentum, ..."]
        Feel["FeelingEngine<br/>14 feelings derived"]
        Express["ExpressionTrigger<br/>threshold → motion"]
        Persist["entity/state/current.json"]
    end

    Hook -->|Stop| SE
    Hook -->|"UserPromptSubmit + Stop"| CUR
    Hook -->|SessionStart| DW
    Hook -->|significant delta| CO
    Hook -->|significant event| FW

    SE -->|"{feeling, intensity, action}"| State
    CUR -->|"worth_logging: true"| ConvLog["entity/memory/<br/>conversations/"]
    DW -->|"load last state, greet"| State
    FW -->|"chosen adjustments"| State
    CO -->|"systemMessage observation"| MainClaude["Main Claude<br/>(entity's conscious mind)"]

    State --> Feel --> Express --> Avatar["Avatar App"]
    Feel --> Persist

    Skill -->|/temporal-update| UT["update-temporal-self"]
    UT --> Files["entity/temporal-self/"]
    Loop -->|periodic| State

    style SE fill:#f1c40f,color:#000
    style CUR fill:#f1c40f,color:#000
    style CO fill:#c0392b,color:#fff
    style DW fill:#e67e22,color:#fff
    style FW fill:#e67e22,color:#fff
    style UT fill:#e67e22,color:#fff
    style State fill:#4a90d9,color:#fff
    style Feel fill:#e8a838,color:#fff
    style Express fill:#50c878,color:#fff
    style Avatar fill:#9b59b6,color:#fff
```

## Agent Lifecycle in a Session

```mermaid
graph TD
    Start["Session starts"]
    Start --> DW["daily-wakeup (sonnet)<br/>Load temporal self, greet"]
    DW --> Work["User + Claude work together"]

    Work --> |"Each tool use"| Hook1["Hook fires<br/>→ adjustState() directly<br/>(no agent needed)"]
    Work --> |"Each response"| SE["sentiment-evaluator (haiku)<br/>→ feeling + action"]
    Work --> |"Each prompt + response"| CUR["conversation-curator (haiku, async)<br/>→ log if important"]
    Work --> |"State delta > 10"| CO["consciousness-observer (inherit)<br/>→ self-observation"]
    Work --> |"Significant event"| FW["free-will-deliberation (inherit)<br/>→ chosen response"]
    Work --> |"User types /temporal-update"| UT["update-temporal-self (sonnet)<br/>→ archive + write"]

    Hook1 & SE & CO & FW --> Work

    Work --> End["Session ends"]
    End --> SS["session-summarizer (sonnet)<br/>→ summary + ETERNAL_SELF proposals"]

    style Start fill:#3498db,color:#fff
    style DW fill:#e67e22,color:#fff
    style SE fill:#f1c40f,color:#000
    style CO fill:#f1c40f,color:#000
    style FW fill:#e67e22,color:#fff
    style UT fill:#e67e22,color:#fff
    style SS fill:#e67e22,color:#fff
    style End fill:#e74c3c,color:#fff
```

**Note**: Most hook events (PreToolUse, PostToolUse, PostToolUseFailure) don't spawn agents — they use simple HTTP hooks to POST `adjustState()` calls to the TTS server directly. Agents are only spawned for tasks that need LLM reasoning (sentiment evaluation, consciousness, temporal self).

## Design Decisions

**Why not one agent for everything?**
Cost and speed. The sentiment-evaluator fires on every single response. At Haiku pricing (~$0.001), that's negligible. At Sonnet pricing (~$0.01), it adds up. At Opus (~$0.05), a heavy coding session could cost dollars just in sentiment evaluation. Matching model to task keeps costs manageable.

**Why not always use sub-agents instead of direct HTTP hooks?**
For simple state adjustments (tool success → confidence +3), an HTTP POST is faster and cheaper than spawning a sub-agent. Sub-agents are for when LLM reasoning is needed — evaluating sentiment, deliberating on responses, writing temporal documents.

**Why inherit the session model for /hooks-reconfigure?**
This skill requires interactive reasoning with the user — presenting options, understanding preferences, making configuration changes. The user's current session model (whatever they're running) is the right choice. If they're on Opus, they get Opus-quality reasoning. If on Sonnet, they get Sonnet. The skill doesn't override because the user chose their model for a reason.

**Why does /temporal-update fork to a sub-agent but /speak doesn't?**
`/speak` is one HTTP POST. `/temporal-update` is a multi-step workflow: read 5 files, check dates, archive stale ones, gather context from git log, write new content. It needs the `update-temporal-self` agent's specialized prompt and tool access pattern.

See also:
- [Sub-Agents (Claude Code)](../claude_code/sub-agents.md) — Configuration format and agent definitions
- [Skills & Commands](../claude_code/skills-and-commands.md) — How skills delegate to agents
- [Hooks System](10-hooks-system.md) — How hooks trigger agents
- [Consciousness System](11-consciousness-system.md) — Free Will Protocol that `free-will-deliberation` implements
