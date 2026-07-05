"""Embedders — Gemini (the one real embedder) and None (the keyless tier).

The Embedder protocol is deliberately tiny: dim, model, embed(texts, task).
The `model` string is recorded beside every vector and filtered in every ANN
query, so vectors from different models are never compared (doc 04's
discipline, doc 12 C6). A model swap is therefore a tracked re-embed, never a
silent mix.

Sync by design: the CLI is synchronous, and batching happens server-side
(one embed call carries up to 100 texts). HAZARD, documented: if this is
ever called from inside a running event loop (future server use), wrap it in
a thread — the google-genai sync client is fine, but do not block a loop.
"""
from __future__ import annotations

import os
import re
import time


class NoneEmbedder:
    """The explicit keyless tier: dim 0, embeds nothing. Present so 'no
    vectors' is a stated choice in the config, never an accident."""

    dim = 0
    model = "none"

    def embed(self, texts: list[str], task: str) -> list[list[float]]:
        return [[] for _ in texts]


class GeminiEmbedder:
    """gemini-embedding via google-genai; model from MULTI_MODAL_EMBEDDING env
    (vape/.env), Matryoshka-cut to 1536 dims (doc 04 §6). Reads GEMINI_API_KEY
    from the environment — the key is never stored or echoed by this code."""

    dim = 1536
    _BATCH = 100

    def __init__(self) -> None:
        self.model = os.environ.get("MULTI_MODAL_EMBEDDING", "gemini-embedding-2")
        from google import genai
        from google.genai import types as gtypes
        self._genai = genai
        self._types = gtypes
        self._client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    def embed(self, texts: list[str], task: str) -> list[list[float]]:
        task_type = "RETRIEVAL_QUERY" if task == "query" else "RETRIEVAL_DOCUMENT"
        cfg = self._types.EmbedContentConfig(
            task_type=task_type, output_dimensionality=self.dim)
        T = self._types
        out: list[list[float]] = []
        for i in range(0, len(texts), self._BATCH):
            batch = texts[i:i + self._BATCH]
            # each text wrapped as its OWN Content: a bare list of strings is
            # folded into ONE content by the SDK and returns ONE embedding —
            # verified live 2026-07-05 (3 texts in, 1 embedding out)
            resp = self._call_with_retry(
                [T.Content(parts=[T.Part(text=s)]) for s in batch], cfg)
            if len(resp.embeddings) != len(batch):
                raise RuntimeError(
                    f"embed batch mismatch: {len(batch)} texts -> "
                    f"{len(resp.embeddings)} embeddings (model {self.model})")
            out.extend([e.values for e in resp.embeddings])
        return out

    def _call_with_retry(self, contents, cfg, attempts: int = 5):
        """Free-tier quota is ~100 contents/min: honor the server's retryDelay
        on RESOURCE_EXHAUSTED instead of failing the whole sweep."""
        last: Exception | None = None
        for _ in range(attempts):
            try:
                return self._client.models.embed_content(
                    model=self.model, contents=contents, config=cfg)
            except Exception as e:
                msg = str(e)
                if "RESOURCE_EXHAUSTED" not in msg and "429" not in msg:
                    raise
                m = re.search(r"retryDelay['\"]?:\s*['\"]?(\d+)", msg)
                time.sleep(int(m.group(1)) + 1 if m else 30)
                last = e
        raise last if last else RuntimeError("embed retry exhausted")
