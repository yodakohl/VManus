# GDT1375 — Small positive whole-form gains fail the joint consistency criterion

**NO_RETAINED_CONDITIONAL_WHOLE_GAIN in allthree readings.** After the fixed
local1279/1308Markov structure is built into partnerassignment probabilities,
1308's frozen wholeform mixture gives positive mean conditional gains. However,
none reaches the required two-thirds-positive-leaf consistency. ZLalso falls
below the0.01effect threshold; RFfails the three-comparison pthreshold. Original
1374coupling remains positive. This outcome is NOTproof of local sufficiency
or absence of all whole-form information.

## Complete primary result

The score is normalized conditional loglikelihoodratio of frozenMIX_Q versus
frozenM1, divided by words withinleaf then averaged equally acrossinformative
leaves. Bothmodels are conditioned on the same complete classstream inventories,
mask,page,Currier andexactends. Positive favors the wholeform mixture.

| Reader | Residual-mobile pools / words | Positive / primary leaves | Mean gain nats/word | Conditional upper p | Failed criteria |
|---|---:|---:|---:|---:|---|
| IT2a |158 /601|18 /31|+0.018784|0.005|Leaf consistency|
| RF1b |145 /542|16 /33|+0.014710|0.025|Leaf consistency; p<=0.05/3|
| ZL3b |153 /564|19 /32|+0.007729|0.015|Leaf consistency; mean>=0.01|

All nominalcapacity requirements pass; reference scoresvary. This is not a
capacitystop. Positive averages and IT/ZLconditional deviations are retained,
not erased by the failed conjunction. Their significance is conditional onthe
fixed fittedtable/reference andexposed subset, not project-wide or a probability
of linguistic truth. Alternative readings concern one manuscript.

The199draw mean/range under the localreference is IT−0.091366/[−0.210715,+0.011563],
RF−0.089341/[−0.279331,+0.030853],ZL−0.115241/[−0.309901,+0.012600]. Negative
expected likelihoodratios under P are required by the KLidentity, not a broken
null. Everydraw, everynegativeleaf andall originaldecisions remain saved.

## What the weighted comparison actually does

1374used uniform partnerexchanges; a favored localjoining rule could explain its
excess.1375therefore assigns each possible completepartner arrangement pi a
probability proportional to the PRODUCT of frozenM1wholeword probabilities.
The rival uses the PRODUCT of frozen1308MIX_Qprobabilities instead. Qis oldTRAIN
wholeformfrequency; no new corpus, fitting, cut, weight or smoothing is introduced.

For a pool, let Lp(pi) and Lm(pi) be summed wordlogprobabilities and let Zp,Zm
sum the respective probabilities over ALLlabeled partnerassignments. Then

    R(pi) = Lm(pi) - Lp(pi) - (log Zm - log Zp).

Subtracting BOTHnormalizers is essential. A rawsum of wholeword gains would not
answer this conditionalquestion. Under the localconditionalmodel E_P R equals
minusKL(P_cond||M_cond), hence is nonpositive. All computed poolmeans satisfy it.
Duplicate streams retain their occurrence multiplicities; the completefinite
reference is evaluated numerically with stableweights, not asserted exactrational.

We verify that1308M1and1279EXACT counts agree in everyevaluated noninitialcontext.
With fixedmask andexactfirst/lastunits, firstunit,sameclass andword-edge factors
are row/column terms. They cancel over completebijections. Thus1374's strictly
INNERcrosscosts ALREADYyield the same conditional local law as the fullwordP.
Maximum checked cancellation-rectangle residual is5.329e-15. No missingedge
constraint in1374is claimed. An earlier source-free review wording tothat effect
was corrected by an appended receipt before1375registration.

## Computational and statistical scope

Only1374C-mobilepools with2<=N<=8were preselected for bounded exhaustive
assignmentenumeration (atmost40320assignmentsperpool). This is not all1374data.

| Reader | Original mobile pools | N>8 excluded pools / words | Computable pools / words | Residual-immobile pools |
|---|---:|---:|---:|---:|
| IT2a |212|33 /378|179 /648|21|
| RF1b |179|17 /192|162 /579|17|
| ZL3b |194|24 /261|170 /603|17|

The primary further requires mobility of the NEWwhole/local ratio matrix, not
only1374localscore mobility. Selection depends on fixed streambags andmatrices,
not the observedassignment's rank. Numerical1e-12mobility remains operational,
not exact symbolicconstancy. No sizecap orpoolconditioning was relaxed afterward.
Pools originallyC-immobile could still possess a wholeformresidual; they are not
examined here. Largepools also remainunscored. No broadnegative inference follows.

Across ALLcomputablepools, including residual-immobile ones, descriptive equal-
leaf gains are+0.019730/+0.014364/+0.012086IT/RF/ZLon33/34/33leaves. Different
within-leaf denominators andleafsets mean these neednot be smaller than the
primarymeans. They are not an alternative successgate. Nor may1375word-level
gains be subtracted from1374edge-level gains as a percentage "explained".

## Interpretation and decision

The pairedstream structure has preferred localcompatibilities (1374). The new
fixedwholeform addition gives an uneven positive residual but no retained joint
lead on this computablesubset. Keep both statements. It would be wrong to say
"all structure is local", "words have no information", or "a wholeworddictionary
is established". A different localconditionalmodel, higherorder shape constraints,
unmodeledpage/topic/position variation andselection remain possible explanations.

Stop this fixed conditionalwholeform increment without retuning mixture, Ncap,
pools or thresholds. Do not infer a need for linguistic wholewordmemory from
1374alone. No new phoneme, language, sourceword identity, actualclassstream,
morphology or meaning is selected. Confirmed lexemes remain0.

A separate selection review also confirms that the22workingunit parser is
uniquelydecodable but NOTprefix-free (s/sh). Parserclosure, fixedends andm-exclusion
do not algebraicallyforce1374coupling. A source-free example shows that genuinely
joint readability/admission selection COULDinduce coupling from independent
preselection streams. This is a possible confound, not evidence that the actual
finding is an artifact. The existing1374conditional scope remains appropriate.

## Independent verification and access

Primary enumerates allpermutations. The independentvalidator instead computes
partitionfunctions andweighted moments with subsetdynamicprogramming, anddraws
from lexicographic prefixblocks usingthe SAMEsingleuniformvariate. Every511
computablepool's matrices, normalizers, observed/reference means,tableagreement,
exclusions, weights and597drawscores match: PASS. No primaryimports orMCMC.
Sourcefreefixtures include repeateddonors, identicalconditionalmodels, nonnull
conditionalLR, CDFcomparisons androw/columncancellation.

Protocol, programs, proof/validator receipts andinputs were hash-locked before
newweights.1374pooldata were previously inspected; this is a selected followup,
not a newblind confirmation. No rawTSV,newnativecorpus,image,source-language text,
f84/f84r,f116v,f1rbody,legacybody or reserve access. Allold1374and1308results remain
unchanged; this independently recorded comparison doesnot replace their gates.
