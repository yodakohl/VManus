# GDT1318: transfer learned one-unit boundary edits to complete word forms

Decision note10October2026. Inclusive08:43–09:18UTCbudget covers selection,
preparation, implementation, validation and publication. No edit-scope, weight,
threshold or smoothing repair after outcome; stop expansion at budget.

Unknown: do learned literal edge substitutions contribute a useful normalized
full-word predictor beyond1308's existing whole-frequency mixture? This is a
new form-generation contrast, not1316midpoint repair.160/161test operation-pair
compatibility/latentclasses;522/524rerank supplied surfaces' old component recipes;
746explicitly predicts no unseen forms. Their outcomes and unconfirmed old glosses
are not reused.914's local parallel-edit failure and1170's duplication stop remain.
No prior next-step decoder is adopted. Producer primary-method review found no
identical full-word sampler in this bounded predecessor set.

Fixed construction: use unchanged1308TRAINwhole/cell counts and held scores
(n>=4workingunits, oddTRAIN/evenheldphysicalleaves;Currier/exactn supplied).
For each Currier separately, take DISTINCTTRAINwhole unit tuples. For every
orderedpair of distinct types that differs ONLYat the first unit, add1to rule
(FIRST,old,new); for pairs differingONLYat the last unit, add1to(LAST,old,new).
Lengths within a pair necessarily match; pool rule counts across lengths within
Currier. No occurrence weighting, subtype threshold, glyph equivalence or value.

For a supplied(Currier,n)cell, draw a baseu with its empirical TRAINfrequencyQ.
Collect ALLFIRSTrules matchingu[0]andLASTrules matchingu[-1]. Choose ONErule with
probability proportional to its trainingpair count, using ONEcommon denominator
across both sides. Apply that single unit replacement. If no rule applies, outputu.
Call the resulting distributionE. Generate every result, including unattested
forms, and SUMprobabilities from every base/rule path that reaches the same output.
Do not restrict application to observed TRAINedges. No insertion/deletion/interior
edit, lengthchange, multiple edit, best-neighbor selection or source reconstruction.

Compare OLD=.5M1+.5Qto NEW=.5M1+.25Q+.25E. M1andQare frozen1308predictors.
Completely absent TRAINcells useM1inboth. All distributions normalize overALL22^n
strings, not just evaluation vocabulary. Length is preserved by every rule.
Primary gate onALLheld occurrences: >=100words,>=10physicalleaves, equal-leaf mean
log(NEW/OLD)>=.01and at least2/3positiveleaves. Additionally require>=100globally
TRAIN-unseen E-positive held occurrences across>=10leaves for productivecoverage.
ZLprimary;IT/RFsensitivities, not independentreplications. If both pass, retain a
limited predictive edge-edit component; otherwise do not select thisfixedsampler.
No general rejection of analogy or word formation follows either way.

Keep ALLwords and penalties. Report NEWvsM1as diagnostic, together with ALL,
GLOBAL_UNSEEN,GLOBAL_KNOWN,Epositive/Ezero cohorts and per-leaf scores. BeatingOLD
on unseenwords is mathematically automatic whenE>0becauseQ=0; it is NOTthe primary
success claim. No raw-unseen-score gate or retrospective revision of1316:1317's
interpretive limit is retained. No parameter or successcriterion is estimated
from this new held outcome. Exposed data, not reservedconfirmation or pvalue.

Outputs: complete rulecounts, finite Edistributions, all fixed heldscores, inventory
and totalmasschecks, newcoverage and primarydecision. Source-free fixtures must
include novel transferred output, identityfallback and multiple paths to oneoutput.
Primary group-by-remainder rulelearning and forward weighted generation; independent
checker discovers trainingneighbors by literal unit replacement and reconstructs
output probabilities by inverse paths. Rebuild source TRAINcounts from unchanged
1233/915to verify the old frozen model; baselineheldscores remainhashbound1318inputs.
Protocol/program/inputhasheslocked before rulelearning or targetscore.

Assumptions/ceiling:22units and definite gaps, Currier/lengthconditioning, exposed
split, fixed first/last edit and fixedweights. This is a probabilistic spelling
model, not a reversible semantic writer. It does not establish morphemes, synonyms,
meaning-preserving changes, source language or actual scribal operations. No old
semantic recipe labels are assigned. No newrawTSV/image/corpus, f84/f84r/f116v/f1rbody,
old327/336body or reservedmaterial. No further edit/window/mixture search follows.
