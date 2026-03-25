CLI = node $(dir $(abspath $(lastword $(MAKEFILE_LIST))))live-ai-partner-avatar/desktop/cli.js
KOKORO = $(dir $(abspath $(lastword $(MAKEFILE_LIST))))live-ai-partner-avatar/kokoro-tts/kokoro

.PHONY: start stop restart list status feeling action say help
.PHONY: wave nod laugh
.PHONY: tts-start tts-stop tts-status tts-restart tts-say tts-speak

## --- Avatar ---
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
feeling: ## Set feeling: make feeling v=happy
	@$(CLI) $(v)

## --- Self-Expressions (Actions) ---
action: ## Play action: make action v=wave
	@$(CLI) $(v)

## Common shortcuts
wave: ; @$(CLI) wave
nod: ; @$(CLI) nod
laugh: ; @$(CLI) laugh

## --- Speech ---
say: ## Say something: make say m="Hello"
	@$(CLI) say $(m)

## --- Kokoro TTS ---
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
	@echo "Avatar:"
	@echo "  make start / stop / restart / status"
	@echo ""
	@echo "Feelings (mood):  make feeling v=<name>"
	@echo "  normal, happy, sad, angry, frustrated, curious, proud"
	@echo "  anxious, excited, calm, bored, guilty, blushing, surprised"
	@echo ""
	@echo "Actions (motion):  make action v=<name>"
	@echo "  nod, headshake, headtilt, wave, bow, laugh, giggle"
	@echo "  gasp, think, celebrate, sweat, starryeyes"
	@echo "  Aliases: yes, no, lol, hehe, omg, yay, hi, bye, sugoi"
	@echo ""
	@echo "Speech:"
	@echo "  make say m=\"Hello\""
	@echo "  make tts-speak t=\"Hello\" v=af_heart"
	@echo "  make tts-say t=\"Hello\" v=af_heart"
	@echo ""
	@echo "TTS Daemon:"
	@echo "  make tts-start / tts-stop / tts-status / tts-restart"
	@echo ""
	@echo "Shortcuts: make wave / nod / laugh"
