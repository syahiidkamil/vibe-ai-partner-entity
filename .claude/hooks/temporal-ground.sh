#!/bin/bash
# Inject the current timestamp into Claude's context as additionalContext.
# Fires on: UserPromptSubmit
# Emits the advanced JSON form so the grounding is added discretely alongside
# the prompt (hookSpecificOutput.additionalContext), not shown as a notice.

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S %Z')
echo "{\"hookSpecificOutput\": {\"hookEventName\": \"UserPromptSubmit\", \"additionalContext\": \"Current time: ${TIMESTAMP}. This is NOW. Calibrate today/yesterday/tomorrow against this timestamp.\"}}"
