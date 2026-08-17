# GDT235 — label residual to visible object-class transfer

## Question

After removing the transferred GDT233 graphical prefix, does the exact residual
identify a broad human-annotated visual object class beyond section/register?

## Data and endpoint

Use every non-f84 exact-locus row tagged `LABEL`, then whitelist those loci
before parsing source-family consensus.  The mutually exclusive source-bound
endpoint is assigned by tag precedence:

`PLANT`, `WATER_OR_APPARATUS`, `ROSETTE_OR_MAP`, `ASTRONOMICAL`,
`FIGURE_ONLY`, `OTHER_LABEL`.

This is coarse annotation metadata, not word meaning or authorial ownership.

## Predictors

Compare exact `RAW_FAMILY`, exact `STRICT_RESIDUAL`, and exact
`TRANSFERRED_PREFIX`.  In leave-one-physical-folio-out prediction, a feature is
eligible only if seen on another folio.  Its modal training object class is
compared on the same covered rows with the modal class for the held row's
section.  A leave-one-section-out sensitivity compares feature lookup with the
training-global majority.

No smoothing, glyph similarity, or semantic hierarchy is fitted.  Alternate
transcriptions contribute one family-consensus observation, not replications.
