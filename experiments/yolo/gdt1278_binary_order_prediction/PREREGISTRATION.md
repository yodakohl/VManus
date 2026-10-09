# GDT1278: compact conditional order prediction

## Decision before fitting
1264's fixed binary partition gives extra class switches;1265retains an effect
in a restricted jointly inventory/position-preserving paired reference.1266's
far-neighbor extension lacks capacity and is not repaired. Earlier full-symbol
Markov models already predicted held within-word transitions beyond position:
this experiment is NOT discovery of local word structure.
Unknown: does one train-fitted positive switch preference provide a useful compact
predictive component on new interiors beyond a fixed five-bin position model,
when every scored candidate order has the observed class inventory? A positive
would retain this explicit probability rule as a construction constraint; a
negative parks THIS compact predictive component without erasing1264/65.
Neither outcome supplies a content encoder, nextword prediction or meaning.
Smallest test: five frozen position log-odds plus one finite-grid coefficient,
exact binary-sequence normalization by short DP; no new classes, pair matching,
source corpora, high-dimensional learner or full decoder. All decisions below
are fixed before new parameter fitting or held scoring. Earlier project exposure
means this is exploratory predictive transfer, not untouched confirmation.
Inclusive conservative outer budget14:24--15:04UTC8October2026, including prior
review, implementation, controls, independent validation and local closure.
No expansion, optimizer repair or beta-range extension at a failure/deadline.

## Source, split and labels
Unchanged1233GROUPS cache; original1264TRAIN labels fixed, including unclassifiedm.
Remove exactly first/last working unit; interiors shorter than3 unscorable.
TRAIN=ZL3b oddphysicalleaf numbers; TEST=evenphysicalleaf numbers. Freeze one
ZLposition/beta model and apply it unchanged to all3readings; readers sensitivity
only. For each reader novelty means its own exact trimmed interior is absent
from its odd-leaf interior inventory(length>=3). ALL and UNSEEN_INTERIOR primary
ZLcohorts. UNSEEN_WHOLE descriptive only. No FARcohort extension or rematching.
Unknown units and short groups counted explicitly, not mapped or repaired.
Existing179selector scope, f84/f84rsealed, f116vunadmitted, reservesclosed.

## Two fully specified probability models
For binary interior x of length n with k ones, candidate space is ALLbinarystrings
of that n and k. This does not predict n,k,unitidentities,wordboundaries or content.
The bin of positioni(0-based) is floor(5*i/n), exactlyfivebins without retraining
boundaries. From allscorableZLTRAINinteriors countones andzeros ineachbin, andset
 theta_b=ln((ones_b+1)/(zeros_b+1)).
These are a fixed smoothed marginal training baseline, not fitted conditional
maximum-likelihood positional parameters or a guarantee to remove every possible
position effect. Detailed length-specific positional models are not tested.
 P_beta(x|n,k)=exp(sum(theta_bin(i)*x_i)+beta*S(x))/Z_beta(n,k),
where S is adjacent switch count and Z sums the entire stated candidate space.
Baseline is beta0. Fixed candidategrid[0,.25,.5,1,2]; select highest TOTALtraining
conditional loglikelihood; tieswithin1e-10choose smallerbeta. No negativebeta,
extra grid point, folio hyperparameter fit, newclass or held-out optimization.
A forward DP(lastbit,onescount) exactly sums every binary order in logspace.
Each beta produces probabilities, not merely an unnormalized switch score.
Freeze MODEL.json andhashlock before invoking evaluation. Protocol andbothprograms
are source-locked beforetraining;controls must pass first.

## Scoring and outcomes
For every scorableheldgroup save logP_beta-logP_0 in natural-log units and divide
by interiorlength n. Perleaf score is mean of these pergroup normalized gains;
primary mean weights physicalleaves equally. Report eventmean too, notanewgate.
ALL and UNSEEN_INTERIOR eachrequire>=100groups on>=10physicalleaves. Eachpasses
only if mean>=.01nat/interiorunit AND >=2/3ofscorableleavesstrictlypositive.
PASS_BOTH requiresbothprimarycohorts; otherwise CAPACITY_STOP or
NO_JOINT_MATERIAL_PREDICTION. Alternative readers do not rescue primaryfailure.
Report selectedbeta,fullTRAINgrid,fitparameters,allcohortdenominators,negative
leaves,unitunknowns and pergroup/perleaf scores. No significance/pvalue or fraction
of manuscript content explained. beta=0 leadsidenticalmodels,notfreshpositive.

## Validation and limits
Smallbinaryorders n3..8 underuniform andnonuniformtheta exhaustivelycheckforward
normalization,probabilitysum1 andbeta0identity. Independentvalidator imports no
runner: reconstructtrainingcounts,uses backward recursive positive-weight sums,
checksfullgrid/modelselection and every heldprediction/aggregation against source.
A useful component may describe phonotactics, graphotactics, conventional spelling,
lexical families or a cipher. No vowel/consonant designation, actualpenroutine,
causalmechanism, grammar or completeness follows. The exactsymbol-bag comparator
is represented only at CLASSlevel: unitidentitywithinclass is not predicted.
Positivepredictionwould not settle1266distancecapacity or eliminate alltemplates.

UNSEEN_INTERIOR is an outcome-defined diagnostic subset of exact unit strings.
Both models remain normalized over ALLbinaryordersofn,k, not renormalizedon
novelty. Testsubset membership never fitsparameters or chooses thegrid.
