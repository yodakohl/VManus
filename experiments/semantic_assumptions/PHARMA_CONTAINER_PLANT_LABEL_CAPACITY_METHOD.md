# Pharmaceutical container/plant-label capacity

## Question

Does the existing human editorial layout layer support a transferable formal
contrast between pharmaceutical labels associated with containers (`Lc`) and
labels assigned to plant fragments (`Lf`)?

This is a filler-blind capacity audit. It does not inspect, store, score, or
compare family surfaces, member codes, literal transcription characters,
roots, parser roles, or English meanings.

## Fixed source projection

Read the validated all-reading consensus-group table. Retain only locus, page,
human layout code, zero-alternative flag, group index/count, and symbol count.
Reject every other field from the analytic projection. Keep loci whose code
ends in `Lc` or `Lf` and whose every group has zero bracketed alternatives.

Represent each physical locus by its ordered tuple of group symbol counts.
Class is `CONTAINER_ASSOCIATED` for `Lc` and `PLANT_FRAGMENT_ASSOCIATED` for
`Lf`. ZL3b, IT2a, and RF1b have already been collapsed into the consensus
table and are not replications.

## Nuisance cells and gates

Form cells by exact page and exact ordered group-length tuple. Retain a cell
only when both classes occur. Compute:

- number of mixed cells, loci, pages, and physical folios;
- class-balanced pair opportunities per folio;
- maximum folio share of all retained loci;
- maximum folio share of balanced pair opportunities; and
- the product-orbit log2 size from `choose(cell_size, container_count)`.

Proceed to any formal-feature design only if all gates pass:

1. at least 20 balanced pair opportunities;
2. at least six physical folios;
3. maximum retained-locus folio share at most 0.35;
4. maximum balanced-pair folio share at most 0.35; and
5. a one-sided whole-folio sign orbit can attain `p <= .05`, requiring at
   least five independently reversible physical folios.

Failure stops before family/member access. The gate is deliberately about
transfer across physical folios, not raw within-page assignment count.

## Claim ceiling

A capacity pass would authorize only a new target-blind formal-marker design.
A stop says only that this source projection cannot support that transferable
contrast. Neither outcome establishes a container word, plant word, name,
identifier, owner, noun, sound, language, cipher, plaintext, meaning, or
translation.
