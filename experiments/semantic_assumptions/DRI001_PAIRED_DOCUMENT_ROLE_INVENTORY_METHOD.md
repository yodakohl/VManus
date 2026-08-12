# DRI001 paired document-role inventory method

Status: **PREREGISTERED BEFORE SELECTED IMAGE ACCESS**.

This is a versioned replacement for the provenance-lost
`DOCUMENT_ROLE_ANNOTATION_V2` viewer, not a continuation of that missing
artifact. It asks whether a small source-native role rubric transfers between
two physical folios that share the same section and exact run of editorial
IVTFF kinds (`P`, `L`, `C`, `R`). It is diagnostic within those matched cells;
it cannot confirm a manuscript-wide document class or treat the fifteen cells
as statistically independent.

## Source-only selection

Collapse consecutive identical `kind` values on each page to make its exact
kind-run template. Retain every `(section, kind-run template)` cell represented
on at least two physical folios. Order its pages by SHA-256 of
`DRI001_ROLE_PAIR_V1|<section>|<template>|<page>` and select the first two pages
on different physical folios. Assign phases by deterministic signed-graph
colouring: the two pages in every cell must have opposite phases, while any
selected logical pages sharing one official canvas must have the same phase.
In each connected component, the selected page with the lexicographically
lowest selection hash is `CALIBRATION`; graph parity fixes the rest. A
contradiction hard-stops. This prevents a calibration foldout image from
exposing a diagnostic logical page. The rule uses no image, transcription
surface, family, member, root, parser role, object tag, public page prose, or
prior visual outcome.

The expected capacity is fifteen cells, thirty selected logical pages, and
twenty-four distinct physical folios; each pair uses different folios, but six
folios necessarily recur across different cells, chiefly in the pharmaceutical
block. Several foldout pages share official canvases
with other page parts; the official canvas is an image witness, never an
independent sample. Existing full-canvas exposure must be disclosed per page.

## Source-native rubric

Inspect each selected logical page region once on the official Yale image with
all transcription identities withheld. Record only visible document role:

- `PROSE_DOMINANT`: continuous multi-line writing blocks occupy the page;
- `OBJECT_WITH_PROSE`: a dominant illustration and a continuous prose block
  coexist without singular caption ownership;
- `REPEATED_OWNED_RECORDS`: at least three repeated visible objects or cells
  each have a distinct author-visible inscription slot assigned by a leader,
  divider, enclosure, reserved column, or unambiguous local stack;
- `DIAGRAM_PARAMETER_ARRAY`: inscriptions occupy repeated diagram-defined
  cyclic, radial, or cell slots rather than prose blocks or singular captions;
- `MIXED_OR_UNRESOLVED`: no one role is secure.

Also record the author-visible evidence devices independently: continuous prose
block, dominant illustration, repeated object/cell template, singular ownership
devices, and diagram-defined slots. Whitespace proximity and transcription
order cannot establish ownership. Do not identify plants, figures, stars,
languages, words, or meanings.

Calibrate the unchanged rubric on all fifteen `CALIBRATION` pages. Continue to
the fifteen sealed `DIAGNOSTIC` pages only if at most three calibration pages
are unresolved and no rubric amendment is needed. A matched cell transfers
only when its two pages receive the same non-unresolved role. The diagnostic
instrument is worth retaining only with at least ten resolved cells, at least
eleven role agreements, and at least three distinct non-unresolved roles over
the thirty pages. Otherwise stop before any transcription/formal association.

Even a pass establishes only repeatability of visible document roles inside
matched editorial layout cells. It supplies no heading, caption, field name,
class name, word, POS, sound, language, cipher, plaintext, meaning, or
translation.
