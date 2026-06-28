# Writing rules for this schema

How to write the files under `magic_chess_gogo/` so the schema stays usable on relight.

## 1. Content is ready-to-consume

Every content file (`schemata.md`, the `infos/` docs, `heroes/`, `equipments/`, `commanders/`,
`synergies/`, `gogo_cards/`, `rounds/`, the `experience/` replay) must read as **finished, usable
knowledge**: the answer already assembled, not the raw materials to assemble it. A reader (me, on
relight) should be able to act on a content file directly, with **no required table join**, no
cross-referencing a raw dump, no decoding step. If using a fact would force the reader to go fetch
and stitch something together first, the file is not done yet.

## 2. The untidy part goes in the `source_map.md` (the librarian, not the content)

The messy half belongs in each folder's `source_map.md`: provenance (where each fact was pulled
from), raw->resolved joins, extraction caveats, name<->id keying, soft spots, "still not
data-extracted" notes, and the regen scripts. The source_map is the **librarian**, it tells you
where things came from and how they were derived, but it is **not the knowledge itself**. Keeping it
out of the content is what lets the content stay clean and ready to use.

## In short

- **Content file** = the resolved, usable answer. No joins, no raw, no fetch-first.
- **`source_map.md`** = provenance + the untidy derivation. Read it only to *check* or *rebuild* a
  fact, never to *learn the game*.
