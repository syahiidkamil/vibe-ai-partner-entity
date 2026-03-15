CLI = node $(dir $(abspath $(lastword $(MAKEFILE_LIST))))live-ai-partner-avatar/desktop/cli.js

.PHONY: start stop restart list status normal angry sad surprised blushing cry mad say help

start: ## Start avatar (single instance)
	@if pgrep -f "Electron\.app.*MacOS/Electron \." > /dev/null 2>&1; then \
		echo "Avatar already running. Use 'make restart' or 'make stop' first."; \
	else \
		cd $(dir $(abspath $(lastword $(MAKEFILE_LIST))))live-ai-partner-avatar/desktop && npx electron . &> /dev/null & \
		echo "Avatar started."; \
	fi

stop: ## Stop all avatar instances
	@pkill -f "Electron\.app.*MacOS/Electron \." 2>/dev/null && echo "Avatar stopped." || echo "No avatar running."

restart: ## Restart avatar
	@pkill -f "Electron\.app.*MacOS/Electron \." 2>/dev/null && sleep 1 || true
	@cd $(dir $(abspath $(lastword $(MAKEFILE_LIST))))live-ai-partner-avatar/desktop && npx electron . &> /dev/null &
	@echo "Avatar restarted."

list: ## List running avatar processes
	@pgrep -lf "Electron\.app.*MacOS/Electron \." 2>/dev/null || echo "No avatar running."

status: ## Show avatar status
	@COUNT=$$(pgrep -cf "Electron\.app.*MacOS/Electron \." 2>/dev/null); \
	echo "Instances: $$COUNT"

## --- Expressions ---
normal: ## Expression: normal
	@$(CLI) normal
angry: ## Expression: angry
	@$(CLI) angry
sad: ## Expression: sad
	@$(CLI) sad
surprised: ## Expression: surprised
	@$(CLI) surprised
blushing: ## Expression: blushing
	@$(CLI) blushing
cry: ## Expression: cry (alias for sad)
	@$(CLI) cry
mad: ## Expression: mad (alias for angry)
	@$(CLI) mad

say: ## Say something: make say m="Hello"
	@$(CLI) say $(m)

help: ## Show commands
	@grep -E '^[a-zA-Z_-]+:.*##' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "}; {printf "  make %-12s %s\n", $$1, $$2}'
