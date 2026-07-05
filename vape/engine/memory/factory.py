"""Factory — config-driven construction of the firewall and its parts.

Reads config.json's `memory` section, loads vape/.env (the repo's first
Python .env consumer — keys never echoed), resolves the configured backend
from the `vibe.retrieval.providers` entry-point group, and ALWAYS keeps the
FilesBackend floor underneath: an unresolvable backend degrades to the floor
with a reason, never a crash. The embedder degrades independently of the
store (no key -> NoneEmbedder -> fts-only search; never an error).
"""
from __future__ import annotations

from importlib.metadata import entry_points
from pathlib import Path

from .files_backend import FilesBackend
from .firewall import Firewall
from .interface import Embedder, RetrievalBackend

ENTRY_GROUP = "vibe.retrieval.providers"
PLACEHOLDER_KEYS = {"", "your-gemini-api-key-here", "changeme"}


def _root_dir() -> Path:
    from engine.cli._paths import ROOT_DIR
    return Path(ROOT_DIR)


def load_env(root: Path) -> None:
    env_file = root / "vape" / ".env"
    if not env_file.is_file():
        return
    try:
        from dotenv import load_dotenv
        load_dotenv(env_file, override=False)
    except Exception:
        pass


def memory_config(root: Path) -> dict:
    from engine.cli._config import read_config
    cfg = read_config().get("memory", {})
    return {
        "retrieval": cfg.get("retrieval", "sqlite"),
        "embedder": cfg.get("embedder", "none"),
        "plugins": cfg.get("plugins", {}),
    }


def build_embedder(name: str, root: Path) -> Embedder | None:
    if name != "gemini":
        return None
    import os
    load_env(root)
    key = os.environ.get("GEMINI_API_KEY", "")
    if key in PLACEHOLDER_KEYS:
        return None            # degrade to fts-only; doctor names the reason
    from .embedders import GeminiEmbedder
    return GeminiEmbedder()


def resolve_backend_class(name: str):
    for ep in entry_points(group=ENTRY_GROUP):
        if ep.name == name:
            return ep.load()
    return None


def build_backend(root: Path, cfg: dict) -> tuple[RetrievalBackend, str]:
    """Returns (backend, note). The note explains any degradation."""
    name = cfg["retrieval"]
    if name == "files":
        return FilesBackend(root), ""
    cls = resolve_backend_class(name)
    if cls is None:
        return FilesBackend(root), (
            f"configured backend '{name}' is not installed "
            f"(uv sync --extra retrieval-{name}); running on the files floor"
        )
    embedder = build_embedder(cfg["embedder"], root)
    try:
        backend = cls(root, cfg["plugins"].get(name, {}), embedder)
        backend.migrate()
        return backend, ""
    except Exception as e:
        return FilesBackend(root), (
            f"backend '{name}' failed to start ({e}); running on the files floor"
        )


def build_core_store(root: Path):
    """CoreStore arrives in S2; the floor runs without counters."""
    try:
        from .core_store import CoreStore
    except ImportError:
        return None
    try:
        return CoreStore(root / "vape" / "entity" / "storage" / "index" / "core.db")
    except Exception:
        return None


def get_firewall() -> tuple[Firewall, str]:
    """The one constructor the CLI calls. Returns (firewall, degradation_note)."""
    root = _root_dir()
    cfg = memory_config(root)
    backend, note = build_backend(root, cfg)
    floor = backend if isinstance(backend, FilesBackend) else FilesBackend(root)
    return Firewall(backend, root, floor=floor, core_store=build_core_store(root)), note
