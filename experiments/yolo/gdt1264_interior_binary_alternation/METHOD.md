# GDT1264: one learned binary distinction in word interiors

## Decision and prior difference
Portable local transitions and position effects are already established in the
source-native Markov/stage primaries.1263rejected a monotone fixed-symbol class
sort but retained a coarse recurrent outer envelope. The genuinely unknown
question here is whether ONE learned binary symbol feature captures a recurring
alternation preference inside words, after accounting for each word's own symbol
inventory. This is a compact descriptive predictor, not a new proof of generic
local dependence, an asserted writer or a vowel/consonant identification.
A fixed positive cross-leaf result would justify retaining this small inner-shape
constraint in future writer selection. Failure closes this fixed learner/test;
no3class, alternate split, smoothing or vowel relabeling follows automatically.
Smallest adequate test: train one binary partition and evaluate it without change.
No new encoder, corpus or language model. Inclusive35minute budget17:27--18:02UTC
includes predecessor review, implementation, validation and local closure.

## Fixed exposed data and feature fitting
Use unchanged1233exact whole-group working units,179selectors, readers separate.
Drop exactly first and last working unit of each group; retain interiors of length
n>=3 (shorter interiors have no useful order distinction and remain counted as
excluded). No word boundary is crossed or repaired. TRAINis odd physical f-number,
TESTeven f-number, as915's physical-leaf convention. All were historically exposed;
this is a new exploratory phase split, not independent confirmation or reserve.
Only ZL trains the partition. TRAINactive units alone get fitted labels; any held
interior with an unseen unit is reported as unscorable, never silently assigned
an invented class. Keep its full denominator/exclusion count. No new eligibility
or active-alphabet change after looking at held results.
For a fixed class partition and an interior with A/Bcounts a,b,n=a+b, uniform
permutation of its own units has expected cross-class adjacency count2ab/n.
Training score is pooled sum(observedcross-2ab/n). It equals a weighted cut:
W_uv=observedundirecteduvadjacencies - sum_words(2count(u)count(v)/n), u!=v.
Compute each aggregate weight exactly as a rational, multiply by10^6 and round
ties-to-even to integer. This fixed numerical precision defines the training
objective, not a statistically tuned regularizer. Exhaustively optimize ALL
nontrivial binary partitions of active symbols, with the lexically first symbol
anchored to0. Choose the smallest numerical bitmask among exact objective ties.
No0-bit allsamepartition, no interpretation of0/1asvowels/consonants. Save the
complete weight matrix, optimum and every tied optimum count. Freeze the fitted
partition artifact before evaluating TEST. No held statistic is used for fitting.

## Evaluation and decision
Reuse the unchanged ZLlabels in each reader. For each physical TESTleaf, sum
cross-minus-expectation and divide by that leaf's total(n-1)scorableinterior edges.
Average these leaf effects equally. Evaluate ALLeligible held groups and the
separate UNSEEN_WHOLEcohort whose complete original group was absent from that
reader's own odd-leaf whole vocabulary. Do not define novelty by trimmed body.
Report all leaves, tokens, unit coverage, exact score numerators and zero/negative
leaves. One-token leaves remain; expose that support rather than tune a cutoff.
Primary descriptive joint gate: BOTH ZLcohorts have>=10scorablephysical leaves,
>=2/3positive leaves and equal-leaf mean excess>=0.03. These are declared
engineering materiality thresholds, not significance levels or evidence of sounds.
IT/RFare separate sensitivities to one manuscript, not extra primary successes.
Use rational arithmetic for reported effects/gates. No new pvalue/nullsimulation.
The permutation expectation preserves the exact interior bag, not its position-
specific frequencies. A fixed positional template can therefore also explain a
positive. This does NOT establish extra dependence beyond the old5-position model,
syllables, morphology, semantics or a reading direction (switching is symmetric).

## Verification and stop
Independent validation imports no runner: rebuild symbol weights and all leaf
scores, check exact chosen numerical objective by exhaustive vectorized binary
masks against the primary Gray-code C++search, and retain all source IDs. Small
matrix enumeration and positive alternating/fully permuted-bag fixtures verify
feature fitting/expectations. Both program families and protocol are hash-locked
before native training. Native prediction already learned from exposed data is
not independent scientific confirmation. No native word meaning is assigned.
No new rawquery, image, f84/f84r, f116v, reserve or source language. Local only.
