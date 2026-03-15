CLI = node $(dir $(abspath $(lastword $(MAKEFILE_LIST))))live-ai-partner-avatar/desktop/cli.js

.PHONY: start stop restart list status normal angry sad surprised blushing cry mad say tts-start tts-stop tts-status tts-restart tts-say help

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

## --- Kokoro TTS ---
KOKORO = $(dir $(abspath $(lastword $(MAKEFILE_LIST))))live-ai-partner-avatar/kokoro-tts/kokoro

tts-start: ## Start Kokoro TTS daemon
	@$(KOKORO) start

tts-stop: ## Stop Kokoro TTS daemon
	@$(KOKORO) stop

tts-status: ## Show Kokoro TTS daemon status
	@$(KOKORO) status

tts-restart: ## Restart Kokoro TTS daemon
	@$(KOKORO) stop
	@sleep 1
	@$(KOKORO) start

tts-say: ## Speak text: make tts-say t="Hello" v=af_heart
	@python3 -c "import socket,json,sys; s=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM); s.connect('/tmp/vibe-kokoro.sock'); s.sendall(json.dumps({'text':'$(t)','voice':'$(or $(v),af_heart)'}).encode()); s.close()"

help: ## Show commands
	@grep -E '^[a-zA-Z_-]+:.*##' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "}; {printf "  make %-12s %s\n", $$1, $$2}'
