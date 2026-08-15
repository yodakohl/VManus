# GDT120 — Q20 latent record-class prediction

Status: `EXPLORATORY_YOLO_FIXED_MODEL_FAMILY`

## Question

GDT115 and GDT117 show that a Q20 record's first line (`OPEN`) predicts the
anonymous compiler profile of its later lines (`BODY`) on unseen physical
folios.  GDT120 asks whether that continuous relationship supports a small,
reusable alphabet of record-template classes rather than only a diffuse
correlation.

`OPEN`, `BODY`, and `class` are structural labels.  They are not headings,
entries, recipes, topics, or meanings.

## Nested class discovery

Reuse the 170 clean star-delimited Q20 records on physical folios f104, f105,
f106, f107, f112, f113, f114, and f115.  Hold out one entire physical folio.
For each `K` in 2, 3, 4, 5, 6, standardize the 12-dimensional BODY compiler
profile on the other seven folios and fit deterministic k-means with 16
SHA-seeded initializations.  Canonicalize cluster labels by lexicographic
centroid order.  Assign the unseen BODY records to the frozen centroids.

The resulting labels are fold-local anonymous record classes.  No class is
given a semantic role.  Class discovery is repeated independently in ZL3b,
IT2a, and RF1b; the readings are sensitivities of one manuscript, not
replications.

## Held-folio predictors

A low-capacity ridge predictor maps nuisance variables to one-hot BODY class.
The nuisance vector contains only record line/group/member counts, page side,
and normalized within-page ordinal.  Four additions are compared at fixed
ridge 1000, inherited from the stable GDT115 compiler channel:

1. `OPEN_WRAPPER7`;
2. `OPEN_COMPILER12`;
3. `OPEN_EDGE29`;
4. `RAW_OPEN_CHAR3_HASH32`.

Gain is the reduction in standardized multiclass Brier/SSE pseudo-code,
`(SSE_nuisance-SSE_model)/(2 ln 2)`.  It is a comparative score, not a
lossless manuscript code.

## Same-page pairing null and stability

In each held folio, permute complete OPEN feature vectors only within page and
exact OPEN-member-count strata.  BODY classes, folio, page, record shape, and
the multiset of OPENs remain fixed.  Use 4,096 shared SHA-seeded worlds and
report inclusive local and max-20 p-values over five K values and four
representations.

For each K, report adjusted Rand agreement of fold-held class assignments
between alternate readings.  This is a reading-stability diagnostic, not
additional sample size.

## Interpretation

A useful exploratory class system requires a positive selector-paid primary
gain, max-20 p at most .05, positive direction in all readings, at least six of
eight positive primary folios, and mean cross-reading adjusted Rand at least
.5.  Failure ranks the class resolution as weak or unstable; it does not erase
the continuous compiler linkage already established by GDT115/GDT117.

f84r is rejected before retention and is not opened, queried, joined, scored,
targeted, assigned, or predicted.  No semantic role, star attribute, word,
morpheme, POS, sound, language, plaintext, meaning, or translation is inferred.
