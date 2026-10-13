# GDT1369 — Open-edge consistency of two-group representative partitions

## Decision note

1368proved triple-window minimum4but did not test simultaneous partition of
longer consecutive runs. It supplied no actual sourceword boundaries. We retain
that absence explicitly: allow one group at either runedge to belong to an
unknown external sourceword. This is a stronger necessary relaxation, not new
framing evidence, repair of a failure or a whole-source reconstruction.
Question: do any global K4/K5representative sets survive this consistency test?
If none atK5, reject theB2/K5conjunction on the retainedruns. If some survive,
retain only structural non-exclusion, with explicit local witnesspartitions.
Smallest adequate test screens the alreadyretained triplewindows then checks
only surviving sets on their maximalruns. Budget25minutes inclusive of review,
implementation, independentvalidation andpublication. No sourcefit, all-code
search, largerB, guessed lineboundary or newcorpus afterward.

## Scope and rule

Use only1368WINDOWS.json.gz andRESULT. Reconstruct unique fullsource rows per
reader byID, requiring repeated copies identical. Group by(page,locus); sort
integer source_group_index and split at gaps. Keep maximalruns oflength>=3.
Re-enumerate every overlapping triple and require exactequality/order with1368
windows. Thus no addedgroups, hiddenjoins, crossline links or newnativeaccess.
Retain originalallowlist andrawparse/ID/seamchecks. Preserve allreadersseparately.

For a fixed representative set H, eachgroup is hit iff its RAW_CHARsupport
intersectsH. Seek disjoint blocks of1or2groups covering the entire run except
optional one leading and one trailing group. Every completeblock must have at
leastonehit. Omitted edgegroups stand for possible proper fragments whose hit
couldlie outside theobservedrun. They are NOTdeleted or asserted actualpartials.
No internal group can be skipped. Boundaries betweenruns remain unconstrained;
independently feasible localpartitions need not coexist in one real fullsource.

A trueB2sourcewordpartition necessarily restricts to such a runpartition: only
one leading andone trailing sourceword can cross theedges, each consumingatmost
one insidegroup. Conversely the localhitpartition establishes only existence
under this generous representative model, not completecarrierparses/language.
Unknownoutsidegroups may be granted arbitraryhits; no boundary is inferred.
Triplecoverage is necessary but potentiallyweaker than this localpartitionrule.

## Enumeration and artifacts

Alphabet is1368FULLrawalphabet. Enumerate all4- and5-element subsets in tuple
lexicographic order. Prefilter by hitting every1368triple. For each survivor
find the first failedrun under the open-edge partitionrule, ornull if allpass.
Retain ALLprefilter survivorrecords, notonly successful candidates. Old1368
lowercertificate excludes<=3; do notrepeat that census. No>=6search.

RUNS.json.gz (mtime0): reader -> listof {sources:[fullcachedrows]}, ordered by
(page,locus,startindex). RESULTstatus OPEN_EDGE_FRAGMENT_PARTITION; panels:
{runs,groups,windows,alphabet,by_k:{"4"/"5":{window_survivors,
partition_survivors,candidates:[{set:list,first_failed_run:int_or_null}]}},
minimum_or_null,canonical_hitset,canonical_partitions}.
Groups counts unique rows belonging to these runs (notFULLcachecount).
Canonicalhitset is firstlex atlowest survivingk; ifnone null andpartitionsnull.
A canonicalpartition perrun has {leading_external:0/1,trailing_external:0/1,
blocks:[[inclusive_start,exclusive_stop],...]}, indexingrunrowsfrom0. Pickfirst
feasible edgepair from(0,0),(0,1),(1,0),(1,1); withinthatspan dynamicprefix
reachability andbacktrackingprefer a finalsingleton whenpossible, elsepair.
This convention makes outputdeterministic; it is not historical segmentation.

Independentvalidator uses a different equivalent characterization (e.g.matching
unhitgroups to adjacenthitgroups with one useperhit, includingexternalends) or
independent exhaustiveblockstate search. Compareallcandidate decisions/firstfail
indices and validate everyupperpartition. Sourcefree controls exhaust binary
hitpatterns to length12and compare with enumerated1/2block partitions under
four edgeoptions; retain a triplecover-but-partitionfail example ifitexists.
Do notclaim a stronger condition withoutsucha counterexample/proof.

Hash-lockprotocol, proofreview, bothprograms,1368method/results/windows/validation,
631allowlist and1046RAWbefore nativeanalysis. Knownexposure is notholdout.
No realvowels,phonemes,wordmeanings,sourcewordidentities or independentreader
replications. No new rawTSV, image, sourcecorpus, reserve, f84/f84r,f116v,f1rbody.
The oldmissing-binding blocker persists; noreopeningapproval claimed.
