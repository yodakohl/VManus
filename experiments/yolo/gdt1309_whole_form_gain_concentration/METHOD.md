# GDT1309: where the fixed whole-form gain comes from

Exploratory, post-result decomposition of1308, NOT a fresh prediction experiment.
Preparation began14:35:15UTC9October; inclusive40minute budget through15:15:15UTC
includes prior audit, this small calculation, validation and publication. No new
predictor, fit, smoothing, weight, split, cutoff-selected codebook or target data.

## Decision and prior audit
1308shows a small ALL-word gain from its full empirical table; it does not show
whether the positive contribution is concentrated in a handful of forms. This
matters before proposing a small list of exceptional spellings or assuming every
word needs its own arbitrary weight. The smallest adequate work is an EXACT
accounting of the existing fixed scores, with TRAIN-frequency versus post-hoc
gain rankings explicitly separated. If few forms dominate positive mass, prioritize
explaining those forms; if it is dispersed, do not describe1308as merely a few
special-word exceptions. Neither result proves a minimum dictionary size or
licenses a new optimized predictor. No large model implementation follows.

Read1308primary/protocol,398primary, composition/controls topics and route-check.
398's old opaque-type frequency/concentration failure is retained, not rerun.
The proposed first-to-last-unit followup was found to have a direct prior:
SOURCE_NATIVE_EDGE_COUPLING_TEST_SPEC and its negative target report. It already
added the first family to second/penultimate/length/locus-position/Currier,
withalpha.5and held-folio logscore. Removing the second-unit control and changing
alphabet/split is not enough reason to rerun it. Old result−.058951nat/group,
13/94positive leaves, remains nonconfirmation. No old payload reopened.

## Fixed accounting
Inputs are unchanged1308EVENTS,MODEL,RESULT and their validated source binding.
Keep readers separate. For reader r let L be its number of held physical leaves,
N_f its ALL-held occurrence count on leaf f, and g_i its fixed log(MIX/M1)score.
For each exact unit tuple w compute C_w=sum_{i:w_i=w} g_i/(L*N_f(i)). Then sum_wC_w
must equal1308's equal-leaf ALLgain. Do not renormalize after discarding words.
Let P=sum_wmax(C_w,0), N=sum_wmin(C_w,0). P+N is the original net gain. Positive
mass shares use P, NEVER the small net denominator. Also retain within-type
positive and negative occurrence contributions, since one type can change sign
between Currier cells.

Rank positive-net types by C_w decreasing, ties by tuple lexicographic order.
Report top1/5/10/20/50/100 shares of P and the minimum counts covering50%and90%
of P. This rank is selected on already scored EVALoutcomes and is descriptive,
not a preselected miniature lexicon or new held performance. No inferential PASS
threshold, p-value, causal count or universal construction bound.

Separately rank all TRAINtypes by total frequency summed across Currier/length
cells, decreasing, lexical tuple tie-break. Report the SAME original contributions
of TRAINtop20 versus its complement. This is not a refit after word removal.
Report exhaustive TRAIN-frequency bands0,1,2-4,5-19,20-99,100+with exact occurrence,
type and summed contribution totals. This is not the Q-positive/Q-zero distinction:
a globally known form can have zero Q in one Currier cell.

Retain one TSV row per EVALtype with exact form/units, train frequency/cell count,
held occurrence/leaf counts, signed/positive/negative occurrence contributions,
and Q-zero/Q-positive counts. Do not pool embedded strings, normalize spellings,
or equate alternate transcriptions with independent manuscripts. Familiar forms
may be inspected manually AFTER the full accounting; no word meanings inferred.

## Validation and ceiling
Independent implementation recomputes log ratios from saved probabilities,
reconstructs saved event counts/model frequencies, all per-type and band totals,
rankings and conservation identities; no runner import or native model refit.
Source-free signed-mass fixture demonstrates why top-positive/net percentages
can exceed100%and why a post-selected ranking is not an independently tested list.
Freeze code/protocol/input hashes before the calculation. Guarded caches only;
f84/f84rsealed,f116v/f1rbody/reserves unadmitted; no images or relation edges.
This report describes where an existing estimator gains/loses. It identifies no
natural-language unit, mnemonic lookup behavior, morphology, semantic root or
word meaning, and does not prove that a few-rule grammar cannot explain many forms.
