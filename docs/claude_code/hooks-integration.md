# Claude Code Hooks Integration

## Overview

Claude Code hooks are event listeners that fire during Claude's workflow. We use them to make the avatar react to Claude's actions in real-time — the avatar watches Claude work and responds with feelings, motions, and speech.

## Hook Events We Use

### Event Lifecycle

```mermaid
graph TD
    UPS["UserPromptSubmit<br/>User sends a message"]
    UPS --> PTU["PreToolUse<br/>Before each tool runs"]
    PTU --> POTU["PostToolUse<br/>After tool succeeds"]
    PTU --> POTUF["PostToolUseFailure<br/>After tool fails"]
    POTU --> STOP["Stop<br/>Claude finishes responding"]
    POTUF --> STOP
    SS["SubagentStart<br/>Subagent spawns"] -.-> PTU

    style UPS fill:#3498db,color:#fff
    style PTU fill:#e67e22,color:#fff
    style POTU fill:#27ae60,color:#fff
    style POTUF fill:#e74c3c,color:#fff
    style STOP fill:#9b59b6,color:#fff
    style SS fill:#95a5a6,color:#fff
```

### Event → Avatar Reaction Mapping

| Event | When | Avatar Reaction |
|-------|------|----------------|
| **SessionStart** | Session begins | Wave hello, set calm feeling |
| **UserPromptSubmit** | User sends message | Nod (listening), set curious feeling |
| **PreToolUse (Bash)** | About to run command | Thinking pose, set focused feeling |
| **PreToolUse (Edit/Write)** | About to edit code | Typing motion, set confident feeling |
| **PostToolUse** | Tool succeeded | Nod, increment momentum state |
| **PostToolUseFailure** | Tool failed | Surprised gasp, set anxious feeling |
| **SubagentStart** | Subagent spawns | Head tilt (delegating), stay calm |
| **Stop** | Response complete | Evaluate sentiment → express appropriate feeling |

## Hook Input Format

Every hook receives JSON on stdin (command hooks) or as POST body (HTTP hooks):

```json
{
  "session_id": "abc123",
  "transcript_path": "/path/to/transcript.jsonl",
  "cwd": "/project/root",
  "hook_event_name": "PreToolUse",
  "tool_name": "Bash",
  "tool_input": {
    "command": "npm test",
    "description": "Run tests"
  }
}
```

Key fields by event:

| Event | Key Fields |
|-------|-----------|
| SessionStart | `session_trigger` ("startup", "resume", "clear", "compact") |
| UserPromptSubmit | `user_prompt` (the user's message text) |
| PreToolUse | `tool_name`, `tool_input` |
| PostToolUse | `tool_name`, `tool_input`, `tool_output` |
| PostToolUseFailure | `tool_name`, `tool_input`, `tool_error` |
| Stop | `stop_hook_active_tool_name`, `stop_response` |
| SubagentStart | `agent_type`, `agent_id` |

## Hook Output Format

Hooks communicate back via JSON on stdout (command) or response body (HTTP):

### Simple Response (Allow/Continue)
```json
{
  "continue": true
}
```

### Response with Side Effects
```json
{
  "continue": true,
  "suppressOutput": true
}
```

### Blocking Response (Stop Claude)
```json
{
  "decision": "block",
  "reason": "Safety check failed",
  "continue": false,
  "stopReason": "Hook blocked this action"
}
```

### PreToolUse Specific (Can Modify Input)
```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow",
    "additionalContext": "This command is safe to run"
  }
}
```

## Recommended Configuration

### .claude/settings.json

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup",
        "hooks": [
          {
            "type": "http",
            "url": "http://localhost:5111/api/hook",
            "timeout": 5
          }
        ]
      }
    ],

    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "http",
            "url": "http://localhost:5111/api/hook",
            "timeout": 3
          }
        ]
      }
    ],

    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "http",
            "url": "http://localhost:5111/api/hook",
            "timeout": 3
          }
        ]
      },
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "http",
            "url": "http://localhost:5111/api/hook",
            "timeout": 3
          }
        ]
      }
    ],

    "PostToolUse": [
      {
        "hooks": [
          {
            "type": "http",
            "url": "http://localhost:5111/api/hook",
            "timeout": 3
          }
        ]
      }
    ],

    "PostToolUseFailure": [
      {
        "hooks": [
          {
            "type": "http",
            "url": "http://localhost:5111/api/hook",
            "timeout": 3
          }
        ]
      }
    ],

    "Stop": [
      {
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Analyze this AI response sentiment. Response: $ARGUMENTS. Return ONLY JSON: {\"feeling\": \"happy|sad|frustrated|curious|proud|anxious|excited|calm|bored|guilty|angry|surprised\", \"intensity\": 0-100, \"action\": \"none|nod|wave|laugh|sigh|celebrate|think\", \"speak\": \"optional short summary for TTS\"}",
            "model": "claude-haiku-4-5-20251001",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

### How the Server Handles Hook Events

The TTS server receives hook events and translates them to avatar commands:

```mermaid
graph TD
    Hook["Hook Event<br/>(HTTP POST /api/hook)"]
    Hook --> Parse["Parse event type<br/>+ tool name"]

    Parse -->|SessionStart| A1["POST /api/feeling {happy}<br/>POST /api/action {wave}"]
    Parse -->|UserPromptSubmit| A2["POST /api/feeling {curious}<br/>POST /api/action {nod}"]
    Parse -->|PreToolUse:Bash| A3["POST /api/feeling {focused}<br/>POST /api/action {think}"]
    Parse -->|PostToolUseFailure| A4["POST /api/feeling {anxious}<br/>POST /api/action {gasp}"]
    Parse -->|Stop + sentiment| A5["POST /api/feeling {result}<br/>POST /api/action {result}"]

    A1 & A2 & A3 & A4 & A5 --> WS["WebSocket broadcast<br/>→ Avatar App"]

    style Hook fill:#27ae60,color:#fff
    style WS fill:#9b59b6,color:#fff
```

## Why HTTP Hooks Over Command Hooks?

| Factor | Command (shell) | HTTP (server) |
|--------|----------------|---------------|
| Cross-platform | Needs bash (Windows: WSL) | Works everywhere |
| Latency | Fork process + parse | Single HTTP POST |
| State | Stateless per invocation | Server has full state |
| Debugging | Print to stderr | Server logs |
| Dependencies | Shell scripting | Already running server |

We prefer HTTP hooks because our TTS server is already running. No need for intermediate shell scripts.

## Why Prompt Hooks for Stop Event?

The `Stop` event carries Claude's full response. A prompt hook can analyze sentiment using a fast model (Haiku) without us writing sentiment analysis code. The model returns structured JSON with feeling + action, which the server forwards to the avatar.

This is the **key innovation**: using an LLM to evaluate another LLM's emotional tone, then driving a virtual body from that evaluation.

## Exit Codes (Command Hooks)

If using command hooks as fallback:

| Exit Code | Meaning | Effect |
|-----------|---------|--------|
| 0 | Success | Parse JSON output, continue |
| 2 | Block | Stop Claude, show stderr as error |
| Other | Error | Log warning, continue |

## Environment Variables Available in Hooks

| Variable | Value |
|----------|-------|
| `$CLAUDE_PROJECT_DIR` | Project root directory |
| `$CLAUDE_ENV_FILE` | Path to write env vars (SessionStart only) |
| `$CLAUDE_PLUGIN_ROOT` | Plugin directory (if from plugin) |
| `$CLAUDE_PLUGIN_DATA` | Plugin data directory (if from plugin) |
