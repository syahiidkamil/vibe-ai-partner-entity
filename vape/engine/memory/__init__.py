"""The memory socket — retrieval over the file-first memory organ.

Files are the source of truth; every store below is a derived, rebuildable
index. Public face: `get_firewall()` (config-driven) and the DTOs.
"""
from .factory import get_firewall
from .interface import (
    Capabilities,
    Embedder,
    Hit,
    IndexReport,
    Memory,
    Query,
    RetrievalBackend,
    Surface,
)

__all__ = [
    "get_firewall",
    "Capabilities", "Embedder", "Hit", "IndexReport",
    "Memory", "Query", "RetrievalBackend", "Surface",
]
