# GDT1281: paid source-known allocation carrier

## Decision before implementation
RAW980contains a meaningful two-share module but leaves all physicalsymbols,
headers,namesandlayout unpaid. The questionhere is whether one explicitly paid
finite-alphabet realization can preserve complete sourceblocks, includingzero,
repeatedplansandheaderchanges, andretainitsannouncedindependenttotalcheck.
Success supplies a complete MODULEcodec for a declaredsource-domain, not a native
readingorfullmanuscriptwriter;failurestops this exactrealization. It resolves a
realdesigngap ratherthanrerunning unchangedmissing-native-binding audits.
Smallesttest: fixedserializer/reader, representativehandpackets and bounded
exhaustiveallocationcases; no nativecensus, statistics, image ortraining fit.
Budget15:22--16:02UTC8October2026 includespriorreview,design,implementation,
verificationandlocalclosure. No automatic prosegrammarorVoynichdecoderextension.

## Explicit new realization of RAW980
RAW980's worked core was the repeated batchidentifier. Here K is a SINGLEfixed
reference mark to the one batch explicitly named in the currentheader. This is
a declared new physical realization, not evidence that980's original K was such
a mark or that a native glyph has thismeaning. It changes the cost of thecore.
Sourceblock fields:LEFT,RIGHT,BATCH,UNIT,TOTAL,thenanorderednonemptylistof(a,b).
LEFTandRIGHTdistinctnonemptyidentifiers. All4identifiers use only uppercaseA-Z,
digits0-9,space,hyphen, withatleastonenonspacecharacter; preserve themexactly.
UNITdenotes an externally taught discretecountunit, not an inferredphysicalsize.
TOTALinteger0..9999; eacha,bnonnegativeintegersand a+b=TOTAL. The rows are
alternativeplans, NOTexecutedtransfers. Repeats retained. Noindividualitemidentity,
negativeamounts,hiddenremainder,conversion,thirdrecipientorconditionalprose.
A message is a nonemptyorderedlistofblocks. Everyblockhasatleastonerow.

## Alphabet, full framing and costs
Use15distinctsignslots within the existing22-working-unit repertoire. For a
fully renderable teachingcodec only, select the FIRST15units in the unchanged
1233inventory order. This is an arbitrary known-source teachingkey, NOT a guessed
Voynichkey or lexical/glyphmeaning claim. No manuscriptstring is decoded.
Slots0..6 are base7digits. Slots7..14 are H,F,G,A,T,K,Z,END respectively.
Literalcharacter order isABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789(space)(hyphen),
38entries. Characterindexj is encoded asdigit floor(j/7) thenj mod7. The other
11digitpairs are invalid. Literalpayloadusesonlyslots0..6, controls disjoint.
Thus namesmaycontainlettersnamedH/T/etc withoutcollision; nofreeescapechannel.
TOTALcanonicaldecimaldigits encoded bytheSAMEtable; noleadingzerosunless0.
Header=H encLEFT F encRIGHT F encBATCH F encUNIT F encTOTAL G.
Row=A T^a K T^b Z. Block=header,onerowormore,END. ENDclosesONEblockandclears
header; anyfollowingblockmuststartanewH. No implicitcarryafterEND.
ThebatchreferencemarkK hasmeaningonlyunderalreadydecodedvalidheader.

A headercosts 2*(fouridentifierlengths+decimalTOTALlength)+6units; ENDcosts1;
eachlogicalrowcostsTOTAL+3units. Nothing is free exceptvisualwhitespace, explicitly
notencodeddata. Canonicaldisplaywraps the encodedstream every24units; reader
ignoresASCIIspace/tab/CR/LF ANYWHERE beforeparsing. Hence nobreak/continuationtag
isrequired:linebreaksanddisplaygaps carry NO information. Sourcename spaces are
encodedwiththeliteral table. A physicalnativeword/line segmentation is NOT
assumed equivalent tothese logicalrows. Ifthatmappingwere laterproposed it would
needseparateevidence. All15selectedworkingunitnamesaresingleASCIIcharacters,
so this teachingrendering hasno lexerambiguity; no claimaboutactualhandwritten
atomization follows. Remaining7workingunitsunused,rejectedbythismoduledecoder.

## Fixed checks and falsifiers
Freezeprotocol/programs and sourcefixtures beforeexecute. Test representative
multi-blockpacketwithuppercase/digit/space/hyphen names,N4/N0/N6,allzeroand
positiveallocations,repeatedrows,andchangedexplicitheaders. Encoderandseparate
parserreturncompleteoriginalsource, notjustsumorwordcount.
For everyN0..12,enumerate allN+1allocations;checkuniqueencodedrows,lengthN+3,
returnedorderedshares,correctzero handling. Forpositivea,b checkequalstart/end
anddirectedbigrammultiset atfixedN; zeroallocationsareoutside thatlemma.
Rejectmissing/truncatedheader,unknownsign,oddlengthliteral,unuseddigitpair,
noncanonicalTOTAL,equalrecipients,emptyblock,missingEND,wrongsumand strayrow.
Swappingrecipientsina VALIDnewheaderisnotanencodingerror:it changescontent.
MovingatallybetweenpositivefieldswhilepreservingNisalsoVALIDdifferentcontent.
Thesumcheckdetectswrongtotals,NOTwhichallocationwasintended. Noerrorcorrection.
Independentvalidatorimportsnoencoder/reader:recognizesheadersbydisjointalphabet,
pairsfixedliteralcodes,parsesrowrunswithfinitepattern,checks everyactualstream,
lengthformulaandfixedinvalidcases. RecordsourceknowncodecPASSseparatelyfrom
NO_NATIVE_BINDING. No testcount orroundtripisdeciphermentprogress.

## Assumptions and stops
Source-domainandteachingkeysupplied;modelnotlearnedfromthefournativeforms.
Existing1280pair-countcontrast motivates the question but doesnotbindT/K/A/Z,
numerals,recipients,units,batchesorheaders. Noe=one,k=batch,cheekey=allocation.
Nohistoricalattestation,fullprosecoverage,statisticalfit ornativeword-boundaryfit.
Original980RAWbytespreserved. A newnativeexperimentneedsindependentheader/total
androwbinding; successfultoyreadbackdoesnotopenreservesorsupplythosebindings.
