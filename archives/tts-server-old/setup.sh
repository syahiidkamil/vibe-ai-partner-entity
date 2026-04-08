#!/bin/bash
# Create Python venv and install vibe-tts in editable mode.
# Usage: cd apps/tts-server && bash setup.sh [--kokoro] [--kitten]

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "Creating venv..."
python3 -m venv .venv
source .venv/bin/activate

echo "Installing vibe-tts..."
pip install -e .

# Install optional engine deps based on flags
if [[ "$*" == *"--kokoro"* ]]; then
    echo "Installing Kokoro dependencies (PyTorch + misaki)..."
    pip install -e ".[kokoro]"
fi

if [[ "$*" == *"--kitten"* ]]; then
    echo "Installing KittenTTS dependencies..."
    pip install -e ".[kitten]"
fi

echo ""
echo "Done. Start the server with:"
echo "  source .venv/bin/activate"
echo "  python -m uvicorn vibe_tts.server:app --host 0.0.0.0 --port 5111"
