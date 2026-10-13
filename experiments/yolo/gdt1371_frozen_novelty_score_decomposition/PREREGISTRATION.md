# GDT1371 — Frozen predictive logscore chain accounting

## Decision and contract

Read BIG_PICTURE_NEXT_DECISION_20261013.json in the existing production-origin
dossier. This is a small post-result accounting diagnostic of1308/1316frozen
models, motivated by1317's logicalcounterexample. No newmodel, sourcewriting
rule, training, heldsplit, mixtureweight, smoothing, cut or outcome gate.
Original1316NO_PRODUCTIVE_HALF_FORM_LEAD remains unchanged. Budget40minutes
including primaryreview, implementation, independentverification/publication.

Question: does the old raw-unseen loss reflect relative mass allocated to the
unseen category, conditional identity quality within it, or both? The answers
change which defect a future independently motivated writer would need to address.
A conditionalgain is neither newproductivePASS nor proof ofmidpointmorphology.
Do not automaticallyrepair mass, gate, source, split orweight afterthisdiagnostic.

## Exact task decomposition

Let Pbe the frozen1308M1 and Mthe frozen1316halfmixture. The conditioningcell
is suppliedCurrier and22working-unit wordlength. Scontains ALLgloballyTRAIN-seen
whole tuples ofthatlength, acrossCurrier, notjustthose seeninthecurrentcell.
Uis the complement in the full22^length universe. This matches oldglobal_unseen.
For eachcell, P(S)=sum_{w in S}P(w), P(U)=1-P(S); similarly for H andM.
M=(P+H)/2where a TRAINcell exists; absentcells useM=Pexactly, Hundefined.
No newwordtypes or extra alphabet filtering. Oldn>=4scope unchanged.

For eventw in category C (S orU), compute:
raw = log(M(w)/P(w)); category = log(M(C)/P(C));
conditional = log((M(w)/M(C))/(P(w)/P(C))).
Then raw=category+conditional eventwise and under identicalaveraging.
All probabilities remain normalized. ZERO-CATEGORY probability on an observed
event stops execution rather than droppingthatword; report any roundoffclamp.
Puses oldadditive0.5over22symbols, Huses the frozenmidpoint/seam tables.

Use ALLoldheldevents, and separately GLOBAL_UNSEEN/GLOBAL_KNOWN. Equal-leaf
means preserve oldweights within eachcohort; tokenmeans also retained. Report
allleafterms, notonlypositive orH-supportedunseenwords. ALLcategory term is a
proper binaryknown/unseen logscore difference. Negativecategoryterm onUNSEEN
alone doesNOTdemonstrate miscalibration: it maytradeoffagainst knownforms.
No statisticalsignificance, newthreshold or independentlyheldconfirmation.

## Inputs, calculation and artifacts

Inputs1308MODEL.json,1316MODEL_H.json/EVENTS.json.gz/RESULT.json plusoldreports.
No nativecachequery, text/image/sourcecorpus orf84/f84r/f116v/f1rbody/reserveaccess.
Check exactoldmodel probabilities for everyevent, unchangedglobalunseenlabels,
evenheldleaf IDs, oldcohortcounts andrawmeans. Do notrewriteoldartifacts.

CELLS.json: reader-> list(sortedcell) of {cell:[currier,length],train_cell:bool,
seen_types,p_seen,p_unseen,h_seen,h_unseen,m_seen,m_unseen}; absentHvaluesnull.
SCORES.json.gz (mtime0): originaleventorder list {id,reader,leaf,cell,unseen,
raw_gain,category_gain,conditional_gain}.
RESULTstatus FROZEN_NOVELTY_SCORE_ACCOUNTING; readers->{ALL/GLOBAL_UNSEEN/
GLOBAL_KNOWN:{words,leaves,raw_equal_leaf,category_equal_leaf,
conditional_equal_leaf,raw_token,category_token,conditional_token,
per_leaf:{leaf:{words,raw,category,conditional}}}}.
No winner orpassedscientificgate field. Roundoffmetadata top-levelclampslist.

Primary floatingprobabilityproducts/math.fsum. Independentvalidator reconstructs
Hfrom oldTRAINwholecounts (notprimaryorMODEL_H), uses rationalM1probabilities
for seen-mass totals, checks allcells/events/aggregates within1e-10andchainrule.
Controlfixture: finitecategorymodel withknowntradeoff where rawUNSEENnegative
butconditionalpositive; demonstrate fullBernoulliscoring separately. Freeze
protocol, bothprograms, proofreview andinputs before newmasscalculation.

This does not reopen1316. The existing no-retuning and conditionalreview gates
remain; a diagnostic is not a new independentlyspecified writingconstruction.
1333alsoqualifies1320: no requiredwholewordmemory followsfrom that oldpositive.
The big-picture aim is to distinguish useful predictions from formalcoverage,
without erasing failedcriteria or turning logicalpossibility into translation.
