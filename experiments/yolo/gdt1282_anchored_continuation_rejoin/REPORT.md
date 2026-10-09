# GDT1282: no later literal rejoin after the fixed thirteen contexts

**NO_LITERAL_REJOIN_IN_FIXED_13.** The unchanged13ZLcontexts from926 have
assessable divergent sites in both ZL andIT. None of those pairs later rejoins
an eligible identical sequence of at least3wholewords inside its two original
completeparagraphs. RFhas no nativeparagraphbounds and remains untestable.
This is a fixed literal-context census, not a rejection of paraphrase, shared
content, grammar or all possible reconnection rules.

| Reading | Fixed contextpairs | Bothsites assessable/divergent | Pairs withrejoin | Ready sites with excludedtaillines | Immediatelyparagraph-final firstdivergence |
|---|---:|---:|---:|---:|---:|
| ZL3b |13|13|0|18/26|1/26|
| IT2a |13|13|0|0/26|1/26|
| RF1b |13|0|unscorable|notassessable|notassessable|

ITprovides fullyeligible continuationlines for all26sites. ZLretains18tails with
lines excluded by the inherited literal/definiteseam policy. Therefore its zero
cannot be read as absence of a match in uncertaintext. No unknowngroup or source
annotation was erased. Readers are alternate transcriptions of one manuscript.
The26ZL/ITpairentries are not26independent physicalcomparisons.

## Why this was a different question from928
928requires two disjoint MAXIMALmatches. The newquery fixes a known common opening,
requires distinctfollowinggroups, and searches strictlyafter those groups without
extending a later match backwards across that opening. Both branches mustcontain
atleastonegroup beforethejoin. Anchorlength remains3andneeds>=2distinctforms.

A source-free counterexample demonstrates non-subsumption, witheachletteraword:

- P: `a b c x d e f`
- Q: `a b c y a b c x d e f`

The fixedopeningabc divergesx/y and thenrejoinsdef. In928thelatermatch grows
backwards toentireP againstQ's latercopy, overlappingP's openingmatch. Its
registered disjointmaximal criterion is false, while the newanchored criterion
is true. The original928function was run unchanged onthisfixtureanddoesreturn
thatresult. This is not a discovered928bug or a new nativeexample; it justifies
checking a genuinely different consequence without shortening oldanchors.

## Scope actually examined
Eachold926seed keepsitsoriginaltwo(page,locus)locations. Eachreader mustsupply
theexactinitialanchoruniquely inits928eligibleline andacompleteoriginalparagraph.
Alternate-readerindicesmaydiffer;actualsourceIDs/wordsarepreserved. No replacement
site, extrainitialcontext, projectedRFboundary or repairedspelling was introduced.
Thefirstdivergentwordmustdifferbetweenthe two actualreader-specificsites.

Everylater candidateis3consecutivewords entirelywithinaneligiblephysicalline.
No cross-linejoin, shorteranchor, backwardextension or jump pastparagraphend.
All qualifyingpositionpairs wouldhavebeenretained, including repeatedopening
contexts andoverlappingtrigrams. Noneoccurred. The original13seeds maythemselves
share/nestsourcepositions; no independenceorsemanticOR/IFstructure is inferred.

Completeparagraphs andbothrawcontinuationsarestored inPARAGRAPHS.jsonandCASES.json.
For illustration, old `daiin cthor chol` is followed bychoratf15v.12,which ends
itsparagraph, butbyykchoratf19r.10,which has12additionalgroups afterthatfirst
branchwordbeforeparagraphend. Thatknownclosurecontrastwasalreadydiscussedin927;
thisexperimentdoesnotrediscover a meaningforchor or anyclosureword.
Theother25ZLfirstdivergentgroup sitesalsohaveatleastonefurtherparagraphgroup.
Theycannotallbeexplainedsimplyasthatfirstgroupendingtheparagraph; thisdoesnot
identify thekindofrelationbetween theircontents.

## Verification and limits
Six source-free controls check rejoining, absence, forbiddenzero-lengthbranches,
line-boundaryexclusion, repeatedopeningasrightanchor andtheactual928maximization
counterexample. Protocolandprograms were locked before nativecomparison.
An independent implementation imports no newrunner: it directly comparesalllater
positions, verifiesselectedfullparagraphs againstthe six915rawcaches, checks
lineeligibility,sourceIDs,offsets,boundaryflags,complete tails and everydecision.
39context/readerpairs,52readysites and44distinctselectedparagraphschecked;PASS.
This validates accountingandthefixedliteralpredicate,notindependentpalaeography.
All data were alreadyproject-exposed; no newreserve or confirmation split.

## Decision
Park this particular anchoredrejoin test. Do not now shorten3words to2, extend
pastparagraphends, poolreaders or normalizeunknowns to manufacture a positive.
926's lackofreplicatedbranches,927's scopedclosurefindings,928's maximal-anchor
result and1153's failedstrictprior-choice rule all remain unchanged. IDEA196is
now assessed for this explicit13seedcontract, not universally exhausted.
No source language, statementidentity, semanticbranch, wordmeaning or decoder
was selected. No newimage, sealeddata, f116v, GDT388edge or publicpush. Localonly.
