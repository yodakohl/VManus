# LM001X Currier-A leaf-margin extension method

## Purpose

LM001 stopped before text access because its prospective held panel contained
only five `TOOTHED` pages: one Currier A and four Currier B. Three of those five
were in q05, giving q05 a 60% share. Its registered reopen condition permits
new independently frozen source-native pages balanced across Currier and
additional quires.

LM001X supplies exactly that new source-only evidence. It does not regrade any
LM001 judgment, lower any gate, or open any Voynich string or formal feature.
The already calibrated LM001 `TOOTHED` / `SMOOTH` / `UNCERTAIN` rubric remains
unchanged.

## Deterministic extension panel

Inputs are the same public Voynich.nu page-annotation TSV, ZL3b metadata,
official Yale IIIF manifest `2002046`, and the published LM001 selection and
held result.

1. Retain `SOURCE_HERBAL_PAGE` pages with ZL Currier A metadata and numeric
   physical folios.
2. Exclude every physical folio in the original LM001 selection.
3. Within each remaining physical folio, retain the page with the lowest
   SHA-256 of `LM001X_PAGE|<page>`.
4. Exclude q05. Because q05 already contributes three of five old toothed
   pages, another q05 tooth cannot help satisfy the frozen 25% concentration
   gate.
5. Within every remaining quire, retain at most the three pages with the lowest
   SHA-256 of `LM001X_SELECT|<page>`.
6. Opaque page ID is `LX` plus the first eight uppercase hexadecimal characters
   of SHA-256 `LM001X_OPAQUE|<page>`.

This yields 19 previously unused Currier-A folios across q01, q02, q03, q04,
q06, q07, q15, and q17, with no quire contributing more than three extension
pages. The builder binds official Yale canvases but does not open their image
bodies.

## Frozen visual pass

Inspect every selected canvas exactly once in opaque-ID order using the
published LM001 rubric. Do not read, transcribe, OCR, or interpret Voynich
writing. Large lobes, separate leaflets, stem branches, root/fruit teeth,
hairs, paint bleed, parchment damage, and decorative dots remain excluded from
leaf-margin teeth.

## Combined capacity gates

After the extension judgments are fixed, combine them with the 16 original
LM001 held judgments without alteration. Proceed to any text design only if the
combined panel satisfies every original LM001 gate:

1. at least six `TOOTHED` and six `SMOOTH` pages;
2. both states on at least three Currier-A and three Currier-B pages;
3. both states in at least three folio-rank quartiles (the extension inherits
   the quartile assigned to each page by the original full Currier-A eligible
   pool);
4. no more than four `UNCERTAIN` pages;
5. no single quire contributes more than 25% of either admitted state.

Given the old 10/5/1 counts and q05 toothed count of three, a combined pass
necessarily requires at least seven new Currier-A toothed pages, no more than
three new uncertain pages, and sufficient cross-quire dispersion. These are
consequences of the original gates, not new relaxed thresholds.

Failure stops before every Voynich text feature. A pass licenses only a new,
separately frozen formal association design controlling Currier, quartile,
quire, hand, text length, and prior flower/fruit tags.

## Claim ceiling

LM001X can only establish whether the expanded source-bound visual panel has
capacity for a future association test. It cannot identify a plant, establish
that prose describes leaf margins, assign a word or morpheme, name a language
or cipher, supply plaintext, or translate the manuscript.
