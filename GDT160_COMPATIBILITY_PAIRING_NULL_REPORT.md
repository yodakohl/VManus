# GDT160 compatibility-pairing null report

Decision: **SPECIFIC_LEFT_RIGHT_PAIRING_EXCESS_SUPPORTED**.

## Exact decomposition

The frozen GDT003 Voynich density is reconstructed as
0.045290648728.  Its compatible-pair
numerator is LEFT×LEFT 0, LEFT×RIGHT 44867, and
RIGHT×RIGHT 0.  Thus the entire published numerator is the
cross-side component, not a mixture of unrelated same-edge phenomena.

## Degree-preserving result

Under the primary right-label switch, the fixed graph retains a null mean
density of 0.005421, or
11.9%
of graph-observed compatibility.  The graph-observed/null ratio is
8.37; the direction is positive
on 12/12 folds
and the inclusive 1,024-world p is
0.000976.  Mean switch mobility is
100.0% of right edges.

The direction-reversed left-label null retains
14.7%
and has p=0.000976.  The stricter
recurrence-profile null retains
63.4% with
65.7% mean mobility.  It is a
sensitivity, not the primary gate.

## Same normalization on GDT159 corpora

| corpus | observed density | null density | survives | observed/null | positive folds | p |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| VOYNICH_MATCHED | 0.045291 | 0.005421 | 0.119 | 8.37 | 12/12 | 0.000976 |
| LATIN_SCHOLASTIC_GRAPHEMATIC | 0.000593 | 0.000032 | 0.055 | 18.34 | 6/6 | 0.000976 |
| LATIN_MEDICAL_GRAPHEMATIC | 0.000898 | 0.000064 | 0.072 | 13.98 | 12/12 | 0.000976 |
| LATIN_15C_GRAPHEMATIC | 0.001410 | 0.000151 | 0.107 | 9.32 | 12/12 | 0.000976 |
| IFORAL_1395_1411_GRAPHEMATIC | 0.001363 | 0.000226 | 0.165 | 6.05 | 6/6 | 0.000976 |
| LATIN_GERMAN_APOTHECARY_LATE15 | 0.000000 | 0.000000 | 0.000 | 0.00 | 0/6 | 1.000000 |

Every powered external corpus also has positive specific-pair excess and reaches
the empirical p floor; some have a larger observed/null ratio than Voynich.
Specific operation pairing is therefore not uniquely Voynich.  The remaining
distinction is absolute breadth: Voynich excess density is
0.039969, versus the largest
external excess 0.001258, a
31.8-fold difference.

## Pairs carrying the Voynich excess

| left operation | right operation | eligible folds | null expected | excess | triplets | complete |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| PREFIX_REPLACE:o>sh | SUFFIX_REPLACE:chy>eey | 12 | 0.006 | +11.994 | 44 | 21 |
| PREFIX_ADD:qot | SUFFIX_REPLACE:dy>eol | 12 | 0.008 | +11.992 | 48 | 12 |
| PREFIX_REPLACE:k>sh | SUFFIX_REPLACE:ey>ody | 12 | 0.009 | +11.991 | 36 | 24 |
| PREFIX_ADD:ok | SUFFIX_REPLACE:dy>eor | 12 | 0.010 | +11.990 | 46 | 12 |
| PREFIX_ADD:ot | SUFFIX_REPLACE:dy>eor | 12 | 0.010 | +11.990 | 47 | 12 |
| PREFIX_REPLACE:qo>sh | SUFFIX_REPLACE:chy>eol | 12 | 0.011 | +11.989 | 44 | 21 |
| PREFIX_REPLACE:k>yk | SUFFIX_REPLACE:edy>ody | 12 | 0.013 | +11.987 | 36 | 24 |
| PREFIX_REPLACE:t>yk | SUFFIX_REPLACE:edy>eol | 12 | 0.013 | +11.987 | 36 | 24 |
| PREFIX_ADD:sol | SUFFIX_REPLACE:edy>ey | 12 | 0.017 | +11.983 | 45 | 12 |
| PREFIX_REPLACE:t>yt | SUFFIX_REPLACE:dy>ody | 12 | 0.017 | +11.983 | 46 | 34 |
| PREFIX_ADD:yk | SUFFIX_REPLACE:iin>in | 12 | 0.019 | +11.981 | 46 | 12 |
| PREFIX_ADD:yk | SUFFIX_REPLACE:in>ir | 12 | 0.020 | +11.980 | 57 | 23 |
| PREFIX_REPLACE:k>yk | SUFFIX_REPLACE:edy>eol | 12 | 0.023 | +11.977 | 36 | 24 |
| PREFIX_REPLACE:k>t | SUFFIX_REPLACE:eol>ody | 12 | 0.024 | +11.976 | 36 | 35 |
| PREFIX_REPLACE:ch>s | SUFFIX_REPLACE:iin>in | 12 | 0.025 | +11.975 | 45 | 12 |

The top 20 post-ranked pairs account for
0.6% of summed positive pair
excess.  These identities are an atlas for subsequent testing, not individually
adjusted discoveries.

## Interpretation

The primary null holds the complete vocabulary and transformation graph fixed,
including operation counts, operation supports, host degrees, recurrence,
lengths, characters, units, folds, and all corpus-side section/register
placement.  It changes only which right-operation identity labels each existing
right edge.  A positive excess therefore cannot be reduced to "many operations"
or "few recurrent hosts" alone.

The null is deliberately abstract.  A switched label is not required to remain
a literal edit of its fixed endpoints, because literal deterministic operations
plus an exactly fixed vocabulary admit no nontrivial randomization.  The result
supports organization of the surface-operation incidence graph, not linguistic
morphology by itself.

## Seal and claim ceiling

The scorer uses only the frozen GDT003/GDT159 panels and published aggregates.
The GDT003 source provenance explicitly excluded f84r.  No f84r row, image, or
formal payload was opened, queried, retained, joined, or scored.

At most this experiment supports specific LEFT×HOST×RIGHT organization beyond
degree/frequency margins.  It establishes no morpheme, word boundary, syntax,
language, sound, plaintext, semantics, or translation.
