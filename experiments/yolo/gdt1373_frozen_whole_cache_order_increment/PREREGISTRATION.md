# GDT1373 — Fixed whole-form cache increment beyond a frozen strong baseline

## Decision note and predecessor distinction

Question: does recent exactwholeform context add to frozen1316probabilities,
and does the observed order provide more gain than the same localword inventories?
This is a one-shot normalized predictivecomponent test, not a newdecodedwriter.
GDT001exact-copy MRUcodec alreadyfailed description-length comparisons: preserve
that result; no newMRUwindow/minlength/code search. IL005uses formconditioned
ROOTrecency to previousLINES, resettingparagraphs. Its code and registryclosure
were inspected, but its resultreport is unavailable in thischeckout; do notclaim
an independentlyverified numericreplication.1170doublet outercontext and1153strict
prior-continuation rules answerdifferentquestions. No fixedfailure is repaired.

Newfalsifier: a fixed recentwholeform distribution must improve the original
completeheldcohort beyond frozen1316AND exceed same-run/length wholeinventory
permutations. A gain without conditionalexcess is NOT proof that localinventory
suffices; only no demonstrated order-specific excess under this reference.
Failure stops thisfixed component. Success retains limitedorder-sensitive
prediction, not copying, memory, language ormeaning. Budget40minutes inclusive
ofpriorreview, implementation, independentvalidation andpublication. No tuning
ofhorizon,weight,base,shuffle cells or source afteroutcome.

## Fixed predictor

P(w) is the unchanged1316mix_h for suppliedCurrier and22unitlength. History is
at mostthepreviousFOUR original strictgroups in the same maximalconsecutive
page+locus run, endingatany missingindex. Retain ALLgroups asdistance steps,
including shorter ones. C(w) is empiricalfrequency amongthose historygroups
with thesameunitlength as target. If none, usePexactly. Otherwise
M(w)=(7/8)P(w)+(1/8)C(w). Both normalized overall22^length forms conditionalon
history/Currier/length. No current/futureword entershistory. No symbol, unit,
length or unknownspelling is removed. Fixed1/8weight is a declaredprobe choice,
not an inferred scribalparameter. No codebookcost or fullsourceencoder claimed.

Score ALLoriginal1316heldevents inoriginalorder; retain zero-gainfallbacks.
Reconstruct runs from1233FULLstrictcache, includinglength1/2runs andshortgroups.
AllsourceIDs,allowlist,rawunits,Pkind,definiteseams andconsecutiveindices checked.
No groupacrossgap,line,page included. Evenleafonlymatchesoldheldevents; for each
heldgroup oflength>=4 require exactlyone oldevent with identicalunits/leaf.
Currier is constant amongscorablegroups ofa run. No newnativeadmission.

Gain=log(M/P), meanwithinphysicalleaf thenequal acrossALLoldheldleaves. Retain
per-event probabilities/cachecounts, per-leafgains andtotalmean. Capacityrequires
>=100cacheavailableheldtargets spanning>=10physicalleaves. Materialgainrequires
mean>=.01nats and>=2/3ALLheldleavespositive. No specialnewword/successfulrepeat
subset is selected or scored asan alternateprimary.

## Conditional order reference

For eachreader separately, permute completeword tuples within eachfixed
(run,length) pool ofscorableheldslots. Everypoolhasone Currier, andallslots
belongtotheoldheldcohort. Shortgroups stayfixed; theyaffectdistance butcannot
matcha>=4target's length. This preserves theexactrunwholeinventory,lengthsequence,
sourcegaps,page,leaf,Currier andSUMbaseline logprobability. It doesnotpreserve
allbigramcounts anddoesnot testorderbeyondallpairdependencies.

Use199permutations, PythonRandom seed1373 resetseparatelyperreader, pools sorted
by(runindex,length), indicesinsourceorder; shuffle occurrencewordindices evenif
valuesrepeat. Recomputeentirecache andallprobabilities aftereachshuffle. A moved
word carries its unchangedPprobability for thatCurrier/length, not its oldgain.
Checkbaseline logsum invariance. Nullmeans useoriginalALLleafdenominators.
Ifcapacitypasses butallnullscoresareequal within1e-12, stopNO_SCORE_MOBILITY.
Otherwise p=(1+#nullmean>=observedmean)/200. Requirep<=.05/3ANDmaterialgain in
each separatelyreportedcase. No readerpooling or independentreplication claim.
Useorder-increment designation onlyif allrequirements met; retainactualresult
andnullrange evenwhenfailed. This is a conditionalwithin-run exchangeability
reference, not proof of a truebaseline generative model or search-wide significance.

## Output schema and validation

SCORES.json.gz original1316eventorder:
{id,reader,leaf,cache_size,cache_hits,base_probability,new_probability,gain}.
RESULTstatus FROZEN_WHOLE_CACHE_ORDER_INCREMENT; readers->{words,leaves,
cache_available,cache_leaves,positive_leaves,equal_leaf_gain,token_gain,
per_leaf:{leaf:{words,gain}},null_scores:list,p_or_null,status}.
statusNO_CAPACITY,NO_SCORE_MOBILITY,NO_RETAINED_CACHE_GAIN,
GAIN_WITHOUT_DEMONSTRATED_ORDER_EXCESS orORDER_SENSITIVE_PREDICTIVE_INCREMENT.
No assertion thatwordrecencyisanuntriedgeneralmechanism; narrowcomparisononly.

Independentvalidator uses separate fullrollingfrequency reconstruction and
checks sourcecohort, everyobservedevent, all199nullscores anddecisions. It may
share declaredPRNG/seed forreproduction, neverprimarycode. Sourcefreecontrols
verify normalization, emptycachefallback, nonfuturehistory, gapreset, length
conditioning andbag-preservedbaseline butchangedcachegain. Protocol, programs,
proofreview andallinputs arelocked before newprediction orpermutation scores.
No rawTSV,images,sourcecorpus,reserve,f84/f84r,f116v,f1rbody or legacybody rerun.
