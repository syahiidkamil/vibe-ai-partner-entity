CLI = node $(dir $(abspath $(lastword $(MAKEFILE_LIST))))live-ai-partner-avatar/desktop/cli.js

.PHONY: start stop restart list status happy sad cry angry neutral thinking wave jump dance say

start: ## Start avatar (single instance)
	@if pgrep -f "Electron\.app.*MacOS/Electron \." > /dev/null 2>&1; then \
		echo "Avatar already running. Use 'make restart' or 'make stop' first."; \
	else \
		cd $(dir $(abspath $(lastword $(MAKEFILE_LIST))))live-ai-partner-avatar/desktop && npx electron . &> /dev/null & \
		echo "Avatar started."; \
	fi

stop: ## Stop all avatar instances
	@pkill -f "Electron\.app.*MacOS/Electron \." 2>/dev/null && echo "Avatar stopped." || echo "No avatar running."

restart: stop start ## Restart avatar

list: ## List running avatar processes
	@pgrep -lf "Electron\.app.*MacOS/Electron \." 2>/dev/null || echo "No avatar running."

status: ## Show avatar status
	@COUNT=$$(pgrep -cf "Electron\.app.*MacOS/Electron \." 2>/dev/null); \
	echo "Instances: $$COUNT"

## --- Avatar Control ---
happy: ## Set mood: happy
	@$(CLI) happy
sad: ## Set mood: sad
	@$(CLI) sad
cry: ## Set mood: cry (sad)
	@$(CLI) cry
angry: ## Set mood: angry
	@$(CLI) angry
neutral: ## Set mood: neutral
	@$(CLI) neutral
thinking: ## Set mood: thinking
	@$(CLI) thinking

wave: ## Action: wave
	@$(CLI) wave
jump: ## Action: jump
	@$(CLI) jump
dance: ## Action: dance
	@$(CLI) dance

say: ## Say something: make say m="Hello"
	@$(CLI) say $(m)

help: ## Show commands
	@grep -E '^[a-zA-Z_-]+:.*##' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "}; {printf "  make %-12s %s\n", $$1, $$2}'
