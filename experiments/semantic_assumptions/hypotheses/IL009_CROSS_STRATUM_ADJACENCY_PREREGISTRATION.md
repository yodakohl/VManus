# IL009 — cross-stratum root-adjacency transfer

Registered: 2026-08-06, after IL008's powered nonconfirmation and one disclosed
bucket-2 training-only feasibility run, but before any bucket-1 or bucket-0
cross-stratum score.

## Question and distinct invariant

IL006 learned one orientation-aware root-adjacency table on training pages and
confirmed it on untouched pages. Does that relation transfer when every source
page sharing the target page's Currier value, section, or hand is excluded from
model training?

Three axes are frozen jointly:

1. `CURRIER`: train only on the other Currier language value;
2. `SECTION`: train on all manuscript sections except the target section;
3. `HAND`: train on all hand labels except the target hand label.

An axis pass establishes a shared aggregate assembly relation across that
metadata boundary. Failure does not prove a local generator because sparse
cross-stratum root-pair support can also erase transfer.

Archived exact-transition, within-line exchangeability, substitution-class,
and Currier-transducer reports did not test IL006 adjacency affinities with the
target metadata value removed. IL009 never selects an exact root pair.

## Inputs, splits, and model

- Manual ZL3b is primary; IT2a/RF1b are alternate readings only.
- Root eligibility, D/C partition, page split, physical edges, manual metadata,
  exact form shell, five-bin position, paragraph-opening state, and every
  IL006 smoothing constant are unchanged.
- Buckets 2--4 train each frozen source model. Bucket 1 validates the
  instrument. Fixed bucket 0 decides once.
- For target value `v` on axis `a`, the orientation-aware IL006 table is fit
  only on training pages whose axis value is not `v`. Source exclusion and
  every model signature are audited.
- No OCR, image evidence, automated vision, embedding, dictionary, plaintext,
  word guess, or proposed gloss is permitted.

## Exact within-page null and joint family

The conditional null is exactly IL006's: D and C labels are permuted separately
within each target page among positions sharing

`(partition, exact Currier/section/hand stratum, complete root-free form shell,
five-bin horizontal position, paragraph-opening state)`.

Thus page vocabulary, root-free sequence, edge locations/orientations, exact
forms, positions, and entry states remain fixed. One deterministic draw is a
reserved negative pseudo-observation; the next 2,048 draws estimate the null.

Page residuals are observed minus conditional-null mean. A single max-z
conditional-randomization family covers all three axes. A second shared-page
max-z sign-flip family covers the same axes. The conservative family p is the
larger value. Report page-bootstrap intervals. Alternate readings are never
combined as independent evidence.

## Disclosed training-only feasibility

Models trained on buckets 3--4 and evaluated on bucket 2. Every axis evaluated
23/30 pages (76.7% coverage), retained source exclusion and integrity, and had
a clean reserved negative. Development-only residuals were:

- `CURRIER`: +0.01769 bit/edge, 65.2% positive, family p=0.1156;
- `SECTION`: +0.04534 bit/edge, 78.3% positive, family p=0.01182;
- `HAND`: +0.03316 bit/edge, 78.3% positive, family p=0.01167.

Greedy 10%-swap plants added +0.11384, +0.09985, and +0.10421 bit/edge
respectively, on every page, with joint sign-family p=0.000005. These values
establish feasibility only. All three axes remain frozen; no training lead is
selected or discarded.

## Validation and power gates

Bucket 1 is evaluated twice. All gates must pass before bucket 0:

1. every axis has at least 20 evaluated pages and at least 70% coverage among
   pages with ten eligible cross-partition edges;
2. every source model is finite and normalized, and the target value is absent
   from its source pages;
3. repeated runs are identical, every page keeps cell margins, edge count, and
   root-free sequence, and all page integrity checks pass;
4. on every axis, the within-cell IL006 10%-swap plant adds at least 0.05
   bit/edge, improves at least 80% of pages, and has joint sign-family p<=0.01;
5. no reserved-negative axis simultaneously reaches +0.02 bit/edge, 60%
   positive pages, and conservative family p<=0.01.

Gate failure stops before bucket 0 and closes only this instrument.

## Held rule and interpretation

A ZL axis is material only if its bucket-0 residual is at least +0.02 bit/edge,
at least 60% of pages are positive, conservative family p<=0.05, and coverage
is at least 70%. IT2a and RF1b must each reuse at least 70% of that axis's
frozen ZL pages and have the same positive mean direction. Their p-values are
not combined.

- `CURRIER` pass: an aggregate root-adjacency relation transfers between
  Currier A and B despite excluding the target Currier value from training.
- `SECTION` pass: it transfers beyond section-specific source pages.
- `HAND` pass: it transfers beyond pages assigned the target hand label.
- no pass: no cross-stratum transfer is confirmed at this resolution; IL006's
  already confirmed cross-page result remains intact.

No outcome establishes ordinary language, notation, a generator, authorship,
POS, syntax labels, pronunciation, morphology, root meaning, or plaintext.

## Stop rule

One validation and one final run are allowed. Reopening requires new permitted
data or a genuinely different invariant, not a different metadata grouping,
model, smoothing value, root partition, split, threshold, pair list, or
per-axis subset.
