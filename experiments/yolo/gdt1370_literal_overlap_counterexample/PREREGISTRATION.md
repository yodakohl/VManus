# GDT1370 — A retrospective all-cut counterexample to literal overlap records

## Decision note

IP078 proposes a stream of overlapping two-piece records. Its unknownpiececut
previously prevented a selected positive test. Instead of selecting a cut, this
followup asks whether ANY nonemptycut can satisfy a known neighboring pair.
This is a retrospective deductive counterexample, not a blind discovery or
frequency census. IT2a qoteold/qokeol is already known from1368manualexamples.
Fix f100r.14 originalindicesG005/G006 for eachreader; retain actual alternates
orMISSING, never substitute another locus. Budget15minutes including protocol,
independent proof/validator, extraction andpublication. If overlap exists, only
compatibility; no keyfit. If absent, reject this universalrecordlaw on that
reader's fixedscope. No broad copy-writing or language ban.

## Literal model and all-cut falsifier

A source piece stream x0,x1,x2,... has fixed nonempty context-independent written
piece strings c(x). Emit consecutive visible records c(x0)c(x1), c(x1)c(x2),...
The record boundary is a written-output condition, NOTa claim of linguistic
wordhood. A record contains two nonempty pieces, allowing arbitrary lengths,
unknown identities and noninjective piece rendering. No markers, erasure,
contextual recoding, hidden reset at the tested seam or extra grouping are allowed.

For adjacent strings u,v in FORWARD orientation, c(x1) must be a nonemptyproper
suffix ofu AND a nonemptyproper prefix ofv. Enumerate every overlap length
1..min(len(u)-1,len(v)-1). REVERSED_RECORD orientation reverses eachentirerecord;
the corresponding condition on observedstrings is nonemptyproper prefix(u)=
suffix(v). Both are predeclared; arbitraryper-record direction is outside.
Absentoverlaps exclude allpossiblepiececuts in that orientation atthispair.
The condition is necessary and sufficient for this TWO-record localfactorization,
not for a globally consistent stream. Anyfixedalphabetrenaming preserves equality.

This avoids a favorable half-lengthchoice, not the need for a declared output
recordscope. Regionally applied overlap with thisseam declared a reset remains
outside the uniformscope; no suchreset is inferred. Splits mustalignRAW_CHAR;
this is notan identification ofphysicalglyphs. Empty sharedpieces would evade
the law andmakeits intended repeatedpiece obligation vacuous.

## Data and artifacts

Reuse1368WINDOWS.json.gz only. Select rows with exactpagef100r,locusf100r.14,
source_group_index5or6. All repeatedcopies mustagree; verifybothrows appear
together as consecutive sources inatleastoneoldwindow, exactIDs/readereditions,
Pkind, definiteleft/rightseams and631scope. Otherwise reportMISSING/unscorable,
notabsenceofoverlap. Allthree alternate readers retained separately.

RESULT status LITERAL_OVERLAP_COUNTEREXAMPLE; panels reader->{status, sources,
forward_overlaps,reversed_record_overlaps}. sources:[twofulloldrows] whenpresent,
otherwiseavailableorderedrows. overlaps lists [{length:int,piece:str}], ordered
bylength. status BOTH_ORIENTATIONS_EXCLUDED, ORIENTATION_SPECIFIC or
PAIR_COMPATIBLE; MISSING forinsufficientfixedscope. No aggregateindependenceclaim.

Primarychecks substrings bylength. Independentvalidator enumeratescomplete
three-piece factorizations bycuts in u/v (and separatelyreversedstrings), verifies
exactsourcecopies andallRESULTfields. Sourcefree controls overbinary strings
length1..4 cover unborderedpairs,validvariableoverlap and empty/proper exclusions.
Bothprograms, proofreview, protocol,oldpacket,allowlist,1368REPORT,883REPORT and
1359REPORT hashlocked beforethis smallreplay. NativeIToutcome alreadyknown and
explicitlynotpresentedasprospective evidence. No imageconfirmation.

## Prior distinction and ceiling

883 encodes overlapping sourceblocks as individual visiblecodes, imposing an
endpoint equalitygraph; here the overlapping piece is literally repeated as
part of adjacent GROUPS.1359omits a shared boundaryrun andtests sourceprofile
capacity, ratherthanliterallyduplicatingapiece. Neither is silentlyrerun.
IP078's general unboundscope/physicalunits remainlimits; only the explicit
uniform literalmodel is adjudicated. No wordmeaning, carrier, phoneme or
historicallyattested writer claimed. No rawTSV,newcorpus,reserve,f84/f84r,
f116v,f1rbody,OCRorimage access. No decoder or automatic exceptionsearch.

Registry reconsider(IP078,new_design) returned NO_REVIEWED_REOPENING_CONTRACT,
not an executionapproval. This is the first assessed retrospective all-cut
literal consequence, not a rerun of a failedIP078test. The old requirement to
motivate a confirming piececut is replaced here by checking ALLpossiblecuts;
source-recordscope andRAW_CHARalignment remain explicit conditionalpremises.
