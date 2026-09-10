# GDT907 — exploratory joins across written line seams

## Decision before target computation

Unknown: do adjacent line-final/line-initial raw groups concatenate into an
elsewhere-attested whole more often than endpoint reassignment within the same
written paragraph and the same right-fragment length? A positive excess would
motivate native investigation of specific possible word continuations; absence
would leave that route unselected. Neither outcome identifies meanings or proves
hyphenation: ordinary cross-line syntax is an explicit competing explanation.
No source transcript is altered and no decoder is built.

GDT850 inventories same-line qolchedy/qol chedy; GDT853 tests same-line neighbor
prediction and stops at zero strict metadata pairs. This experiment does not
relax those pairs or score that predictor: the observation and endpoint are the
physical sequence of separate lines. GDT800/801 establish line-final m behavior;
that does not establish concatenation across a line. Route-check and bounded
memory found no primary cross-line concatenation test. Lexical absence does not
prove scientific novelty. The source schema (metadata fields and kind/paragraph
flag counts only) was inspected before registration; no seams were enumerated.

## Fixed discovery scope and computation

Use only the three hash-bound GDT851 guarded JSON source projections, all179
selectors, previously exposed. f84/f84r remain forbidden. No new image, page,
held corpus, language source, normalization or substring meaning enters.
These are three alternate readings of one manuscript, not independent trials.

For each reading, retain kind P lines with exact page.NUMBER loci, complete
contiguous one-based group indices, and their original metadata. A seam links
successive numeric loci on one selector only when the first is not flagged
paragraph-end and the next is not paragraph-start, both are P, and hand/section
agree, and the next code is +P0 or +P1 (ordinary below-line paragraph
continuation). Recorded same-line and special-location codes are not crossed.
Missing loci break runs. The first line may be midparagraph; a run is
only an uninterrupted observed segment, not proof of a complete paragraph.
An uncertain/annotated end or head is excluded if not literal [a-z]+. No edge
is inferred across a recorded same-line continuation, paragraph boundary,
omitted locus or page. Unannotated image obstacles cannot be excluded by this
text-only rule; source metadata is not a fresh native layout observation.

A candidate joins the complete last group A to the complete first group B,
without deleting any letter. W=A+B must occur as a single plain raw group in
a P line on a DIFFERENT physical leaf in that reading. Keep all lengths and
all exact source witnesses. This is a written-string relation, not word identity.

Stratify eligible seams by the uninterrupted run and length(B). Within each
stratum, retain the observed A list and B list. Enumerate its complete A_i+B_j
matrix against the leave-physical-leaf-out whole vocabulary. Report observed
hits, exact reassignment mean (sum of matrix/n), diagonal excess and number
of exchangeable strata/folios. Singleton strata contribute equal observed and
expected counts and no evidence of sequence specificity. Also report, as a
fixed descriptive diagnostic, the subset with both fragments at least2letters;
it is not an alternative success criterion.

Generate9999 independent uniform B permutations per stratum with Python
random.Random(907), readings in SPEC order and strata in sorted-key order.
Report (1 + count(null >= observed))/10000, the full null score vector and
seed. This is an exploratory conditional randomization comparison, not a
confirmatory semantic test or a model of the manuscript writing process.
No significance threshold selects a translation or licenses recombining text.
All hits, all eligible seams, source witness IDs, row/column endpoints and
compact matrix certificates survive regardless of outcome. Report agreement
at identical locus pairs across the readings, without treating it as replication.

## Completion and limits

Smallest adequate pass: one complete census, its fixed reassignments, a separate
source-to-result implementation, and publication of code/protocol/results.
The user withdrew the time budget; no elapsed-time cutoff is imposed. Finish
this finite pass without adding new fragment rules, larger windows or decoders.
A native follow-up requires a separately justified candidate and must respect
the current visual admissions. GDT388 semantic relation scoring is not claimed;
this is a text-only exploratory seam statistic without named endpoints.
