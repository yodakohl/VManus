# GDT126 — Q20 star-boundary record-reset test

## Question

Are adjacent physical lines more similar in anonymous HPR2 compiler profile
when they remain inside one human-inventoried star record than when the same
page transition crosses to the next star-defined record?

This directly tests the record scope implied by GDT115/GDT117. It does not
assume that a star names its following text or that an OPEN is a semantic
heading.

## Inventory

- Reuse all 170 clean Q20 records on eight physical folios and 13 pages.
- Form every adjacent line pair inside a record.
- Form a cross-record pair only when successive star ordinals are both present
  on the same page; do not bridge the missing f106r record.
- ZL3b is primary. IT2a and RF1b are alternate-reading sensitivities.
- f84r is rejected before formal retention and remains entirely sealed.

## Representations

For each physical line calculate:

1. the anonymous 12-cell compiler-rate vector;
2. the 29-cell host-edge vector;
3. hashed raw-group character trigrams;
4. hashed PAGE_HOST character trigrams.

The outcome is cosine similarity between adjacent lines. Compiler similarity
is primary; raw and host strings are strong string-statistical controls.

## Nuisance and null

Regress each similarity on page fixed effects, log left/right group counts,
absolute group-count difference, and normalized adjacency position. Compare
the residual mean inside versus across boundaries with equal weight for each
page and boundary class.

Use 4,096 deterministic topology-preserving worlds. Within each page and
coarse total-length bucket, retain the observed number of cross-boundary
positions and permute which adjacency positions carry them. Recompute the
page-balanced residual contrast and use a max-four statistic. Report
leave-one-physical-folio contrasts and all null capacity.

## Decision

`Q20_STAR_BOUNDARY_HAS_COMPILER_RESET` requires positive compiler contrast,
positive contrast after every folio deletion, max-four p <= .05, the same
direction in all readings, and compiler contrast at least as large as both
string controls. Otherwise report a weak/string-like/no-reset result.

The strongest possible conclusion is a formal record boundary. No bullet
meaning, heading, recipe, semantic role, word, morpheme, POS, sound, language,
plaintext, meaning, or translation follows.
