"""Memory-engine configuration — the single source of truth for secrets and dimensions.

Everything secret (the Gemini API key, the DB connection string) is read from
``vape/entity/memory/.env`` and is **never** written to a tracked file or printed.
Callers ask for a value through the accessors here; the value lives only in process
memory. ``mask_secret`` exists so logs/CLI output can *show that* a key is present
without leaking it.

The embedding dimension is **pinned** here. It was live-verified against
``gemini-embedding-2-preview`` (native output = 3072 floats); the pgvector column and
its index depend on this number, so it lives in exactly one place.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

try:
    # use the project's canonical root resolver when importable
    from engine.cli._paths import ROOT_DIR
except Exception:  # pragma: no cover — fallback if imported outside the package
    ROOT_DIR = Path(__file__).resolve().parents[3]

ENV_PATH = ROOT_DIR / "vape" / "entity" / "memory" / ".env"

# --- pinned, live-verified against gemini-embedding-2-preview -------------------
EMBED_MODEL_DEFAULT = "gemini-embedding-2-preview"
EMBED_DIM = 3072  # native output dimension — verified live; the schema depends on it.

# --- the memory-tree on disk: one place every module resolves paths from --------
# Warm tier = the wiki (markdown + git, identity-adjacent, diffable). Bubbles, the
# bookmark spike-store, reveries, and the active-bubble register all hang off here so
# no downstream module hardcodes a path. All absolute, anchored at the repo ROOT_DIR.
MEMORY_WIKI_DIR = ROOT_DIR / "memory_wiki"
BUBBLES_DIR = MEMORY_WIKI_DIR / "bubbles"
MEMORY_INDEX_PATH = MEMORY_WIKI_DIR / "MEMORY.md"          # the Tree-of-Knowledge root
BOOKMARKS_PATH = MEMORY_WIKI_DIR / "bookmarks.jsonl"       # durable spike store (plugs the river-leak)
REVERIES_PATH = MEMORY_WIKI_DIR / "reveries.json"          # minted reverie candidates
DREAM_STATE_PATH = MEMORY_WIKI_DIR / "dream_state.json"    # dream bookkeeping (is_due cursor)
# the register lives beside internal_states.json in the mental folder (per the spec)
ACTIVE_BUBBLE_PATH = ROOT_DIR / "vape" / "entity" / "mental" / "active_bubble.json"


@lru_cache(maxsize=1)
def _load_env() -> None:
    """Load the .env once. Real env vars already set take precedence (override=False)."""
    if ENV_PATH.exists():
        load_dotenv(ENV_PATH, override=False)


def get_database_url() -> str:
    """The Postgres connection string from .env. Never hardcoded, never logged raw."""
    _load_env()
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError(
            f"DATABASE_URL not found. Expected it in {ENV_PATH} or the environment."
        )
    return url


def get_gemini_key() -> str:
    """The Gemini API key from .env. SECURITY: callers must never print this value.

    Use ``mask_secret`` for any human-facing output that needs to confirm presence.
    """
    _load_env()
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise RuntimeError(
            f"GEMINI_API_KEY not found. Expected it in {ENV_PATH} or the environment."
        )
    return key


def get_embed_model() -> str:
    """The embedding model id from .env, falling back to the pinned default."""
    _load_env()
    return os.environ.get("MULTI_MODAL_EMBEDDING", EMBED_MODEL_DEFAULT)


# Module-level constant for ergonomic imports (``from ...config import EMBED_MODEL``).
EMBED_MODEL = get_embed_model()


def mask_secret(value: str, *, show: int = 4) -> str:
    """Render a secret safe for logs: first ``show`` chars, then a fixed mask.

    e.g. a long key -> ``"XXXX…[MASKED:53chars]"``. Never reveals enough to reconstruct.
    """
    if not value:
        return "[EMPTY]"
    head = value[:show]
    return f"{head}…[MASKED:{len(value)}chars]"
