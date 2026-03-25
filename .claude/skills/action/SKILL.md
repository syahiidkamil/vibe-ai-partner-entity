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

`/action wave` — avatar plays wave animation

## Error Handling

If action name is not in the valid list, show valid actions. If server is not running, suggest `npm start`.
