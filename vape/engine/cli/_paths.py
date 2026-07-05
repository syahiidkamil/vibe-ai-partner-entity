"""Central path resolution for the Vibe AI Partner project."""

from __future__ import annotations

import os
from pathlib import Path


def _find_root() -> Path:
    """Walk up from this file to find the project root (contains .git or config.json)."""
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / ".git").exists() or (current / "config.json").exists():
            return current
        current = current.parent
    return Path(__file__).resolve().parents[4]


ROOT_DIR = _find_root()
CONFIG_PATH = ROOT_DIR / "config.json"
PLUGINS_DIR = ROOT_DIR / "vape" / "plugins"
RENDERERS_DIR = PLUGINS_DIR / "renderers"
SHELLS_DIR = PLUGINS_DIR / "shells"


def cache_base() -> Path:
    """Per-user cache base: XDG_CACHE_HOME > %LOCALAPPDATA% (Windows) > ~/.cache.

    Downloader and every model loader must agree on this — the same branch is
    mirrored in _progress.py and tts-kokoro-onnx/engine.py; change all three
    together.
    """
    xdg = os.environ.get("XDG_CACHE_HOME")
    if xdg:
        return Path(xdg)
    if os.name == "nt" and os.environ.get("LOCALAPPDATA"):
        return Path(os.environ["LOCALAPPDATA"])
    return Path.home() / ".cache"


def cache_dir() -> Path:
    """Return the cache directory for model files. Creates it if needed."""
    d = cache_base() / "vibe-ai-partner"
    d.mkdir(parents=True, exist_ok=True)
    return d


def model_cache_dir(subdir: str) -> Path:
    """Return a model-specific cache directory (e.g., 'kokoro-onnx')."""
    d = cache_base() / subdir
    d.mkdir(parents=True, exist_ok=True)
    return d
