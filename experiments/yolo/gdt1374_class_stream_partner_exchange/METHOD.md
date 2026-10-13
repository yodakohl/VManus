# GDT1374 — Conditional pairing of two complete class streams

## Decision note

IDEA1049, nominated by the four-agent positive-evidence review, tests the dual
of1265: masks stay fixed while partners between whole ordered class streams
change.1279shows exact inner-unit predictive information but doesnot establish
this conditionalpairing result.1246literalhalf repeat,1285secondunit estimator,
1372fusionmemory capacity and1373wholecachefailure remain unchanged.

Unknown: do original stream pairings have higher frozen cross-class inner scores
than conditionalindependent pairing with the same stream inventories, masks and
outerunits? Positive requires coupled selection underthisscope; nonconfirmation
is not independenceproof; inadequatecapacity stops. Budget40minutes including
review, implementation, independentvalidation andpublication. No maskcoarsening,
unitrelabeling, endpointremoval, score/modelrefit or newsource afteroutcome.

## Data and conditional model

Use old1233strictcache,631allowlist,1264TRAINlabels and1279MODEL/EVENTS. Evenleaf
n>=4words only, allunits must have afrozenbinarylabel. Report excludedunclassified
words (mhasnofrozenlabel), never addalabel. Rejoin1279eventIDs, n,Currier andeach
previous/nextpair tothecachedwords. No rawquery,image,corpus orreserveaccess.

For eachword retain fullbinarymask and ordered subsequences S0,S1. Pool byexact
page,Currier,fullmask,firstunit,lastunit. These endpointconstraints factorize
because the mask fixeswhichstreamowns eachendpoint. The NULLis exchangeable
independent selection of S0 andS1 WITHINthese pools, equivalentlyuniformpartner
assignment conditionalon bothobservedstreambags. Arbitraryword-position-specific
stream laws are NOTincluded; conditioningdoesnot proveexchangeability.

Permute entireS1streams among S0carriers. Everywhole stream, withinstreamorder,
aggregate unitcounts at eachWORD-INTERNALordinal across thepool remain preserved,
as do eachword length,mask andouterunits.
Createdwholeforms neednot have beenattested. Wholewordfrequencies andcrossclass
pairings neednot bepreserved. Native classes are working labels, not vowels or
phonemes. No claim ofactualdeinterleaving orsourceword meaning.

## Score, exact expectation and mobility

Score only targets i=2..n-2 (zero-based) where mask[i-1]!=mask[i], under frozen
1279EXACT logprobability (count+.5)/(contexttotal+11), conditionedCurrier,length,
i,previousunit. Otheredges are not scored. No outcome-based noveltycohort.
Words without suchanedge are excluded asNO_INNER_CROSS_EDGE.

For a pool ofNoccurrences, Cij is the sum of these logprobabilities after weaving
S0fromrowi withS1fromrowj. Observed score=sum_i Cii. Exactuniform-assignment mean
=sum_i mean_j Cij. Rows/donors retain occurrence multiplicities. A poolisMOBILE
iff some rectangle Cij+ C00-Ci0-C0j has absolutevalue>1e-12. Savefirstsuch i,j
inrow-major order; otherwise assignmenttotal isadditivelyconstant totolerance.
This is statistic-specific capacity, not a count ofindependent comparisons.

PRIMARYuses ALLmobilepools only. Denominatorperphysicalleaf is the numberof
strict-inner-crossedges acrossallwords in itsmobilepools; samefixeddenominator
for observed,exactmean andeverypermutation. Retain every suchleaf, including
zero/negativeexcess. Capacityrequires>=100edges in mobilepools on>=10leaves.
Materialeffectrequires equal-leaf observed-minus-exactmean>=.01nats/edge and
>=2/3primaryleavespositive. Also retain a DESCRIPTIVE mean overallscorablepools
andtheirleaves, withimmobilezeroexcess included, neverasareplacementgate.

Ifcapable,199uniformS1occurrence permutations, Random seed1374 resetperreader;
pools sorted by(page,Currier,mask,first,last), rows in originalcacheorder, skip
immobilepools; shuffle donorindexrange(N). Computeprimaryscoreexcess eachtime.
Upperp=(1+#null>=observed-1e-12)/200; requirep<=.05/3in additiontomaterialeffect.
Ifallnullsconstantwithin1e-12, NO_SCORE_MOBILITY instead. Per-readerstatuses
NO_CAPACITY,NO_SCORE_MOBILITY,NO_RETAINED_PARTNER_EXCESS or
CONDITIONAL_PARTNER_COUPLING. No readerpooling or independenceclaim.

## Artifacts

POOLS.json.gz reader->ordered pools:
{page,currier,mask:list,first,last,leaf,inner_indices:list,
rows:[{source:fullcachedrow,s0:list,s1:list}],costs:listoflists,
observed,expected,mobile:bool,rectangle:nullor{i,j,value}}.
Onlywords withcomplete labelsandcrossinneredges are pooled, singletonpoolskept.
RESULTstatus CLASS_STREAM_PARTNER_EXCHANGE; readers->{held_n4_words,
excluded_unclassified,excluded_no_cross,pooled_words,pools,mobile_pools,
mobile_words,mobile_edges,mobile_leaves,observed_mean,expected_mean,excess_mean,
positive_leaves,per_leaf:{leaf:{edges,observed,expected,excess}},
all_edges,all_leaves,all_excess_mean,null_excess:list,p_or_null,status}.
Null/capacitymeansnullwhereundefined. Allcomputationsandnegativecases retained.

Independentvalidator reconstructs streamswithseparatelabel-positionselection,
weaves words explicitly, checks allcostcells, sourceevents, exactexpectations,
rectanglecapacity, weights and199scores. Smallsourcefree controls enumerate
allassignment permutations toverifymeans/mobility andstream/mask/endpoint/marginal
preservation, plus additiveconstant matrices andlabel-swap symmetry.
Freezeprotocol, proof, programs, rawproposal andinputs before nativecalculations.
Positiveexcess concerns thisconditionalpairinglaw; hiddenline/topic/position or
otherwordselection canproducecoupling withoutthe proposedhumanwriter. No meaning,
sourcealphabet, natural-language proof, originalhand orhistoricalcausality.
f84/f84r,f116v,f1rbody,reserves andalllegacybody stops remain.
