# Cross-base opening-member capacity

Status: **FROZEN_TARGET_LABEL_MASKED_CAPACITY_ONLY**

## Question

The confirmed onset result learns an exact `(base, onset)` preference on other
physical folios.  It does not distinguish a base-specific lookup from a
member-state relation shared across different bases.  Before defining that new
test, measure whether the existing masked panel supports simultaneous transfer
away from both the target base and target folio.

No `NONE`/`DA` row label may be exposed or scored.  Use the frozen 1,207-row
masked panel and its 197 exact base/folio quota cells.  The source-native STA
table may be used only to recover the first member's family for an opaque
family diagnostic; no operation label or later remainder member may be stored.

## Frozen eligibility

For row `(base=b, folio=f, onset=o)`:

1. `b` must occur on at least one physical folio other than `f`;
2. after excluding both `b` and `f`, `o` must occur in at least two distinct
   other bases;
3. its base/folio cell must retain at least two different onsets satisfying
   rules 1--2.

Rule 3 prevents a constant cell-level prediction from masquerading as member
discrimination.  Eligibility is computed without row operation labels.

Capacity passes only with at least 600 eligible rows, 90 cells, 20 bases, 35
folios, 12 exact onset states, five onset families, and no base contributing
more than 15% of eligible rows.  Every retained family must contain at least
two bases and two onset states.  The output panel must contain exactly the
original masked fields plus opaque `onset_family_id` and binary
`crossbase_eligible`; it may contain no operation, prefix, full remainder,
page/locus, or English field.

## Ceiling

A pass authorizes target-free calibration of a shared-member predictive test.
It does not establish that such transfer exists and supplies no detachment,
allomorphy, harmony, orthography, morphology, pronunciation, wordhood, POS,
syntax, language, cipher operation, meaning, plaintext, or translation.
