# GDT325 — sparse-cell coordinate backoff

## Prospective target

GDT324 found a small coordinate-only wrapper-distribution gain after hiding
complete powered cells. Test that lead on a lower-support panel not scored by
GDT324: every exact cell with 5–9 events on at least two physical folios that
fails the GDT324/GDT322 powered threshold, while its five-field renderer
coordinate occurs in the frozen 136-cell GDT324 training population.

Selection uses no wrapper outcome. The frozen panel contains 94 cells, 609
events, 85 folios, 84 opaque hosts, and 12 renderer coordinates.

## Frozen models

Wrapper count distributions are learned only from the 136 powered GDT324
training cells; no event in a sparse target cell supplies a count.

1. `GLOBAL`: pooled powered-cell Dirichlet-1/2 counts;
2. `GLOBAL_TWO_RULE`: GLOBAL plus the exact frozen GDT322 coefficients
   `s×LINE_START=1.0021314958853849` and
   `q×PREV_DY=0.8920380870887143`;
3. `COORDINATE`: powered cells with the same exact
   `(local-frame, inner-D, right-family, DY, B3)` coordinate;
4. `COORDINATE_TWO_RULE`: COORDINATE plus the two frozen GDT322 coefficients.

No parameter, threshold, coordinate, wrapper class, or coefficient is fitted
on the sparse panel. Score mean cross-entropy within each target cell and give
94 cells equal primary weight; report event-weighted sensitivity separately.
Charge each nonbaseline candidate by a fixed two-bit four-model selector.

Use 8,192 fixed-prediction worlds permuting target wrappers within
`register × LINE_START × PREV_DY × target-event-count-bin`, with bins
`5–6/7–9`, and max-correct over all four models. This preserves register,
entry-state, and approximate cell opportunity while destroying the target
coordinate relation. It is a diagnostic, not a refitted exact null.

Call `SPARSE_CELL_COORDINATE_BACKOFF_SUPPORTED` only if the best coordinate
model has positive selector-paid cell-equivalent gain, beats the best global
model, gains in at least two of B/H/S, and has max-four p≤.05. If coordinate
backoff transfers but the two fixed rules do not add held gain, retain
coordinate-only backoff. Otherwise preserve GDT322's unknown-cell policy.

This can license only a probabilistic wrapper prior for a previously unseen
host×coordinate cell. It assigns no host identity, morpheme, lexical class,
meaning, sound, language, plaintext, or translation. No f84 row may be
opened, parsed, retained, joined, or scored.
