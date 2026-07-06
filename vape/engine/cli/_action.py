"""Canonical avatar action (self-expression) verbs — the single source for CLI validation.

The model-independent gesture names `vape action` accepts. A given model maps each to
its own motion (the renderer's SELF_EXPRESSION_MAP) and may express only a subset; this
frozenset is the stable public vocabulary, the twin of `_feeling.SETTABLE_FEELINGS`, so a
typo fails loud instead of being silently swallowed by the renderer.
"""

from __future__ import annotations

ACTIONS = frozenset({
    "nod", "head_shake", "head_tilt", "laugh", "giggle", "gasp",
    "think", "celebrate", "wave", "bow", "starry", "clap",
})
