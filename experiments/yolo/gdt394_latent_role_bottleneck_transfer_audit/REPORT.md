# GDT394 — latent-role bottleneck transfer audit report

## Decision

`LATENT_ROLE_COMPRESSION_NOT_DISTINCT_FROM_MATCHED_SOURCE_BOTTLENECKS`

The anonymous role coordinate is a useful one-dimensional compression in both
readable domains, but it loses to equally small generic source bottlenecks.
The semantic-role architecture therefore closes. GDT395 is not authorized.

## Interpretation correction

A role score is deterministically computed from source-side features. It
cannot contain information conditional on that complete source representation.
Accordingly, GDT384's `+425` bits, GDT385's `+194` bits, and GDT387's `+85`
bits are finite-model compression/calibration improvements, not new information
absent from the source. GDT394 tests only whether that compression is unusually
portable at a matched one-dimensional budget.

## Matched-capacity result

| domain | scalar bottleneck | held gain (bits) | null-centered excess | positive folds | top-1 | MRR |
|---|---|---:|---:|---:|---:|---:|
| CoReMA | anonymous role | +396.72 | +327.78 | 5/6 | 14,754 | .74817 |
| CoReMA | direct supervised source | **+1,018.98** | **+573.40** | 6/6 | 14,691 | .74697 |
| CoReMA | grammar summary | +908.57 | +52.57 | 6/6 | 14,754 | .74818 |
| CoReMA | exact-joint role rate | +337.97 | +369.66 | 6/6 | **14,934** | **.75162** |
| PCEEC2 | anonymous role | +1,173.50 | +661.75 | 79/84 | 7,340 | .49184 |
| PCEEC2 | direct supervised source | **+3,418.27** | **+1,882.39** | 84/84 | **9,026** | **.52872** |
| PCEEC2 | PCA source | +1,413.57 | +49.26 | 82/84 | 7,354 | .49247 |
| PCEEC2 | grammar summary | +936.72 | -4.28 | 77/84 | 7,293 | .49009 |

Every entry is one scalar passed through the same eight-bin Dirichlet decoder.
The direct supervised scalar is not claimed to be a semantic discovery; it is
the strongest equal-budget demonstration that source grammar can be compressed
more effectively for the external target. More damagingly, the role also loses
to a simple grammar summary in CoReMA and to unsupervised PCA in PCEEC2.

## Null and rank gates

The role remains positive after coupling destruction is centered out, and its
effect survives removal of the largest fold and the most frequent exact source
form in both domains. It is therefore not noise or a one-form artifact.

It nevertheless fails every decisive comparative gate:

* role gain does not beat every equal-budget control in either domain;
* role null-centered excess does not beat every control;
* the jointly charged max-eight p-value is `1.0` in both domains;
* MRR does not exceed the best control by `.001`; and
* top-1 recovery does not exceed the best control by the frozen margin.

Thus the earlier role coordinate captures real regularity, but no evidence says
it is the privileged portable abstraction of that regularity.

## Consequence

Do not design GDT395 on the premise that this anonymous role should exist in
Voynich. The GDT384–387 signals remain useful examples of regularization and
low-dimensional calibration. They do not support a cross-domain semantic role
layer over matched source compressions.

The independent validator reconstructs source counts, fold arithmetic, null
means/excesses, max-family p-values, gates, hashes, and the final decision and
passes `70/70`. It honestly does not refit the eight projections.

## Claim ceiling

GDT394 establishes only that the tested role coordinate is useful but not
distinctive one-dimensional comparator compression. It establishes no Voynich
role, TIME, REF, coordination, parent, syntax, POS, meaning, language,
plaintext, or translation. It read zero Voynich rows. f84 remained fully
sealed.
