# GDT1279: matched edge/interior, class/exact-symbol prediction

## Decision and predecessors
The old exact-position-controlled full-symbol Markov result is positive, but
includes first-to-second and penultimate-to-last transitions. The old endpoint-
free nonconfirmation tests POSITION structure, not endpoint-free MARKOV gain.
1278predicts binaryordergiveninventory and fails; it cannot establish whether
specific symbol identity was the missing ingredient in a different prediction
problem.1264/65remain positive associations;1266distantcapacitystop remains.
Unknown: does portable exact-symbol prediction remain on transitions touching
neither end unit, and does the exact previous unit outperform its fixed1264class
on those SAME cases? A positive identifies a usable inner predictive constraint;
a negative prevents assuming the old complete-word gain extends there underthis
instrument. Class-vs-exact outcome chooses whether thisparticularcompression
loses predictive information; not whether every2classwriter is impossible.
Smallest test: three elementary count tables, fixed smoothing, same sources,
positions and split; no model tuning, decoder, classfit, newreferenceorcorpus.
Budget14:33--15:18UTC8October2026 includes priorreview, design, implementation,
verification and localclosure. Stop expansion atdeadline; no automaticrepair.

## Frozen source and common support
Use unchanged1233GROUPScache (P prose, bothouterspacesdefinite, pureletterraw,
fixed22workingunits). Join Currier by(reader,locus) from915cachedSOURCE_DISCOVERY
andSOURCE_EVALUATION JSONs. Require each targetrow's page/edition/kind and every
exact groupID/rawstring match that cachedline; no query to mixedrawTSV.
All179oldselectors only; assert f84/f84r/f116vabsent. No images/reserves/newdata.
Words of length n>=4 only inTRAINandTEST so both edgeandinner opportunities exist.
TRAINoddphysicalleaf numbers, TESTeven. Fit eachreader independently, ZLprimary.
Readers are alternate readings, not replications. All data already exposed.

Transition predicts x_i from x_(i-1), i=1..n-1(zero-based). EDGE iff i=1 or i=n-1;
INNER otherwise(2<=i<=n-2): neither endpoint participates. GivenfeaturesinALL
models are Currier(rawmetadata,includinganyunknownclass),exactwholelengthn,
exacttargetordinali. No wordidentity, pageID, outerunitvalues or wholebag supplied.
Use1264classesfrozen. If previousunit hasno class(m), exclude THAT transition
from ALLthree models inbothtraining/test; count excludedopportunitiesexplicitly.
Nextunit maybem:fullfixed22alphabetremainsavailable. Neverinventclassm.
Thus every comparison uses identicalevent population; no classfallback advantage.

## Three probabilities, no fitting choices
Let c=(Currier,n,i); outputalphabetfixed22unitsfrom1233SPEC.
POS counts nextunits under c.
BIT counts nextunits under(c,class(previousunit)).
EXACT counts nextunits under(c,previousunit).
For every model p(next=v|context)=(count(v)+.5)/(total+22*.5).
Unseencontexts predictuniform1/22. All22outcomesretained, no rareunitcutoff.
This inherits the old exactpositionMarkovcore's additive.5 rule, notits population
or24symbolalphabet. No smoother, hyperparameterselection, borrowedlabels or
post-resultfallback. Models predict the SAME exactnextunit; parameter-count and
sparsitydifferencesremain partofthisfixedcomparisontheyarenotcausalestimates.
Serialize/freeze counts beforeheldevaluation. Protocol/programs lockedbeforefit.

## Scores and fixed outcomes
For everycommontransition save all3logprobabilities and theirsourceID/index.
Within eachphysicalleaf, gain is summedloglikelihooddifference/transitioncount;
primarymean givesleavesequalweight. Report eventmean too, notalternatecriterion.
Cohorts ALL and UNSEEN_INTERIOR: trimmedexactunitsequenceabsentfromownreaderodd
n>=4inventory. Novelty is observed-outcome-defined; probabilities areNOT
renormalizedonthenoveltycohort. Not independent confirmation or newsource.

For eachprimarycohort, INNER EXACT-minus-POS musthave>=100transitions on>=10leaves,
mean>=.01nat/transition AND >=2/3leavesstrictlypositive. Bothpass =>
INNER_EXACT_TRANSFER; insufficientcapacity=>CAPACITY_STOP;elseNO_JOINT_INNER_TRANSFER.
Onlyifthisprimarypasses, INNER EXACT-minus-BIT passingthesamegatesinBOTHcohorts
supports the additional label EXACT_IDENTITY_ADDS_PREDICTIVE_VALUE. Otherwise
that additional claim is NOT_ESTABLISHED. No favorablecohortreplacement.
Report BIT-minus-POS and allEDGEcomparisons diagnostically. Edge/interiormean
differenceisnotacausaldecomposition orfractionofexplainedcontent. No pvalues.

## Checks and limits
Toytablesverify normalization,unseenuniformity,correctsourceholdout andknown
conditionalcounts. Independentvalidatorimportsno runner, reconstructs allthree
trainingtables, everyheldsourceevent/logprobability, exclusions, novelty, leaf
aggregation andfixeddecisions. No changesafterheldresults. A positive supplies
formalprediction, notlettersounds,phonotactics,morphemes,wordmeanings,anactual
writingalgorithmor decodingkey. Earlierreportsretain theiroriginaldecisions.
