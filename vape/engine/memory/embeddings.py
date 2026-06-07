"""The Gemini embedding client.

Wraps ``google-genai``'s ``embed_content`` for ``gemini-embedding-2-preview``. The key
is read from ``.env`` via ``config.get_gemini_key()`` and lives only in the client
object — it is **never** printed, logged, or returned. The output dimension is the
pinned ``EMBED_DIM`` (3072), so vectors match the DB column and index exactly.

Embeddings are a regenerable index, not truth: swap the model, re-embed, nothing is
lost (the spec's rule). That is why the dimension is pinned in one place — change it
there and re-embed.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Sequence

from google import genai
from google.genai import types

from engine.memory.config import EMBED_DIM, EMBED_MODEL, get_gemini_key


# A per-request HTTP timeout (ms). Without it a Gemini service stall blocks the
# caller indefinitely — fatal for the Stop-hook dream and any CLI write path. A bounded
# timeout turns a stall into a clear, loud failure the caller can surface instead of a hang.
_REQUEST_TIMEOUT_MS = 60_000


@lru_cache(maxsize=1)
def _client() -> genai.Client:
    """A cached Gemini client. Holds the key in memory only; never exposes it.

    Carries a bounded per-request timeout so a transient API stall fails fast and
    loudly rather than hanging the dream/CLI write path forever.
    """
    return genai.Client(
        api_key=get_gemini_key(),
        http_options=types.HttpOptions(timeout=_REQUEST_TIMEOUT_MS),
    )


def embed(
    texts: Sequence[str],
    *,
    task_type: str = "RETRIEVAL_DOCUMENT",
) -> list[list[float]]:
    """Embed texts. Returns one 3072-float vector per input, in input order.

    IMPORTANT (live-verified): ``gemini-embedding-2-preview`` returns exactly ONE
    embedding per ``embed_content`` call regardless of how many ``contents`` you pass —
    so a multi-text call would silently drop all but the first and misalign every vector
    with its text. To stay correct we issue one call per text. (If a future model
    supports true batching, this is the one place to change.)

    ``task_type`` follows Gemini's retrieval convention: ``RETRIEVAL_DOCUMENT`` for
    stored corpus rows, ``RETRIEVAL_QUERY`` for the search query — embedding both with
    their matched task type is what makes asymmetric retrieval work well.
    """
    if not texts:
        return []
    client = _client()
    vectors: list[list[float]] = []
    for text in texts:
        resp = client.models.embed_content(
            model=EMBED_MODEL,
            contents=text,
            config=types.EmbedContentConfig(
                task_type=task_type,
                output_dimensionality=EMBED_DIM,
            ),
        )
        if len(resp.embeddings) != 1:
            raise RuntimeError(
                f"Gemini returned {len(resp.embeddings)} embeddings for one text"
            )
        vec = list(resp.embeddings[0].values)
        if len(vec) != EMBED_DIM:
            raise RuntimeError(
                f"Gemini returned a {len(vec)}-dim vector, expected {EMBED_DIM}"
            )
        vectors.append(vec)
    return vectors


def embed_one(text: str, *, task_type: str = "RETRIEVAL_DOCUMENT") -> list[float]:
    """Embed a single text. Convenience wrapper over ``embed``."""
    return embed([text], task_type=task_type)[0]
