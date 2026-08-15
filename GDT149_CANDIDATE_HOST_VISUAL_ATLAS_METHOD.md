# GDT149 — candidate-host visual atlas

## Scope

GDT149 is an exposed, post-hoc semantic-hypothesis generator following
GDT148.  It does not test a translation.  It asks whether the four rare exact
PAGE_HOST witnesses nominated by the three top-six GDT148 component
relations—`pch`, `olo`, `kor`, and `oko`—associate with any of the twelve
human-visible Herbal page features frozen before GDT137 formal scoring.

The candidate set is fixed from the published GDT148 shared-host table:
`pch` is the rarest MHI005 witness, `olo` the rarest MHI006 witness, and `kor`
and `oko` the two rarest MHI007 witnesses.  No alternative host or visual
feature is added after scoring.

## Test

Across all 127 f84-free Herbal pages, record exact candidate-host presence and
the twelve binary GDT137 visible features.  For each of 4×12 cells, compute the
within-stratum centered overlap

```text
sum_host_pages(feature - mean_feature_in_stratum)
```

where strata are Currier × hand × illustration profile.  Shuffle complete
12-feature page vectors within strata for 100,000 deterministic worlds.  This
preserves visual-feature covariance.  Report local enrichment tails and a
maximum-over-48 standardized tail.

For each host, also remove both pages in the human relation that nominated it
and repeat the local calculation with 50,000 within-stratum shuffles.  This is
a relation-endpoint sensitivity, not a new holdout: all visual features and
the decision to inspect these hosts are already exposed.

Labels are descriptive:

- `INTERESTING_EXPLORATORY` requires max-48 p≤.05;
- `PROVISIONAL_POSTSELECTED` requires local p≤.05 and a positive
  relation-endpoint-excluded effect;
- `WEAK` requires local p≤.10;
- otherwise `NO_SIGNAL`.

## Claim ceiling

At most this atlas nominates a PAGE_HOST/visible-page-feature pair for a later
prospective test.  Whole-page presence supplies no locus ownership.  No host
is assigned a plant-part meaning, semantic role, word, morpheme, POS, sound,
language, plaintext, or translation.  The GDT062 source has zero f84r rows;
all other f84-prefixed rows are rejected before retention.
