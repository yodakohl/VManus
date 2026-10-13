# GDT1372 — Capacity for a lexical-site persistence test

## Decision note

1047predicts serialdependence at a recurring complete sourceword/site.1371does
not supply evidence for that mechanism. Before scoring it, ask whether the
existing admitted packet contains enough genuinely variable, nonadjacent visits
under a fixed conditional contrast. Budget25minutes including review, code,
independent validation and publication. Only capacity, no persistence statistic,
permutation p-value, estimated retention or native memory claim in this pass.
If adequate, a later preregistration still needs physical-drift rival controls.
If inadequate, stop; no pooling pages, relaxing endpoints or changing keys.

1320/1333expand FOURligatures jointly; that changes1047's completewordkeys.
Instead use all eight separately fixed singlefusion bindings: chosenheight h
in k,t,p,f, C=cHh; expand onlythisC to (ch,h) forBH or(h,ch) forHB. Everyother
working22unit stays literal. Each binding therefore implements the declared
21sourceunits+1reservedoutputclass architecture, not the old18primitive model.
No binding is selected as true; eachreader/binding is a separate conditionalcase.

## Sequence scope

Use exactly1369RUNS.json.gz: maximaltrueconsecutive strictgroups on onepage+locus,
replaying against1368WINDOWS to verify identical scope. Missinggroups andlinebreaks
terminate runs; no observations across them are linked. Recheck631allowlist,
readers,IDs,originalindices,rawparse,Pkind anddefiniteseams. Allinterveninggroups
are present and decoded underthesameonefusionrule. No new corpus,image orreserve.
Monotone physicalgrouporder within a run is an explicit writing-order assumption,
not established chronology. Uniform reversal preserves the switch-capacity test.
No initialmemory0 is assumed at a cache/runstart. Histories are conditioned on
first/lastobservedchoice, absorbing unknownoutside states ratherthan resetting.

## Episodes and mobility

For eachcase, expand sourceword as above; find every disjoint chosenpair site.
An originalC giveschoice1; an original separatepair giveschoice0. Key is the
completeexpandedsourceword tuple AND zero-basedsourceposition, withinONErun.
All occurrences ofthissamekey are orderedby originalgroupindex. Retain anepisode
if it has>=2visits. Sameworddifferent sites remain separatekeys. Singlevisits
are counted but cannot be serial evidence. A remote transition joins consecutive
visits with at leastone intervening other sourceword (groupindexdifference>1).
Since allgroups are present, a skipped occurrence of thesame sourceword/site
cannot be hidden inside such aninterval underthisfixedliteralbinding.

Condition each episode on its endpoints and totalnumberoffusedchoices. OverALL
binaryarrangements oftheinterior withthatcount, calculateminimum andmaximum
numberofadjacent switches. MOBILEmeans max>min. n2/n3episodes cannot bemobile;
unequal drawings alone are insufficient. No observed switchcount is scored.
Static per-key Bernoulli weights cancel underthisconditioning;1047's fixed
retention.75would give relative pathweights proportionalto3^(-switches).
This distinguishes conditionalpathlaws, not lexicalmemory fromphysicaldrift.

A case has necessary CAPACITY_READY onlyif its MOBILEepisodes span>=10physical
leaves andcontain>=100remote transitions total. These are predeclared research
coverage gates, not a power guarantee. No pooling ofreaders/heights/orientations.
Allcases notmeetingboth are NO_CAPACITY. If nonepass, no nextscoringrun.
Even a readycase requires prospective different-key/physicaldistance controls
before any memory-specific inference. We do not measure driftcontrolcapacity here.

## Artifacts and validation

EPISODES.json.gz: case(reader_BH/HB_height)->ordered list ofepisodes:
{run_index,page,locus,source:list,position:int,visits:[{id,index,y}],
min_switches,max_switches,mobile:bool,remote_transitions:int}.
Orderbyrunindex, then lexicographicsource tuple, thenposition. visitsbyindex.
Only>=2visits saved. ReproductionusesoriginalRUNSforcompletecontext.
RESULTstatus LEXICAL_MEMORY_EPISODE_CAPACITY; cases->{runs,opportunities,
keys,singleton_keys,episodes,visits,mobile_episodes,mobile_visits,
mobile_remote_transitions,mobile_leaves,status}. keys=allunique(run,source,site)
with>=1visit; visits=sumlengths ofsavedepisodes. Mobileleavescountdistinctfnumber.

Primary uses a direct source expansion followedbytaggedsite recovery and a
binary dynamicprogram forswitch extrema. Independentvalidator must reconstruct
chosenfusionevents by a different traversal; compareallepisodes/counts/decisions.
Sourcefreecontrols include multiple sites, othercomplexunitsremainingliteral,
exactinverse, n2/n3immobility andendpoint-preservingmobile/immobileexamples;
exhaustbinaryhistories up tolength10for extrema against direct permutation.
Freezeprotocol/proof/programs/rawproposal/oldpackets/scope before episodecensus.
No new meaning, trueglyph, sourceword identity, historicalpractice or language.
No rawTSV,f84/f84r,f116v,f1rbody,reserveorimageaccess.1323differentanagram-choice
capacitystop and1333staticflankresults remain unchanged.

Beforeanyfuture nullscore, rendering-dependent linewrapping, transcription and
admission must also be addressed: fixedobservedrun conditioning is not itself
proof of choice-independent selection. This pass estimates no exchangeability
p-value and grants no scoring license from capacity alone.
