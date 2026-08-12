# LM001Y final residual leaf-margin census method

## Purpose

LM001 and its first new-data extension LM001X remain sealed from every Voynich
text feature. Their combined 35-folio visual panel passes all original capacity
gates except one: q05 supplies three of ten toothed pages, a 30% share rather
than at most 25%.

LM001Y is the final nonadaptive new-data extension. It includes every remaining
unseen Currier-A `SOURCE_HERBAL_PAGE` physical folio outside q05. It does not
resample, regrade, lower a threshold, or choose pages based on morphology.

## Deterministic complete residual census

1. Reconstruct the Currier-A numeric-folio `SOURCE_HERBAL_PAGE` pool from the
   public page annotation TSV and ZL3b metadata.
2. In each physical folio, retain the page with the lowest SHA-256 of
   `LM001X_PAGE|<page>`, preserving the exact LM001X folio representative rule.
3. Exclude every physical folio already present in the published LM001 or
   LM001X panels, and exclude q05.
4. Retain every remaining row. No page-count target, rank, or sampling step is
   applied.
5. Opaque page ID is `LY` plus the first eight uppercase hexadecimal characters
   of SHA-256 `LM001Y_OPAQUE|<page>`.

The complete residual is expected to contain exactly nine pages on nine
physical folios. Official Yale canvases are bound without opening their image
bodies.

## Frozen visual pass and decision

Inspect every selected canvas exactly once in opaque-ID order under the
unchanged published LM001 `TOOTHED` / `SMOOTH` / `UNCERTAIN` rubric. Do not
read, transcribe, OCR, or interpret Voynich writing.

Combine the new judgments without alteration with the published 35-page
LM001+LM001X panel, then apply every original LM001 gate unchanged. Because q05
is fixed at three toothed pages, the 25% cap requires at least twelve total
toothed pages; hence at least two of these nine new pages must be `TOOTHED`.
Every other state, Currier, quartile, uncertainty, and quire gate must also
pass.

Failure closes whole-page leaf-margin association at this resolution before
text access. Pass licenses only a separately frozen text design; it is not an
association result.

## Claim ceiling

LM001Y can establish only capacity for a later formal association test. It
cannot identify a plant, establish that prose describes leaf margins, assign a
word or morpheme, name a language or cipher, supply plaintext, or translate the
manuscript.
