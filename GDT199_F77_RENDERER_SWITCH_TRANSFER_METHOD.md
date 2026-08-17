# GDT199 — f77 renderer-switch transfer

## Question

Do the two local renderer changes isolated by GDT198 transfer to every
non-f77 annotated label carrying the same exact opaque payload?

This is a deliberately narrow follow-up.  It freezes the f77 observations
before enumerating the target rows:

| payload | apparatus/tube renderer | figure renderer |
|---|---|---|
| `e|NONE|DY1|B30` | `NONE|D0|OT` | `d|D0|OT` |
| `ch|NONE|DY1|B30` | `d|D0|NONE` | `NONE|D0|OT` |

The values are formal HPR2 fields, not morphemes or meanings.

## Complete target inventory

Enumerate every single-group non-f77 locus in the frozen GDT059/GDT012
human-annotation panel whose exact parser output has either retained payload.
Classify its already published tags as:

- `FIGURE_ONLY`: `FIGURE` without `WATER_OR_APPARATUS`;
- `APPARATUS_ONLY`: `WATER_OR_APPARATUS` without `FIGURE`;
- `DUAL_OR_AMBIGUOUS`: both; or
- `OTHER_CONTEXT`: neither.

Only the first two classes receive the corresponding exact-renderer
prediction.  Dual and other contexts remain visible but are not repaired or
reclassified.  The use of `WATER_OR_APPARATUS` is only the closest archived
proxy for f77's tube-state class and is an explicit limitation.

## Decision

The local renderer-switch rule transfers only if every eligible target has
the exact frozen renderer.  Any miss yields
`F77_RENDERER_SWITCH_DOES_NOT_TRANSFER_TO_ARCHIVED_LABELS`.

This exposed archived transfer is a falsifier, not pristine confirmation.  It
cannot establish ownership, a visual role, word, sound, language, plaintext,
meaning, or translation.  f84r and every f84 row are excluded.
