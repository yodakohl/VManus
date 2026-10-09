# GDT1226 — fixed-profile mixture, not a rescued writer

Selected06:44UTC on6October2026, preparation from06:40UTC; total45minutes
through07:25UTC including validation/local closure. Decision note and primary
predecessors: existing HAND_WRITER_RECONSTRUCTION dossier. No public
preregistration or push under the4October local construction exception.

Question: can ANY convex mixture of the four existing1202 empirical8000-word
frequency profiles meet the old top-ten upper bound if each exact source word
has at most TWO output spellings globally across all books? The profiles are
b4,w1,bs1,gr1 in1202/FREQUENCIES.json, unchanged. No token, orthography,
punctuation, source-window or alias-count change. This is a new quantified
compilation scope, not a rerun of the old single-book decision. The files are
edition projections; original CoReMA writing was already used in1166/1171.

For book counts p_b(w) summing8000, mix c(w)=sum_b lambda_b*p_b(w),
lambda>=0,sum1. Any five source words occupy at most ten output forms;
their total mass therefore lower-bounds the ten largest output masses,
including with homographic merging. Giving every word two private equal
halves attains exactly the five-largest source sum in a continuous relaxation.
This is not a physical writer, integer8000-word text or public spelling rule.

Minimize that sum over all four weights. Bounded cutting-plane LP: start with
distinct individual-book top5 sets (lexical ties), four weights and epigraph;
add the actual top5 set at each candidate. At most100iterations, numeric
gap1e-7. SciPy1.14.1 HiGHS is only a certificate proposer. Convert nonnegative
primal/dual coefficients to Fractions (denominator<=10^9), then normalize
exactly. Primal weights give exact upper U by sorting all mixed word masses.
Convex dual weights over five-word cuts give exact lower
B=min_b(sum_cut d_cut*count_b(cut)), valid for every mixture.
Save all cuts, coefficients, bounds and trace. Only rational B/U decide.
An unresolved bracket stays UNKNOWN; no extra search, source or tolerance.

For EACH unchanged1174 reader limit (old top10 count+400): B>limit means
EXCLUDED; U<=limit means CONTINUOUS_NOT_EXCLUDED; otherwise UNKNOWN.
All excluded: EVERY_MIXTURE_TWO_ALIAS_CONCENTRATION_EXCLUDED.
All not excluded: CONCENTRATION_RELAXATION_FEASIBLE. Mixed determinate:
READER_SPECIFIC_MIXTURE_CAPACITY. Any unknown: UNRESOLVED_BOUND.
No type-capacity test, favored reader, new native count, integer rendering,
glyph metric, language identification or full statistical pass.

Separate validator uses neither runner nor SciPy. Rebuild the four old8000word
profiles from1177 recipe positions, check1202table/receipt identities and1174
limit arithmetic, then check every rational primal/dual certificate against
all words/books. Same author and exposed data, not independent confirmation.

Exclusion stops a pure mixing-only extension on THESE empirical profiles.
Non-exclusion keeps only continuous concentration open; no automatic writer.
Actual recipe selection/order, other book windows, languages/editions, more
aliases and morphology remain outside scope.1202 and every old decision stay.
No native raw data, image, reserve, f84/f84r/f116v or relation score accessed.
