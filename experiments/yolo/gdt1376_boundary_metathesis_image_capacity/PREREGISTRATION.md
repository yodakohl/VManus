# GDT1376 — Exact local image capacity of a boundary metathesis rule

## Decision note

IDEA1048 is a new once-simultaneous boundary A|B→B|A transducer, A!=B. Existing
reviews distinguish it from internalneutralization, fieldexchange, wordweaving
andgapshifting. No sourcewordmeaning orhistoricalpractice isclaimed. A new linear
image lemma permits a stronger test thanonly nonsingletonforbiddenboundaries,
without exponential source enumeration or a decoder-fitting project.

Unknown: which ofall462ordered22-unit keys admit every retained openrun as an
output? Any impossible run refutes that fixedkey underdeclaredunits/grouping.
Survival means localpossiblepreimages, notoneglobalplaintext/language/keyproof.
Budget35minutes inclusive ofproof/selection, implementation, independentcontrols,
validation andpublication. No keyselectedbyactivity, no sourcecorpusfit, multiple
rules, repeatpasses ormeaning guesses afteroutcome. Interiors remain unchanged;
thisedgewriter doesnot itself generate1374strictinnersequences.

## Writer and exact image lemma

Mark ORIGINALsourceABboundaries andswaptheir endpoints simultaneously once.
Theycannotshare a unit becauseoverlapwouldrequire a singleton tobeAandB. The
same holds forvisibleBAcandidate reversals. Every true source swap leaves a
visibleBA, so inversecandidates reverse subsetsofvisibleBAthenforwardcheck.

At a non-BAoutput seam, those reverse swaps can onlychange leftA→B througha
singletonleftword orrightB→A througha singletonrightword. Theycan destroy anAB
obligation butcannotcreate a newone. Thus a CLOSEDoutput has a preimage iff each
ABseam has at leastone neighboring BAseam connectedthroughthesingleton inbetween.
Allconstraints arepositiveORs. Reversing ALLvisibleBA simultaneously gives a
canonicalpreimage wheneveranypreimageexists. This doesnot enumerateallpreimages.

For an OPENretainedrun, use artificialOUTPUTpadding BB ontheleft, AA ontheright,
each a2unitword. PaddingintroducesnoABobligation andgrants exactlythepossible
outside rescue of a firstsingletonA/lastsingletonB. Closedmembershipofthispadded
run is equivalentto someoutsideextension underthisformalwriter. Different runs
mayneedincompatibleactualoutsidecontexts; localcapacity isNOTglobalfit. Padsare
notobservedwords andtheirBAseams areexcludedfromnativeopportunitycounts.

## Frozen native scope and tests

Reuse1233FULLstrictcache and631allowlist;22workingunits andall3readersseparate.
Buildmaximaloriginal-index-consecutive runs on eachpage+locus, includingonegroup
runs. Keepallwordlengths, including singletonunits; nojoining acrossgaps/lines.
Verifyedition/ID/parse/Pkind/definiteseams/allowlist andf84/f84r/f116v/f1r exclusions.
Runs orderedby(page,locus,startindex), rowsbyoriginalindex. No rawTSVornewimage.

For everyorderedA,B in sorted22alphabet, record allABboundaries, nonsingletonAB
violations, andunsupportedABboundaries under the openlemma. At boundaryi:
leftrescue iff len(left)==1 AND(i==0 OR previouswordendsB);
rightrescue iff len(right)==1 AND(i+2==runlength OR followingwordstartsA).
Only an observedA|B seam is checked. Unsupported iff neither rescueexists.
Every nonsingletonAB is unsupported, but singletonseams needtheir actualcontext.
Savefirst unsupportedwitness plusnumberofphysicalleaves withunsupportedseams.

Also count ALLobserved BAseams, singletonorotherwise, aspotentialreverse sites
only. BAcanoriginateunchanged; it doesnotprovea swap. Survivors withABcount0
permit anidentitysource on eachunextendedrun. SurvivorswithABcount>0 require
some change underTHATconditionalkey, but do notidentifythekeyasactual.
For eachsurvivor, canonicalreverse everyBAonpaddedrun andforwardvalidateexactly.
Retain digest of CANONICALINTERNALpreimage wordlists perrun, not inventedlexemes.

## Outputs and independent validation

RUNS.json.gz reader->[{sources:[fullcachedrows]}], mtime0.
RESULTstatus BOUNDARY_METATHESIS_IMAGE_CAPACITY; readers->{groups,runs,boundaries,
keys:[{A,B,ab_count,nonsingleton_ab,unsupported_ab,unsupported_leaves,
first_unsupported:nullor{run_index,boundary_index},ba_opportunities,status,
canonical_preimage_sha256:nullorhex}],excluded_keys,surviving_keys,
survivors_with_ba,survivors_requiring_change}.
status EXCLUDED orLOCAL_IMAGE_CAPACITY. Allcounts refer onlyoriginalinternalseams.
Keyorder alphabetlexAthenB, A!=B. Survivor digest: for eachrun in order,
json.dumps(internalpreimage,ensure_ascii=False,separators=(',',':'))+'\n', UTF8.
No preferredcandidate, translatedcontent orstatisticalsignificance.

Primaryuses the unsupportedseam lemma; independentvalidator uses directALLBA
inverse thenFORWARDcomposition on paddedruns tocheck eachkey. Separatelyverify
counts/firstwitnesses/digests andallsourcecontext. Sourcefree exhaustive small
wordstreams compare fullimagebyallsourceenumeration withlemma/canonicalinverse,
including singletoncreation andclosedversusopenpadding. Freezeprotocol, both
programs, proofreview, rawproposal,scope/cache andpriorreviews before census.
A deterministic existencewitness is not aunique reading. Allold source-specific
interior/length contradictions remain when their originalpremises stillapply;
wordwise≤2alias orper-wordbagbounds mustnotbe silentlyimported.
f84/f84r,f116v,f1rbody, reserves andalllegacybody boundaries remain closed.
