# GDT395 scorer/validator conformance correction V5

Status: `POST_ORACLE_CONFORMANCE_CORRECTION_FROZEN_BEFORE_SCORING_V5`

The blind decoder claims were frozen before oracle access. Scoring V4 then
opened the exact 50 held synthetic oracles and wrote eight aggregate files.
Independent validation stopped at `PANEL_METRICS_MISMATCH_GATE`; it wrote no
validation artifact. The failure initially appears at the authentic-view label
(`main` in the producer versus `authentic` in the validator), but static review
found additional producer/validator convention differences.

This correction does not select a world, property, representation, threshold,
or result from observed performance. V5 adopts the complete independently
published `VALIDATION_DESIGN.md` as the normative aggregate-output
specification. That specification and its implementation were frozen before
the held oracle was opened. The settled V4 output bytes are hash-bound before
V5 runs.

## Fixed conformance changes

V5 retains the V4 authenticated claim/oracle join, canonical opaque-set truth,
private abstention singletons, NMI, Hubert-Arabie ARI, pair-F1, recurring-only
entity-reuse restriction, seven scoreable partitions, ten interface HOLDs, and
the conjunctive `.35/.20/.35` seed gate. It changes only the independently
predeclared aggregate contract:

1. authentic output rows use `view=authentic`;
2. exact kind/status/qualification/note literals, `NA` cells, eligible
   prediction counts, and JSON Boolean spelling follow the validator design;
3. diagnostic `primary_index` is the minimum threshold ratio rather than its
   mean;
4. W10 uses the median of the five held-seed rates and the frozen median-based
   3,125-resample nearest-rank upper bound;
5. representation selection and exploratory decision serialization follow the
   validator's deterministic frozen ordering;
6. the compact summary contains aggregate role hashes rather than 2,203
   per-file hash entries;
7. pair endpoints remain hard HOLD, non-semantics-light architecture endpoints
   remain unscored, and all decisions remain exploratory/unconfirmed.

No event claim, oracle truth, metric effect, property decision, or scientific
performance value is used to choose these changes. The correction is
post-oracle and that chronology remains explicit. The first few V4 aggregate
rows were displayed while diagnosing the mismatch; no event-level oracle row
or synthetic label meaning was used for the repair.

## Scientific scope

V5 remains a synthetic identifiability benchmark. It contains no Voynich rows,
does not score Voynich, and does not access `f84` or `f84r`. A PASS can validate
or invalidate methods only; it cannot transfer a recovered synthetic property
to the manuscript.
