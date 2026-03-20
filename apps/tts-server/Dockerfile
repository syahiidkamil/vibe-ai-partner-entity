# ─── Stage 1: Dependencies ──────────────────────────────────
FROM python:3.12-slim AS deps

WORKDIR /app

# System deps for sounddevice (PortAudio)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libportaudio2 \
        libsndfile1 && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# ─── Stage 2: Application ───────────────────────────────────
FROM deps AS app

COPY src/ ./src/
RUN pip install --no-cache-dir -e .

# Default: install KittenTTS (lightest engine)
RUN pip install --no-cache-dir kittentts

EXPOSE 5111

# Health check
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5111/api/health')"

CMD ["python", "-m", "uvicorn", "vibe_tts.server:app", "--host", "0.0.0.0", "--port", "5111"]
