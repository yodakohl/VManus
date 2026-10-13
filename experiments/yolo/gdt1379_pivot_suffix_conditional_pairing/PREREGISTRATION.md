# GDT1379 — Fixed-pivot suffix exchange under parameter-free local control

## Decision note and prior scope

IDEA1051 asks whether a word's entire prefix and suffix retain a preferred
pairing after every observable position-dependent one-step transition factor
is held constant. This follows1279/1308/1374 positives, rather than fitting a
new historical passage. It differs from1246's equal-half endpoint,1280's
per-word bigram inventory, and1375's fitted weighted class-stream null. All
original failures remain. IL026's registered root/shell line-level synthetic
power stop is retained; its primary report was not recovered in the bounded
local/public/reachable-history search, so no complete re-audit is claimed.

Unknown: capacity and observed pairing excess under this exact invariant.
Positive changes the accepted conditional observable-state independence model;
nonconfirmation does not prove its sufficiency; inadequate capacity stops the
contrast. Budget35minutes including prior review, implementation, validation
and publication. No threshold, split, score, conditioning or source repairs.

## Frozen sample and pooling

Use exactly1308held EVENTS (even physical leaves,n>=4), the unchanged1308MODEL,
and1233strict source rows joined by reader/id. Validate rawunits/IDs/lengths,
631allowlist, Pkind and two definite outer spaces; f1r,f116v,allf84prefixes
excluded. Both oldsourceunit andeventunit lists must match. All22workingunits,
including m, retained. No freshrawquery, image, reserve or fitting. Historical
exposure remains; this is not independent confirmation. Readers separate.

For length n set k=floor(n/2), L=w[:k], R=w[k:], pivot=L[-1]. Pools have exact
(page,Currier,n,firstunit,lastunit,pivot). Sort poolkeys lexicographically;
keep original1233row order within each pool and repeated occurrences separately.
Every heldword enters one pool, including immobile singleton pools. The split
is a fixed convention, not an identified morpheme boundary. Do not search cuts.

Hold each L_i fixed and permute complete R_j among rows. The reconstructed word
is L_i+R_j. Length, first/last units, all position-specific unit margins and
all aggregate (position,previousunit,nextunit) counts are unchanged perpool.
Edges insideL stay withrow; edges insideR and pivot->firstR stay withdonorcolumn
because pivot is common. For arbitrary positive table P_i(current|previous,
page,Currier,n), logP(L_iR_j)=a_i+b_j. Thus every labelled permutation has the
same product of wordlikelihoods, without estimating the table. Conditioning on
both occurrence bags therefore gives a uniform labelled assignment under the
exchangeable factorized null. Identical suffix strings retain multiplicities.
If the observed margins have positive support, no new local transition is made.

This is an independence/exchangeability hypothesis. Unbound within-page topic,
source selection, individual occurrence context or latent model mixture can
violate it. It is not a theorem that human words use these22units or boundaries.
1316's unmixed H component also factorizes at this cut on positive support;
MIX_H need not. A mixture of independent binary components with both marginals
0.9 or both0.1 has cell masses0.41,0.09,0.09,0.41 and unequal pairing products.
No H filter or H score is used. No inference of wholeword memory from coupling.

## Fixed whole-form association score

Reuse1308 M1 P and exact TRAIN whole-form Q by(Currier,n), without refitting.
P uses alpha0.5 over22units, position-conditioned previousunit contexts.
M=(P+Q)/2 when the whole TRAINcell is nonempty; otherwise M=P.
S_ij=log(M(L_iR_j)/P(L_iR_j)), computed stably. Assert observed P and gain agree
with old1308events and that logP matrices have zero additive rectangles within
1e-9. Save every S/logP matrix and first mobility witness. A score-mobile pool
has some anchored rectangle S_ij+S_00-S_i0-S_0j with abs>1e-12; use the first
row-major i,j starting1. O=sum diagonalS; exact uniform E=sum(rowmeanS).

The primary is equal-physical-leaf mean of sum_pool(O-E)/number_of_words, using
ALL score-mobile pools and all their words. Negative and zero leaves remain.
Save perleaf words/excess. Also save all-pool descriptive mean using allheldwords;
it cannot replace the primary. No novel-only or favorable-form cohort. O-E is
an association-score excess, NOT1375's normalized conditional prediction gain;
no mixture-permanent normalization or factorial enumeration is required here.

Capacity requires>=100primaryword occurrences and>=10physicalleaves perreader.
If met, sample199worlds with Python Random(20261013), reset perreader; fixed
poolorder, shuffle list(range(N)) independently per mobilepool/world. Nullscore
uses the same E, denominators and leaf set. p=(1+#null>=observed-1e-12)/200.
Require meanexcess>=0.01nats/word, at least2/3positiveleaves and p<=0.05/3.
Constant aggregate null range<=1e-12 is NO_SCORE_MOBILITY. Otherwise statuses
NO_CAPACITY, CONDITIONAL_PIVOT_PARTNER_DEPENDENCE, or
NO_RETAINED_PIVOT_PARTNER_EXCESS. Report eachreader separately; call a robust
across-reading lead only if allthreepass. They are not independent replications.
Tails are exposed exploratory conditional diagnostics, not project-wide
significance or a general Markov/language exclusion. No pool-size cap.

## Reproducibility and stops

Sourcefree controls prove/check exact positionaledge preservation and uniform
mean on small asymmetric models and repeatedsuffixes, plus mobile/immobile
score examples. Independent validator reconstructs source joins, wholeform
probabilities, everypair and the same declared permutations without importing
primary code. Freeze protocol, programs, spec, proofreview and inputs before
newpool construction or counts. Successful software validation is not meaning.
No new relation-edge score. Failed original1375gate is not superseded.
At any stop retain allzeros/negative cases and do not widen conditioning or
change scorer, midpoint, units, threshold or unknown-form treatment.
