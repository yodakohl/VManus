# GDT1075 method

## Question and fixed input

Does the GDT1074 pX/yX physical paragraph-opening contrast survive comparison
within the same section and scribal hand? The preregistration fixes the five
complete-form bases `aiin`, `chedy`, `cheol`, `cheor`, `chor` and the exact
GDT1074 event-file hash before section/hand metadata is queried. The unit is
a line-initial, definitely separated complete group, not a presumed morpheme.

## Data and calculation

Read only GDT1074 events marked `INCLUDED`. Join the section, hand and Currier
fields by reader and exact line locus from the frozen source TSV. `query-tsv`
must filter the 179 admitted page selectors and reject `f84*` in the selector
before the requested columns are materialized. Group events by reader, base,
section and hand. Retain all strata, including ones with only one form. A
stratum is informative only if each form occurs at least twice and on at least
two physical folios. Compare fractions by cross multiplication of integer
paragraph-start counts. Readers are three alternative transcriptions of the
same manuscript, so ZL3b makes the primary decision and IT2a/RF1b are
sensitivity checks.

`src/run.py` emits every fixed event with its joined metadata, all strata,
and the summary. `src/validate.py` independently checks the frozen input hash,
complete event roster, domain and uniqueness, stratum arithmetic, capacity,
direction and guard record. Run both commands from the repository root as
specified in `experiment.json`.

## Decision and limit

At least three distinct bases must have informative ZL3b strata and every
informative ZL3b stratum must show pX's greater paragraph-opening fraction.
Otherwise record failure or insufficient capacity exactly as preregistered.
Section-only and same-leaf counts are descriptive. This can disfavor a *pure*
section/hand mixture explanation for the formal contrast; it cannot identify
the meaning of p/y, any whole word, a sentence boundary or a historical genre.
