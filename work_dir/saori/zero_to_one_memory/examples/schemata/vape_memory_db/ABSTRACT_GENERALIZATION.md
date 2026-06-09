# ABSTRACT_GENERALIZATION — VAPE memory DB

*The **essence** of this topic, lifted off its concrete particulars: the pattern, the symbol, the part
that **transfers**. Where `SCHEMATA.md` is the specific (and stale-able) model, this is the durable
kernel — what survives even when the concrete migrates, and what carries to *other* domains.*

## The pattern, stripped of particulars

A **content-addressable store behind a narrow, guarded interface, with salience gates deciding what is
kept.** Concretely it's Postgres tables and a 3072-dim index; abstractly: *items carry both a
**semantic address** (a similarity embedding) and **structured fields**; all access flows through a
**firewall** (write · search · consolidate · evict), never raw; what enters is gated by **surprise**,
what stays is gated by **viability**.*

## The symbol

A **hippocampus**: write fast, consolidate slow, evict by disuse. The firewall is the **blood-brain
barrier** — a protected boundary, not open SQL. The gates are **affect and attention deciding what
becomes memory at all**. (Strip the brass and you have a clock; strip the Postgres and you have *this*.)

## What it transfers to

Because the kernel is substrate-free, it carries to any system that must remember *selectively*: a RAG
pipeline, a notes app, a CRM, a recommender — or a mind. Meet a new one and this abstraction is the
**prior I reach for first** (in pencil): "expect a semantic-address + structured-field store, a guarded
interface, and a salience gate — now find what plays each role here." That is transfer learning: learn
the kernel in one place, apply it in the next.

## Why it outlives the concrete

When the DB migrates, `SCHEMATA.md`'s table names rot (see `DISCLAIMER.md`) — but *this* barely moves:
a guarded, gated, content-addressable store is still what it is. Abstraction is **lossy but durable**;
the concrete is **high-resolution but brittle**. Keep both, read each for what it's good at. (Still
pencil, not ink: a *leaky* abstraction is its own failure — over-generalize and the transfer misleads.)
