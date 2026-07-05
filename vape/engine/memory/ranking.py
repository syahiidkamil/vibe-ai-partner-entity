"""Rank policy — the ONE place score math lives (every backend stays dumb).

Doc 13's rails, coded: relevance (RRF over legs) dominates; usage strength is
a small, capped, decaying whisper that can break ties but never outshout the
cue; a quarter of top-k goes to challengers (optimism for the untried); the
explore mode drops the usage term entirely and widens the challenger quota.

Constants below are feel-first on purpose — tune ONLY after `vape memory
stats` shows real skew (you cannot tune what you never measured).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timezone

from .interface import Hit

RRF_K = 60                    # standard reciprocal-rank-fusion constant
STRENGTH_W = 0.10             # weight of one net-useful log unit
STRENGTH_CAP = 0.30           # strength can move a hit ~3 rank positions, no more
DECAY_HALF_LIFE_DAYS = 14.0   # unused strength halves every two weeks
CHALLENGER_BONUS = 0.15       # UCB-ish optimism numerator
CHALLENGER_SHARE = 0.25       # quarter of top-k reserved for challengers
EXPLORE_CHALLENGER_SHARE = 0.5


@dataclass
class UsageRow:
    recalled: int = 0
    dereferenced: int = 0
    helped: int = 0
    hurt: int = 0
    last_recalled_at: datetime | None = None


@dataclass
class Scored:
    hit: Hit                       # representative hit (first leg it appeared in)
    sources: list[str] = field(default_factory=list)
    relevance: float = 0.0         # normalized RRF within the candidate set
    strength: float = 0.0
    score: float = 0.0
    challenger: bool = False


def _decay(last_recalled_at: datetime | None, now: datetime) -> float:
    if last_recalled_at is None:
        return 1.0
    days = max(0.0, (now - last_recalled_at).total_seconds() / 86400.0)
    return 0.5 ** (days / DECAY_HALF_LIFE_DAYS)


def strength(usage: UsageRow, now: datetime) -> float:
    net = max(0, usage.helped - usage.hurt)
    return min(STRENGTH_CAP, STRENGTH_W * math.log1p(net)) * _decay(usage.last_recalled_at, now)


def fuse(
    legs: list[Hit],
    usage: dict[str, UsageRow],
    k: int,
    explore: bool = False,
    now: datetime | None = None,
) -> list[Scored]:
    """RRF-fuse per-leg candidates, apply the usage whisper, mix challengers.

    `legs` is the flat list of Hits from the backend (leg = Hit.source);
    `usage` maps memory_id -> UsageRow (empty dict is fine: strength 0).
    """
    now = now or datetime.now(timezone.utc)

    by_id: dict[str, Scored] = {}
    for h in legs:
        s = by_id.setdefault(h.memory.id, Scored(hit=h))
        s.sources.append(h.source)
        s.relevance += 1.0 / (RRF_K + h.leg_rank)

    if not by_id:
        return []

    top_rel = max(s.relevance for s in by_id.values()) or 1.0
    for s in by_id.values():
        s.relevance /= top_rel
        u = usage.get(s.hit.memory.id, UsageRow())
        s.strength = 0.0 if explore else strength(u, now)
        s.score = s.relevance + s.strength

    ranked = sorted(by_id.values(), key=lambda s: s.score, reverse=True)

    share = EXPLORE_CHALLENGER_SHARE if explore else CHALLENGER_SHARE
    n_chal = int(k * share)
    n_exploit = k - n_chal

    exploit = ranked[:n_exploit]
    chosen = {s.hit.memory.id for s in exploit}

    # challengers: high relevance, low trials, not already chosen
    def challenger_score(s: Scored) -> float:
        u = usage.get(s.hit.memory.id, UsageRow())
        return s.relevance + CHALLENGER_BONUS / math.sqrt(1 + u.recalled)

    pool = [s for s in ranked[n_exploit:] if s.hit.memory.id not in chosen]
    pool.sort(key=challenger_score, reverse=True)
    challengers = pool[:n_chal]
    for s in challengers:
        s.challenger = True

    out = exploit + challengers
    # backfill if the challenger pool ran dry
    if len(out) < k:
        rest = [s for s in ranked if s.hit.memory.id not in {x.hit.memory.id for x in out}]
        out += rest[: k - len(out)]
    return out
