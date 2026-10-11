# GDT1333 — does word/site choice survive immediate expanded flanks?

Fixed11October2026 before flanking-context enumeration. Inclusive budget
07:49–08:35UTC for preparation, implementation, independent validation and
publication. No automatic extra conditioning, reweighting, source binding or
orientation selection after the result.

## Decision and primary predecessor review
1320supports word-conditioned choice beyond a Currier/height coin, in BOTH
stipulated bench/gallows expansion orders. It explicitly leaves local writing
context as a rival and says unseen source words gain exactly zero.1307's literal
mandatory-fusion counterexamples remain. The old four exact whole-word pairs
had no identical OUTER WORD neighbours: the5October dossier primary and its
stopped narrow lookup were read. This is not a broadened search for semantic
substitution between those words.1285's failed two-previous-unit next-symbol
predictor concerns a different outcome; no repair is performed.

Unknown: can whole-source-word AND opportunity-site identity predict fusion
beyond the two immediately surrounding source primitives? Human stroke joining
could depend locally on both adjacent shapes;1320does not isolate that. The
producer's new1001whole-word port-planning sketch supplies a rival intuition,
not native values or proof of this mechanism. It is not used as a fitted model.

If residual gain survives, the fixed independent local coin is insufficient
under the stated conditioning/selection assumptions; word spelling memory,
more distant geometry, position, hand or correlated events remain distinct
alternatives. If it fails, no retained residual gain is found; local sufficiency
is NOT proved. If mobile capacity fails, stop without calibration. No outcome
identifies true ligatures, expansion order, pronunciation or word meaning.
This is one diagnostic decision about the scope of1320's positive structural
result, not an attempt to rescue its rejected uniform habit or decode a passage.

## Fixed data and binding
Reuse1320OPPORTUNITIES and independently reconstruct them from unchanged1233
strict Pgroups and915source metadata. Same631allowlist and Currier A/B only.
No new source, image, mixed TSV, reserve, f84/f84r, f116v, f1r body or327/336body.
Previously exposed odd-numbered physical leaves TRAIN, even HELD; subpanels
share physical leaf. Readers separate; six cases ZL/IT/RF times BH/HB.
BH: cHh->ch,H; HB: cHh->H,ch, H=k,t,p,f. Other working units remain literal.
Under each orientation opportunities are disjoint and expansion is invariant
to fused/separate spelling. This remains a stipulated18primitive source, not
an inferred alphabet. The target y=1 iff the original pair was fused.

For opportunity at expanded source index j, pair covers j,j+1. L=source[j-1]
or BOS if j=0; R=source[j+2] or EOS at the end. Distinct BOS/EOS are analysis
boundary labels, never written signs. Local key=(Currier,height,L,R).
Word/site key=(Currier,height,complete expanded source tuple,j). It determines
the local key exactly; repeated same-height sites in one word remain distinct.
This differs explicitly from1320's word-only alternative. Adding j is needed
for nested conditioning, not a claim of native absolute-position causation.

## Null, predictors and primary statistic
Null: conditional on fixed source words, sites and Currier, independent choices
with arbitrary probabilities p(C,H,L,R). Opportunity admission/transcription
confidence is assumed independent of choice conditional on these inputs.
Cross-site, leaf/hand, longer context or geometric dependencies can violate this
null; rejection does not uniquely attribute the residual to lexical identity.

TRAIN only fits three nested rates, fixed smoothing throughout:
 pCH=(fCH+0.5)/(nCH+1)
 pLocal=(fLocal+2*pCH)/(nLocal+2)
 pWordSite=(fWordSite+2*pLocal)/(nWordSite+2).
An unseen word/site falls back exactly to pLocal. No hyperparameter fit.

A mobile local stratum has0<F<N across its fixed TRAIN+HELD opportunities.
This eligibility depends only on totals preserved by every declared permutation.
Primary scoring uses only HELD events in mobile strata. All TRAIN events may
fit predictors. For each eligible event compute log pWordSite(y)/pLocal(y),
average within physical leaf then equally over contributing leaves. Save full
held probabilities and eligibility flags. Full-held and local-vs-CH gains are
DESCRIPTIVE only, no additional significance or success claim attached.

Capacity: at least100mobile HELD opportunities on at least10physical leaves.
If false, record NO_MOBILE_CAPACITY and run zero native permutations in that case.
If true, shuffle y within each local stratum across TRAIN+HELD, preserving all
source/split/site fields and local fused totals. Refit ALL predictors each time.
1999replicates, seed1333reset separately for every case. No added permutations.
Monte Carlo p=(1+#null scores>=observed)/2000. Retain residual only if gain>=0.01
nats/opportunity, >=2/3contributing leaves strictly positive and p<=0.05/6.
Six fixed cases; do not pool readers or choose BH/HB by comparing scores.
Report RESIDUAL_WORD_SITE_GAIN or NO_RETAINED_RESIDUAL_GAIN per capable case.

Keep TRAIN-unseen word/site counts and their exactly-zero contributions; no
claim of productive prediction of new forms. Every relevant negative leaf is
retained. Primary mobile eligibility, training keys and null are unchanged at
outcome. No extra position/hand features or relaxed gates follow failure.

## Validation and outputs
Before native scores, toy fixtures check that word/site determines flanks;
multiple sites remain distinct; unseen word/site fallback is exact; mobile
stratum membership is unchanged by permutations; singleton/all-equal strata
are excluded. A tiny binary labelled stratum enumerates all label allocations
and verifies the conditional exchangeable sample space.

Runner uses cached1320opportunities; independent validator imports no runner,
re-expands tagged original units, joins all61,181source groups to915 and checks
cache equality. Recompute train count tables/probabilities, mobile and unseen
counts, equal-leaf gains, every null replicate and all decisions with separately
written estimators. Sharing declared seed/RNG to reproduce permutations is
computational validation, not an independent biological/linguistic observation.
Save held probabilities, compact result and all null scores; cached opportunity
source remains referenced by hash. This is a conditional spelling comparison,
not a semantic relation packet or GDT388meaning score.

Mobile scoring conditions on observed stratum totals and is not an unconditional
future prediction claim. Nominal mobile capacity need not ensure statistic
variation or trained word/site overlap; constant null scores give their actual
pvalue without a new feature or gate. Zero-gain/unseen-only mobile leaves remain
in the denominator and positive-leaf test.
