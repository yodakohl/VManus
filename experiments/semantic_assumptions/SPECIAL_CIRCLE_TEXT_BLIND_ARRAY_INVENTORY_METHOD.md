# Special-circle text-blind array inventory

Date: 2026-08-12

## Purpose

Create a new provenance-complete, filler-blind array inventory for the
manuscript's f67--f73 diagram block. This is not a reconstruction of the lost
historical EAS001 panel. The old panel reported 46 arrays and 391 slots on 13
folios; its exact membership and artifacts remain unavailable. The new panel
is independently selected from the current human exact-locus annotation table
and is restricted to seven physical folios in the special-circle block.

## Frozen selection

Read
`results/existing_human_exact_locus_annotations.tsv` in source row order.

1. Retain pages whose numeric folio is 67 through 73 inclusive.
2. Group rows by exact `(page, unit)`.
3. A group is an array when at least three rows have a nonempty
   `normalized_code` whose final two characters are one of
   `L0, Ls, Lz, La, Ri, Ro` (individual label, star/zodiac label, or radial
   writing layouts in the human source).
4. Once a group qualifies, retain every row in it in original source order.
   Classify an empty-code row as `ABSENT` only when the human local comment
   explicitly says the position is missing or not labelled; classify a row
   with reported ink traces or an unreadable label as `UNREADABLE_TRACE`.
5. Assign arrays and slots by first source occurrence. Derive physical folio
   only as the leading `f` plus digits from the page ID.

No Voynich transcription, family, member, formal root, parser role, gloss,
image feature, or proposed meaning enters selection or output. Human unit and
local descriptions are retained as provenance, not translated field names.

## Scope

This inventory can support a future separately preregistered graphical-array
question. It does not inherit EAS001's historical score, establish a record
boundary, equate slots across diagrams, or license inspection of filler
identities. ZL3b, IT2a, and RF1b would remain alternate readings if a later
target is designed.

The inventory supplies no direction, month, star, nymph, object, field, word,
sound, language, cipher, plaintext, meaning, or translation.
