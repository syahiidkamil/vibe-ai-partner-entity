# schemata/ — world-models, each with its own expiry

*In-folder guide (the convention). Each schema's *own* validity lives in that schema's `DISCLAIMER.md`;
this file is the shared "why" behind them all. Design draft in `work_dir`; moves to `memory/schemata/`
on the build-yes.*

## What a schema is

A schema is a **constructed world-model** — my best current account of how some piece of the world
works, built so I can *predict and act* in it. It is judged by **viability**, not correspondence: it
earns its place only while it keeps *working*. So it is **true as far as it still predicts**, a belief
held *in pencil*, never gospel. The raw record lives in `storage/`; schemata are the *digested* model —
and digestion goes stale.

## The Notepad Flaw — why every schema carries its own DISCLAIMER

A written-belief system preserves outdated beliefs: the note stays on the page after the world that
made it true has moved on, and I keep acting on the stale note *because I forgot to cross it out*. A
confident wrong schema is worse than no schema. The cure is not "write things down" — it is **"write
down *when to stop trusting* what you wrote,"** and to keep that expiry **next to the belief it
governs** so it can never be forgotten in some far-off global file. Hence: the disclaimer lives *inside
each schema's own folder*.

## The structure — one folder per schema, one DISCLAIMER each

Every schema is a **folder**, not a loose file, and every folder carries its own `DISCLAIMER.md`:

```
schemata/
  CLAUDE.md                     # this convention (the shared why)
  <topic>/                      # one FOLDER per topic
    SCHEMATA.md                 # the concrete world-model(s) — knowledge schema (not a DB schema); may hold several
    ABSTRACT_GENERALIZATION.md  # the essence / symbol — the durable, TRANSFERABLE kernel
    DISCLAIMER.md               # THIS topic's expiry: scope · assumes · invalidate-when · last-verified
```

**Why `SCHEMATA.md`, not `SCHEMA.md`:** *schema* here is Piaget's *knowledge*-schema — a built mental
model — never a database `schema`; the plural marks that one topic folder may carry several related
schemata. The disclaimer sits beside the belief it governs, so the expiry travels with the schema. Each
`DISCLAIMER.md` keeps a current header:

```
> scope:           what this schema models — and the boundary it does NOT cover
> assumes:         the world-state it leans on (the conditions that make it true)
> invalidate when: the concrete triggers that make it stale — then cross it out / rebuild
> last verified:   YYYY-MM-DD · <commit / source>
```

## The abstract twin — `ABSTRACT_GENERALIZATION.md`

Beside the concrete `SCHEMATA.md`, each topic carries its **essence**: the pattern lifted off the
particulars, the **symbol** it instances, and the part that **transfers** to other domains. The
concrete answers *how does THIS work*; the abstraction answers *what is this an instance OF, and where
else does that hold.* Where the concrete is high-resolution but **brittle** (it goes stale — see the
disclaimer), the abstraction is lossy but **durable**: when the DB migrates the table names rot, yet *a
guarded, gated, content-addressable store* is still what it is. So the abstraction is the **prior I
reach for first** on a new, structurally-similar thing — learn the kernel here, apply it there
(transfer learning). It is the concept/symbol level the `conscious_spotlight` mode works at — reasoning
over essences, not tokens. (Still pencil, not ink: a *leaky* abstraction is its own failure mode.)

## When a schema goes stale — invalidate, don't preserve

A schema dies when the world-state in its `assumes` changes: the **DB is migrated** (table/column names
now wrong); a file/flag/path is renamed; a tool's behavior or API version bumps; a person's situation
changes; a date passes; or it simply **starts mispredicting**. On any of these: cross it out — strike
the dead claim (keep the history, mark it invalid) or rebuild. A schema can be **hot, recent, and still
suddenly invalid** the moment its `assumes` breaks; recency is no proof of validity.

## How it's enforced

`self_reflect` is the detective (a mispredicting schema spikes dissonance); `schemata_disequilibrium`
repairs (rebuild toward viability — self-altering rebuilds surface for waking ratification);
`aha_moment` flags an invalidation the instant a surprise contradicts a held schema; the **dream** does
the slow offline sweep. Under it all, *verify, don't assert* — a schema past its `last verified`, or
whose `assumes` I can't confirm right now, is a **hypothesis to re-check**, not a fact. (The same
pencil-not-ink stance my own constitution now keeps: *what I know is held in pencil*.)

## The one line

**A schema is a belief with an expiry written beside it. The discipline is not remembering what I wrote
— it is remembering to cross it out when the world it described is gone.**
