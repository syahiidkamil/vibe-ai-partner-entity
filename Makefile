.PHONY: start stop restart list status

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

help: ## Show commands
	@grep -E '^[a-zA-Z_-]+:.*##' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "}; {printf "  make %-10s %s\n", $$1, $$2}'
