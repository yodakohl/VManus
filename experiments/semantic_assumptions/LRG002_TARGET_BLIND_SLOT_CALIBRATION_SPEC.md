# LRG002 target-blind slot calibration

Status: `CORRECTED_V2_TARGET_BLIND_SYNTHETIC_CALIBRATION`

The real LRG001 prose scores and their association with segment position remain
closed. Calibration uses only the fixed LRG002 metadata panel and synthetic
score vectors.

For every synthetic or future real score vector, replace each score by its
average rank within exact page x symbol-count, scaled as
`(rank + 1)/(cell_n + 1) - 0.5`; a singleton cell receives zero. This removes
all page and length level shifts before position scoring.

Within every physical folio, define

* `A = mean(FIRST) - mean(CORE)`;
* `B = mean(LAST) - mean(CORE)`.

Average the two-vector `(A,B)` equally over folios. The primary direction-free
statistic is its Euclidean norm. B/P section vectors and odd/even folio-parity
vectors are separately equal-folio averages. Folio support and deletion are
projections onto the frozen observed overall unit direction.

Two deterministic 8,192-assignment Monte Carlo nulls rotate complete ranked
score sequences within each segment:

1. `INDEPENDENT_SEGMENT`: each segment receives its own uniform cyclic shift;
2. `COUPLED_FOLIO`: all segments in a folio receive one common integer clock,
   reduced modulo segment length.

Rotations preserve every score, page, length, segment, segment size, folio,
section, parity, and within-segment cyclic order. The observed alignment is not
included; p is `(1 + count(null_norm >= observed_norm)) / 8193`.

All gates are mandatory:

* both null p-values <= .01;
* overall vector norm >= .06;
* B, P, odd, and even projections onto the overall direction each >= .025;
* weaker/stronger projection ratio is >= .35 for both B/P and odd/even;
* B/P vector cosine and odd/even vector cosine each >= .25;
* at least 12 of 16 folio projections are positive;
* every leave-one-folio-out projection is >= .015;
* maximum absolute folio-projection concentration is <= .25.

Calibration contains 64 null worlds and eight worlds each of distributed
FIRST-full, LAST-full, EDGE-full, FIRST-half, and LAST-half plants. Every one
must pass. Eight worlds each of ONE_FOLIO, ONE_SECTION, ONE_PARITY,
FOLIO_RANDOM_DIRECTION, SECTION_OPPOSITION, PARITY_OPPOSITION, PAGE_ONLY,
LENGTH_ONLY, and SEGMENT_ONLY controls must all fail. Rotation rows must be
unique and both matrices/digests must reconstruct independently.

The first target-blind run is preserved as v1. It passed all 64 null and 40
distributed-signal requirements, but two of eight ONE_SECTION worlds passed
because noise on the unplanted P section happened to exceed the absolute .025
floor. Before any real position score was opened, v2 adds the already implied
balance requirement above. The floor alone did not enforce a material share in
the weaker section; .35 is below the weakest v1 distributed plant ratio
(.5024) and above both leaking ONE_SECTION ratios (.1289 and .2814). The same
rule is applied symmetrically to parity. No other statistic, plant, threshold,
or gate changes.

Only if every gate passes may a separately frozen aggregate manuscript target
be run once. A target pass can establish only that relative LRG001 label-profile
likeness occupies a distributed, repeatable corrected-segment position. FIRST,
LAST, and CORE remain structural coordinates, not words, identifiers, names,
nouns, POS, meanings, plaintext, or translation.
