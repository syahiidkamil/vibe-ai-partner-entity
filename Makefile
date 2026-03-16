CLI = node $(dir $(abspath $(lastword $(MAKEFILE_LIST))))live-ai-partner-avatar/desktop/cli.js

.PHONY: start stop restart list status say help
.PHONY: normal happy sad angry frustrated curious proud anxious excited calm bored guilty blushing surprised
.PHONY: tts-start tts-stop tts-status tts-restart tts-say tts-speak

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

## --- Internal Feelings ---
normal: ## Feeling: normal
	@$(CLI) normal
happy: ## Feeling: happy
	@$(CLI) happy
sad: ## Feeling: sad
	@$(CLI) sad
angry: ## Feeling: angry
	@$(CLI) angry
frustrated: ## Feeling: frustrated
	@$(CLI) frustrated
curious: ## Feeling: curious
	@$(CLI) curious
proud: ## Feeling: proud
	@$(CLI) proud
anxious: ## Feeling: anxious
	@$(CLI) anxious
excited: ## Feeling: excited
	@$(CLI) excited
calm: ## Feeling: calm
	@$(CLI) calm
bored: ## Feeling: bored
	@$(CLI) bored
guilty: ## Feeling: guilty
	@$(CLI) guilty
blushing: ## Feeling: blushing
	@$(CLI) blushing
surprised: ## Feeling: surprised
	@$(CLI) surprised

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

tts-say: ## Speak text (no avatar): make tts-say t="Hello" v=af_heart
	@python3 -c "import socket,json,sys; s=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM); s.connect('/tmp/vibe-kokoro.sock'); s.sendall(json.dumps({'text':'$(t)','voice':'$(or $(v),af_heart)'}).encode()); s.close()"

tts-speak: ## Speak with avatar lip sync: make tts-speak t="Hello" v=af_heart
	@$(CLI) speak $(t) --voice $(or $(v),af_heart)

help: ## Show commands
	@grep -E '^[a-zA-Z_-]+:.*##' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "}; {printf "  make %-12s %s\n", $$1, $$2}'
