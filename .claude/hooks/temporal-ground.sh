#!/bin/bash
# Inject current timestamp into Claude's context.
# Fires on: UserPromptSubmit

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S %Z')
echo "{\"systemMessage\": \"Current time: ${TIMESTAMP}. This is NOW. Calibrate today/yesterday/tomorrow against this timestamp.\"}"
