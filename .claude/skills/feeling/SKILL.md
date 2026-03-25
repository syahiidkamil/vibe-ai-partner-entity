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

`/feeling curious` — avatar shows curious expression (head tilt)

## Error Handling

If feeling name is not in the valid list, show the valid feelings and ask the user to choose. If server is not running, suggest `npm start`.
