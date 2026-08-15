# GDT161 latent operation-class report

Decision: **LATENT_CLASSES_NOT_ABOVE_HOST_DEGREE_BASELINES**.

## Predictive compression

| corpus | median LEFT×RIGHT K | both-unseen gain vs host baseline (bits/cell) | both-unseen AP gain | positive graph folds | masked-cell COMPAT gain |
| --- | ---: | ---: | ---: | ---: | ---: |
| VOYNICH_MATCHED | 32.0×1.0 | -0.306214 | -0.697275 | 0/12 | -0.119296 |
| LATIN_MEDICAL_GRAPHEMATIC | 1.0×1.0 | +0.032028 | -0.000658 | 12/12 | +0.033013 |
| LATIN_15C_GRAPHEMATIC | 1.0×1.0 | +0.288652 | -0.000880 | 12/12 | +0.064366 |
| LATIN_SCHOLASTIC_GRAPHEMATIC | 1.0×1.0 | +0.022757 | -0.000520 | 6/6 | +0.023166 |
| IFORAL_1395_1411_GRAPHEMATIC | 1.0×1.0 | +0.412412 | -0.139003 | 5/6 | +0.065335 |
| LATIN_GERMAN_APOTHECARY_LATE15 | INSUFFICIENT | | | | |

Voynich's anonymous HOST_BLOCK has both-operations-unseen gain
-0.306214 bits/cell and AP gain -0.697275 over the matched
HOST_PROFILE_LOGIT baseline, with positive direction on 0/12
pre-existing GDT003 folds.  Its median selected class inventory is
32.0×1.0.  The
masked-cell compatibility-profile upper bound gains -0.119296
bits/cell; the both-unseen fraction of that gain is
not defined because masked-cell gain is nonpositive.

| Voynich model | masked-cell AP | masked-cell loss | both-unseen AP | both-unseen loss |
| --- | ---: | ---: | ---: | ---: |
| global | 0.085742 | 0.438384 | 0.073681 | 0.441598 |
| host-profile logistic | 0.889611 | 0.114259 | 0.885372 | 0.116477 |
| degree logistic | 0.711627 | 0.231246 | ineligible | ineligible |
| host block | 0.265877 | 0.377136 | 0.188098 | 0.422691 |
| compatibility block | 0.666781 | 0.233555 | ineligible | ineligible |

The full-graph descriptive MDL fits choose more than one class on
12/12 Voynich folds and
0/36 powered comparator
folds.  Where Voynich
does choose multiple descriptive classes, cross-fold coassignment is unstable:
median Jaccard is 0.517
for LEFT and 0.428 for
RIGHT.  Thus the large excess is well ranked by continuous anonymous host
overlap, but it does not collapse into a stable small categorical inventory
under this fixed class family.  On 12/12 full-graph
fits one side reaches K=32, the predeclared ceiling; this is evidence against a
small inventory, not evidence for 32 privileged formal categories.  The Latin
both-unseen fits select 1×1: their nominal log-loss gains over an unstable
sparse HOST_PROFILE_LOGIT are accompanied by negative AP gains and do not
constitute latent classes.

The masked-cell result answers whether the already-observed compatibility
matrix is block-compressible.  The both-unseen result is the decisive test of
whether anonymous host-support profiles assign entirely new LEFT and RIGHT
operations to reusable classes.  Operation spellings, glyphs, edit strings,
and family subtype were not model features.

## Top-20 excess concentration

On the exact frozen GDT160 4,309-pair atlas, the observed top-20 share is
0.005777.
Its leave-one-world-out degree-null mean is
0.064237
(95% interval 0.058187–
0.071364); the inclusive
lower-tail/diffuseness p is
0.000976.
The full pair-universe observed share is
0.005793, with null
mean 0.031400 and lower-tail p
0.000976.

The atlas-scope result conditions on the already selected GDT160 library; the
full-universe sensitivity removes that selection.  Neither gives individual
operation pairs confirmatory status.

## Interpretation

GDT160's 31.8× absolute excess is therefore evaluated here as a prediction
problem, not merely redescribed as a dense graph.  A compact factorial reading
requires the host-derived class model to transfer to pairs whose two operations
were absent from compatibility training.  A gain confined to COMPAT_BLOCK means
the exposed matrix has local communities but does not establish a reusable
operation algebra.

## Claim ceiling

This experiment concerns anonymous surface-operation incidence and predictive
graph compression only.  It establishes no morphology, word boundary,
language, sound, plaintext, meaning, semantic role, or translation.  f84r was
not opened, queried, retained, joined, or scored.
