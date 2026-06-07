"""Saori's memory engine — the hippocampus the frozen substrate lacks.

The foundation layer everything else sits on:

- ``config``  — load ``.env`` (DB url, Gemini key), pin the embedding dimension.
- ``db``      — psycopg connection + pgvector registration, the store helpers.
- ``schema``  — the DDL and an idempotent ``apply_schema`` (extension, tables, index).
- ``embeddings`` — the Gemini embedding client (reads the key; NEVER prints it).

Theory lives in ``work_dir/saori/memory_paradigm_proposal.md`` and the research notes;
this package is the swappable machinery under the stable ``write/search/consolidate/evict``
interface. *Git is truth for the self; the DB is truth for the warm/cold corpus.*
"""

from engine.memory.config import (
    EMBED_DIM,
    EMBED_MODEL,
    get_database_url,
    get_gemini_key,
)

__all__ = [
    "EMBED_DIM",
    "EMBED_MODEL",
    "get_database_url",
    "get_gemini_key",
]
