# GDT389 method — frozen before image access

## Question

Does the exact permitted 61-page/30-folio frame contain author-visible
connectors that establish singular, directed inscription-to-inscription edges
without consulting Voynich text or formal structure?

## Frozen page universe

The sole universe is `gdt388_page_frame.tsv`: all 61 f84-free pages already
represented in the permitted GDT360 annotation archive. No page may be added or
removed after image review begins. Page order is a deterministic SHA-256 order
fixed in the pre-image artifact.

Official Yale image metadata may be queried only with an exact page allow-list.
A raw canvas label is checked before any other metadata field is retained. A
canvas mixing an allowed page with any `f84*` label is rejected. Mapping failure
is `UNMAPPED`, never guessed.

## Review stages

1. **Page-level geometry screen.** Inspect the complete allowed page or mapped
   page segment. Do not inspect or transcribe glyph identities. Record one of:
   `NO_CONNECTOR_CANDIDATE`, `AMBIGUOUS_CONNECTOR`,
   `CONNECTOR_WITH_FEWER_THAN_TWO_INSCRIPTIONS`, or
   `CONNECTOR_WITH_TWO_OR_MORE_INSCRIPTIONS`.
2. **Source-aware localization.** Only for the last state, map each endpoint to
   the already published human locus inventory. A missing or plural mapping is
   unresolved. No surface or formal column may be read.
3. **Direction review.** Admit direction only from a visible arrowhead,
   unambiguous authorial flow device, or an external source-authored order
   frozen independently of Voynich text. Plain lines, ducts, paths, radial
   spokes, proximity, and reading order are nondirectional.
4. **Eligibility.** Retain an edge only when both endpoint loci are exact and
   distinct, ownership and direction are singular, the target is not a
   deterministic consequence of array/layout geometry, and at least one matched
   alternative target remains mobile.

The complete frame must be reviewed before capacity is interpreted. A page
with no candidate remains a valid observation, not a failed experiment.

## Reviewer provenance

This is an exploratory YOLO acquisition by one AI visual reviewer. It is not an
independent human annotation. Page screening, endpoint localization, and
direction judgment are logged separately, but the same observer may perform
them. Any future confirmation must treat these observations as exposed and
obtain a newly frozen independent review rather than calling this blinded human
evidence.

No OCR, CLIP, embedding, machine-generated caption, automatic image
classification, or neural image recognition is permitted. Direct visual
inspection of official pixels is permitted.

## Frozen stop and capacity rules

- Do not score formal data in GDT389.
- Publish all candidates, ambiguities, and negatives.
- Fewer than 50 eligible directed edges or fewer than five physical folios
  closes the current parent-link application at capacity.
- Even 50/five only permits a later separately frozen score; it is not
  confirmation-level power.
- ZL3b/IT2a/RF1b are never replications.
- All `f84*` material is forbidden.

## Claim ceiling

GDT389 can establish only a geometry-derived edge census and its capacity. It
cannot establish parenthood, reference, syntax, semantic role, POS, word,
meaning, language, plaintext, or translation.
