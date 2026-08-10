# PFR001 — public pharmaceutical ROOT-only versus PLANT-fragment capacity

Status before audit: **SOURCE-METADATA ONLY; VOYNICH STRINGS FORBIDDEN**.

## Question

Can the public human label catalogue support a folio-clustered comparison of
labels attached to fragments catalogued as `root` versus `plant`, before any
Voynich form is inspected?

This is distinct from S98--S101. It does not compare pharmaceutical labels to
Herbal prose, copied-plant pairs, exact words, parsed roots, or a proposed
`d` diagnostic. It asks only whether the public same-register object classes
have enough independent, mixed production units for a fair later test.

## Frozen source and eligibility

- Public source: Stolfi/Grove 1998 best-label catalogue,
  <https://www.ic.unicamp.br/~stolfi/PUB/EXPORT/voynich/Notes/107/work/Notes/614/labtit-best.idx>.
- Use records whose public section is `pharma`, object class is `P`, certainty
  is `UNHEDGED`, and object guess is exactly `root` or `plant`.
- The primary capacity panel additionally requires the already validated
  current-locus crosswalk flag `primary_eligible == 1`.
- Physical folio is the leading `f` plus digits. ZL3b/IT2a/RF1b text columns,
  source label strings, roots, roles, and all grammar features are forbidden.
- A missing or hedged object description is never converted into either class.

## Capacity gates

A later transferable test requires all of:

1. each class on at least five physical folios;
2. at least five physical folios containing both classes;
3. for every held mixed folio, at least five mapped training labels of each
   class outside that folio;
4. at least three minority-class labels of each direction across mixed pages.

The five-folio condition is the minimum for a one-sided synchronous sign orbit
to reach `1/32 < .05`. Label-level within-page permutations may be reported as
capacity diagnostics, but cannot replace physical-folio replication.

If any gate fails, stop before scoring text. The maximum claim is a public-data
capacity stop; neither `root` nor `plant` is a Voynich meaning.
