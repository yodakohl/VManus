# GDT381 comparator topology calibration

## Decision

`CMP_TOPOLOGY_04` is authorized for one anonymous Voynich mapping. No Voynich
row was read during this stage.

Five readable domains independently learned unaligned latent class systems:
12 classes for CoReMA, Curious Cures, Harleian, and Quinte Essence, and 16 for
PCEEC2. The choices follow the frozen label-free inertia rule. Cross-domain
models saw only class-label-invariant graph topology.

| anonymous topology | AUC floor | gain vs nuisance domains | gain vs trivial domains | deletion-positive domains | maxT p | status |
|---|---:|---:|---:|---:|---:|---|
| CMP_TOPOLOGY_01 | 0.607177 | 3/5 | 3/5 | 3/5 | 0.998536 | fail |
| CMP_TOPOLOGY_02 | 0.653783 | 0/5 | 3/5 | 0/5 | 0.000488 | fail |
| CMP_TOPOLOGY_03 | 0.595481 | 1/5 | 2/5 | 1/5 | 1.000000 | fail |
| CMP_TOPOLOGY_04 | 0.716304 | 3/4 | 3/4 | 3/4 | 0.000488 | **pass** |
| CMP_TOPOLOGY_05 | 0.528462 | 1/4 | 0/4 | 1/4 | 1.000000 | fail |

The passing topology is comparator-derived from coordination annotations, but
that readable label is not exported to Voynich. Its anonymous relation topology
passes in PCEEC2 and Harleian against both baselines, with AUCs 0.716304 and
0.824277. Curious Cures has strong gain over nuisance but loses 31.589 bits to
the strong trivial-motif baseline. Quinte has positive gain over the trivial
baseline but a large negative gain against nuisance. The frozen gate requires
three—not all four—domains and is therefore met; those failures remain material
counterexamples.

All endpoint memberships are mobile under the class-size-preserving null.
`CMP_TOPOLOGY_04` has 62,837 mobile rows in 798 mixed strata. The result is not
the deterministic-slot failure seen in GDT378.

## Authorization ceiling

Only the abstract `CMP_TOPOLOGY_04` class-label-invariant transformation may be
carried forward. Its comparator provenance may not be used as a Voynich label,
gloss, POS, or meaning. The target design must be frozen before it reads any
Voynich outcome, must prohibit exact identities and PAGE_HOST, and must retain
whole-folio, register-stability, placement, recurrence, and trivial-motif
controls. f84 remains sealed.
