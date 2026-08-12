# FPR001 f37v one-shot ordered-root target

Status: **PREREGISTERED; TARGET FORMAL CONTENT UNOPENED**.

## Fixed evidence and statistic

The externally fixed relation is pharmaceutical label `f102r1.2` to Herbal
page `f37v`. The already exposed query is exactly
`ot+od+e+od+or`. This experiment uses the frozen manual-derived formal
interlinear only; ZL3b, IT2a, and RF1b are alternate readings of one page.

For each reading, retain rows with section H, Currier A, hand 1, and
`CONFIRMED_PROSE`. Split each row's `root_sequence` on spaces into parsed
words, then each word on `+` into roots. The page score is the maximum LCS
length between any one complete word and the five-root query. The 94
background pages are exactly the capacity/calibration panel; f37v is excluded
from them before any formal field is indexed.

For each reading, the inclusive rank is one plus the number of background
pages whose score is at least the f37v score. The pooled score is the sum of
the three reading scores, and its inclusive rank is defined identically from
the per-page sums. Division by 95 gives the empirical rank fraction.

The target passes only if all frozen gates pass:

1. f37v score is at least 3 in every reading;
2. inclusive rank is exactly 1/95 in every reading;
3. pooled inclusive rank is exactly 1/95;
4. all three readings therefore agree on the positive decision; and
5. all rank fractions are at most the prospectively frozen `.02` ceiling.

The scorer must report every f37v word attaining that reading's maximum, with
edition, locus, zero-based word index, aligned literal surface word, complete
root word, and a deterministic LCS witness. The aligned surface word is the
text before the first `=` in the corresponding ` | `-separated
`formal_interlinear` entry; manual `surface` groups are not assumed to align
one-for-one with parsed root words. The witness maximizes length, then
chooses the lexicographically smallest query-index tuple and earliest target-
index tuple. These fields may be opened only during this registered one-shot
run. They may describe an anonymous manuscript-internal recurrence; they are
not translations.

## Isolation and decision

Before the registration freeze is published, no f37v `surface`,
`root_sequence`, `formal_interlinear`, match, score, rank, or best word may be
accessed. The freeze binds this specification, the already published
calibration and validation, the scorer, an independent validator, the source
table, the registration commit, and the absence of all four target/validation
outputs. Outputs are no-clobber.

The first frozen invocation stopped output-free at non-target row f10r.3
before any f37v row because it incorrectly required manual surface-group count
to equal parsed-root word count. The replacement freeze may correct only the
surface-witness alignment above. It must bind the aborted freeze SHA and must
not alter the query, statistic, background, gates, thresholds, or decisions.

If any gate fails, the decision is
`FINAL_NONCONFIRMATION_FIFTH_RELATION_ORDERED_ROOT`; do not lower the LCS
threshold, change the query, move to cross-word matching, select a reading, or
mine another word on f37v. If all gates pass, the strongest permitted decision
is `PASS_ANONYMOUS_SAME_PLANT_ORDERED_ROOT_RECURRENCE`.

Neither outcome establishes a plant name, component, word boundary, morpheme,
sound, language, cipher, plaintext, meaning, or translation.
