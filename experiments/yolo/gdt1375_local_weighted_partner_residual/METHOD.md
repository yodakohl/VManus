# GDT1375 — Whole-form preference beyond a fixed local partner law

## Decision note

1374rejects uniform independentpairing but its scoreislocal. Newquestion: does
frozen1308MIX_Q predict the actualpartnerassignment betterthan frozen1308M1,
AFTERconditioningon1374streambags/mask/page/Currier/exactends? This isnotanother
uniform-null score, newmodel fit orproofagainst alllocalmechanisms.1308already
showedunconditionalwholeformgain; the newconditionalmargins change thequestion.
1280's fixed-per-word-bigram capacitystop and1374's originalpositive remain.

Smallestboundedcalculation: retain1374MOBILEpools with2<=N<=8, making complete
assignmentenumeration at most40320perpool. Larger poolsareexplicitcomputational
exclusions, never silentlycollapsed orrepaired. Budget40minutes includingreviews,
sourcefreecontrols, implementation, independentverification andpublication.
If residualcapacityfails, STOP. IfconditionalMIXgainfails, no retainedwholeform
increment inthissubset, not local-sufficiencyproof. Ifitpasses, retain additional
fixedwholeformpredictive preference, not lexicon, longrangegrammar ormeaning.
No alternateNcap, statistic, smoothing, mixture orsource afteroutcome.

## Frozen models and cancellation

P(w)=1308M1; M(w)=1308MIX_Q=(P+Q)/2 for nonemptyTRAINcells, elseP. Q is theold
TRAINwholeformfrequency in(Currier,length). Use oldtables, no refitting. Verify
1279EXACT and1308M1noninitialcontextcounts agree for each evaluated classified
context. Within a1374pool, all sameclass factors, firstunit factors andalso
crossclass WORD-EDGE factors contribute row/column terms only, because exactends
andmask are fixed. Hence exp(1374INNERmatrix) and productofFULLPwords give the
SAMEconditionalassignment law. Verify thiscancellation numerically; no omission
of a localedgeconstraint is alleged.

For each eligiblepool weave all S0_i/S1_jwords, compute logPij andlogMij. For
assignmentpi, Lp(pi)=sum_i logPi,pi(i), Lm(pi)=sum_i logMi,pi(i).
Zp=sum_pi exp(Lp), Zm=sum_pi exp(Lm). Enumerate everylabeledoccurrence permutation
in itertools.permutations(range(N))order; duplicates retain correctmultiplicity.
Use rowmax-scaledweights orstablelogsumexp; reject numericalunderflow ratherthan
ignore nonfinite terms. Observedassignment isidentity. The ONLYprimaryscore is
R(pi)=Lm(pi)-Lp(pi)-(logZm-logZp), a normalizedconditional loglikelihoodratio.

Conditionalreference draws pi withprobabilityexp(Lp(pi))/Zp. This is a product
local-word law conditionedon observedstreaminventories, not allfirstorderwriters
or independently established physicalhistory. Unmodeledpage/topic/position
heterogeneity andselection remain alternatives.

## Capacity, aggregation and null samples

Tij=logMij-logPij. Residual-MOBILE iff some anchored2x2Trectangle hasabsvalue>1e-12.
This isnewscoremobility, not inheritedCmobility. Savefirstrectangle ornull.
PRIMARYuses ALLresidual-mobile computablepools; everyinformativeleaf included.
Perleafscore=sum_pool Robserved / totalwords in itsprimarypools; equalleafmean.
Capacity>=100words and>=10leaves. Material>=.01nats/word and>=2/3leavespositive.
No selectedHpositive/unseen subset, no newlanguage or wordmeanings.

Ifcapable,199globalconditionaldraws fromthe exactfinitePassignment law. Seed1375
separatelyperreader; primarypools inoriginal1374order. For eachpool drawONEuniform
random variate and invert its lexicographic assignmentCDF. RecomputesampledR;
leafdenominators unchanged. Upperp=(1+#null>=observed-1e-12)/200. Requirep<=.05/3
ANDmaterialgate. Ifdrawmeans constantwithin1e-12, NO_SCORE_MOBILITY. Outcomes
NO_CAPACITY,NO_SCORE_MOBILITY,NO_RETAINED_CONDITIONAL_WHOLE_GAIN or
CONDITIONAL_WHOLE_FORM_INCREMENT. No readerpooling/replicationclaim.

Also retain allcomputablepool conditionalgain as descriptive, withimmobile
zero-gain cases. OriginalALL1374 result isnot retrospectivelyrescored/replaced.
Record exactweightednull mean ofR perpool (must<=0withinroundoff) as a KLcontrol.
Finiteprobability enumeration is numericalstable arithmetic, not exactrationals.

## Artifacts and validation

POOLS.json.gz reader->list oneentry for EVERY1374mobilepool:
{original_pool_index,N,leaf,status} forN>8(statusCOMPUTATION_CAP), otherwise
{original_pool_index,N,leaf,status:COMPUTABLE,logP,logM,logZP,logZM,
observed_R,null_mean_R,mobile,rectangle:nullor{i,j,value}}.
No fullfactorial permutationlist needbesaved; protocol regeneratesit.
RESULTstatus LOCAL_WEIGHTED_PARTNER_RESIDUAL; readers->{original_mobile_pools,
excluded_large_pools,computable_pools,residual_mobile_pools,primary_words,
primary_leaves,positive_leaves,mean_gain,per_leaf:{leaf:{words,gain}},
all_computable_words,all_computable_leaves,all_computable_mean_gain,
null_scores:list,p_or_null,status}. Meansnullifundefined; null[]ifnocapacity.

PrimaryenumeratesN!assignments. Independentvalidator uses subsetDP partition
functions/moments andlexicographic prefix-block sampling fromthe sameuniform
variate, notprimaryimports. Reweave allwords, validateoldtables, cancellation,
allmatrixentries, normalizers, scores, exclusions and199draws. Smallcomplete
permutationfixtures compareDPwithenumeration, includingduplicates, identical
conditionalmodels, knownnonnullscore, andedgefactorcancellation. Freezeboth
programs, proofreview, priorpackets/models andprotocol before newnativeweights.

No new rawTSV, image, corpus, f84/f84r,f116v,f1rbody,legacybody orreserve. Source
inputsareold1374POOLS,1308MODEL,1279MODEL andselectedproposal/primaries. Allnative
materialalreadyexposed; no freshconfirmation claim. Numericalmobilitytolerance
is operational, not exactsymbolicconstancy. No automatic largerpermanent solver.
