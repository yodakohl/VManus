# GDT324 — opaque-cell lattice compression

## Question

Can the exact compatibility-cell lexicon required by GDT321/322 be compressed
from other cells of the same opaque PAGE_HOST and from shared renderer
coordinates, without observing any wrapper event from the target cell?

This differs from GDT310. GDT310 predicted three operation licenses from
source-wrapper ecology of a host. GDT324 hides every event in one complete
`(PAGE_HOST, local-frame, inner-D, right-family, DY, B3)` cell and predicts its
eight-way wrapper distribution using only other cells.

## Frozen panel

From the f84-free GDT278 Voynich reference, retain cells with at least 10
events on at least three physical folios. A target cell is scoreable only when
its PAGE_HOST has at least one other retained cell. Selection uses no wrapper
diversity or outcome value. The frozen panel contains 60 target cells, 3,135
events, and 20 opaque hosts; the training population contains 136 cells.

## Fixed predictors

In leave-one-complete-cell-out folds compare Dirichlet-1/2 count models:

- `GLOBAL`: every event outside the target cell;
- `COORDINATE`: other hosts with the same five non-host renderer coordinates,
  backing off to GLOBAL only if empty;
- `HOST_SIBLING`: every other retained cell with the same opaque PAGE_HOST;
- `HOST_COORD_ADDITIVE`: normalized
  `log P(HOST_SIBLING) + log P(COORDINATE) - log P(GLOBAL)`.

The target cell contributes neither counts nor wrappers to any predictor.
Score the mean held cross-entropy inside each cell and give all 60 cells equal
weight. Report event-weighted sensitivity separately. Charge the selected
nonbaseline model by a two-bit four-model selector.

Use 8,192 fixed-prediction worlds that permute complete target-cell wrapper
count vectors inside frozen event-count × folio-count bins. This preserves a
cell's internal wrapper distribution and approximate opportunity while
destroying its host/coordinate address. Max-correct over the three nonbaseline
models. The null is an architectural diagnostic, not a retrained exact
conditional test.

Call `OPAQUE_CELL_LATTICE_FACTORABLE` only if the additive model beats GLOBAL
after the two-bit selector, beats both single-axis models, and has max-three
p≤.05. Call `OPAQUE_HOST_ECOLOGY_ONLY` or `OPAQUE_COORDINATE_ECOLOGY_ONLY` if
one single-axis model alone is the shortest positive selector-paid model.
Otherwise call `OPAQUE_CELL_LEXICON_NOT_COMPRESSED`.

This may compress known recurrent-host cells only. It cannot predict a new
host, establish a morpheme or lexical category, or assign meaning, sound,
language, plaintext, or translation. No f84 row may be opened, parsed,
retained, joined, or scored.
