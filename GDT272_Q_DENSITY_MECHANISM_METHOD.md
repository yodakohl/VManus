# GDT272 — frozen q density/expansion mechanism test

## Rationale and chronology

GDT267 reported that the q13 earlier-minus-later q-rate effect correlates
`0.860` with the log earlier/later record group-count ratio. GDT270 then showed
that q remains separable after exact host/compiler matching, while GDT271 found
a positive but page-unstable Q20 echo. This method freezes a mechanistic
prediction before any GDT271 page score is joined to Q20 density features:

> The page-level compiler-matched q conditional score follows early-versus-
> late record density, rather than a universal ordinal by itself.

The GDT271 outcome is already public, so this is metric-level prospective
testing on an exposed panel, not observer-blind validation.

## Frozen panel and predictors

Use the same thirteen Q20 pages and first/last equal-sized star-record halves
as GDT271. Middle records on odd-sized pages remain excluded. From the
f84-free `gdt127_q20_field_inventory.tsv`, compute three page predictors in
ZL3b without reading wrapper or PAGE_HOST values:

1. `GROUP_COUNT_LOG_RATIO` — log((early source groups + 0.5)/(late + 0.5));
2. `FIELD_COUNT_LOG_RATIO` — log((early HPR2 fields + 0.5)/(late + 0.5));
3. `LINE_COUNT_LOG_RATIO` — log((early physical loci + 0.5)/(late + 0.5)).

The primary predictor is group count. Field and line count are declared
mechanism sensitivities. The freeze artifact publishes the predictor table and
its hashes before the outcome join.

## Outcome and tests

The outcome is the already fixed GDT271 primary page conditional score for
`PAGE_HOST_PAGE_OTHER_COMPILER`, one value per page. It is reconstructed from
`gdt271_page_scores.tsv`; no alternative q endpoint is scanned.

For each predictor report Pearson correlation, rank correlation, sign
agreement excluding exact zeroes, linear slope, and all thirteen leave-one-
page Pearson correlations. The directional prediction is positive.

Use 65,536 deterministic outcome permutations over the thirteen fixed pages.
The seed is SHA-256 of the literal string
`GDT272_Q_DENSITY_MECHANISM_NULL_V1`. The same worlds score all three
predictors; report local and max-three one-sided inclusive p-values.

The frozen primary gate requires:

- positive group-count Pearson correlation;
- at least 9/13 sign agreements;
- at least 11/13 positive leave-one-page correlations; and
- group-count max-three p <= 0.05.

## Claim ceiling

A pass would support a density/expansion-conditioned q rendering mechanism in
Q20; a failure would leave q's exact mechanism unresolved. Neither outcome
assigns q a word, morpheme, sound, semantic value, language, plaintext, or
translation. No f84r access is authorized or performed.
