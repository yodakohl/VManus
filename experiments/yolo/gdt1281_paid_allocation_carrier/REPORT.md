# GDT1281: a complete source-known allocation MODULE, no Voynich reading

**SOURCE_KNOWN_MODULE_ROUNDTRIP_PASS.** A fixed teachingcodec preserves the full
names/identifiers, separately written total, ordered allocations, zero shares,
repeated rows and block changes. It uses15of the existing22working-sign slots.
This completes one previously unpaid carrier forRAW980's restricted source
module. It is not a full language, a fitted manuscriptwriter, historical evidence
or a decipherment. Native status: **NO_NATIVE_BINDING_NO_STATISTICAL_FIT**.

## The actual hand procedure
A header explicitly names left recipient, right recipient, batch, countunit and
TOTAL. Names use a fixed two-sign literal table; reserved markers delimit the
five fields. Read and validate that header before any row. A row has the role
notation `A T^a K T^b Z`: tallycounta forleft, countb forright;Krefersto the one
batch in the header. Everyrowmustsatisfy a+b=TOTAL. END closes thatblock; another
block needs its own completeheader. Repeatedrows remain repeatedproposals, not
extra material or repeated executedtransfers.

This realizes K as a fixed header-reference sign. RAW980's illustrative K was
the repeated literal batchname. That change is explicit, not a silent repair or
proof that a native k is a batchmarker. The originalRAWfile remains unchanged.

For Ada/Bela and a separately declared total4, these teachingrows encode:

| Role notation | Sourceplan |
|---|---|
| A T K T T T Z | Ada1, Bela3 |
| A T T K T T Z | Ada2, Bela2 |
| A T T T K T Z | Ada3, Bela1 |
| A K T T T T Z | Ada0, Bela4 |

The first three have exactly the same directed adjacent-sign counts, but different
ordered shares. The zero case changes adjacency; it is allowed but outside that
positive-run equivalence lemma. These labels denote roles in an invented codec,
not interpretations of cheekey/chekeey, e, k or other manuscript forms.

## Fully paid alphabet and framing
Seven signslots encode base7digitpairs. A fixed38character table covers uppercase
A–Z,0–9,space andhyphen. Eight further signs are H/F/G/A/T/K/Z/END. Literaldata
andcontrols are disjoint; unusedliteralpairs are invalid. No unencoded names,
freeescape, decimaldigits, punctuation or headerlength is supplied externally.
TOTALuses canonicaldecimalspelling throughthesame literal table, domain0..9999.
Other quantities/characters are outside the declared source-domain, not silently
normalized. UNITis an explicitly taught discrete countingunit; a string alone
does not establish a physical scale or an unknown medieval measure.

For reproducible rendering the first15entries of the unchanged22working inventory
are deliberately assigned in inventoryorder. This arbitrary source-known teaching
key is NOT a proposed Voynichkey. Its glyph/function correspondences must not be
exported as lexical or component facts. No manuscript token is decoded here.

Whitespace is purely displayformatting and ignored everywhere by the reader.
Source-name spaces are encoded. Canonical output wraps every24workingunits;
breaks may split literalpairs or tallyruns because the stream is reassembled
before parsing. Thus no extraCONTglyph is needed under THIS explicit layoutrule.
Native word/line boundaries have not been identified with these logical records.
A completeproseorhistoricalpage-layoutclaim does not follow from this convention.

## Costs and full-message checks
Each header costs twice the total characterlength of the four identifiers and
the decimal total, plus6framingunits. A logical row costs N+3units; ENDcosts1.
The stored sourcepacket has3blocks/11rows and costs210units:

| Block | Header | All rows | END | Total |
|---|---:|---:|---:|---:|
| total4, sixplans includingzeroandrepeat |40|42|1|83|
| total0, onezero/zeroplan |40|3|1|44|
| total6, fourplans and space/hyphen/digitidentifier |46|36|1|83|

Names/headeroverhead is substantial, not hidden in short example rows. Unary
cost grows with N; this is not a claim of efficient generaltextcompression.
EveryNfrom0through12 was separately encoded with ALLN+1allocations(91total).
Each yields distinctrows, exactroundtrip, lengthN+3, and fixedbigramcounts for
positive shares. All38literalcharacters roundtrip; fullfixturepacket also survives
wrapping at1,2,3,24and41units. No wordfrequency or statisticalVoynichscreen was run.

Eleven malformedstreams are rejected, covering missing/truncatedheaders, odd or
unusedliteralcodes, unknownsigns, leadingzeroTOTAL,equalrecipients,emptyblock,
missingEND,wrongsumandastrayrowafterEND. Independentvalidation imports no codec:
a regex/frame and literal-table parser reconstructs everycomplete source,
checks the91allocations, everymalformedstream and costformula. PASS concerns the
supplied-source module only. Programs/protocol/fixtures were locked before runs.

## What the independent total does—and does not do
Under TOTAL4, a rowwithshares2and3 is invalid. A rowwith1and3 is valid, as is2and2.
Thetotalcheck therefore does NOT select the intendedallocation amongsame-sum
variants or detect every transcriptionmistake. It constrains a proposedreading,
not magically supplies its missingmeaning. Changing recipients in a newvalid
header alsochanges content without making the syntax invalid.
ForfixedNthereareN+1possibleorderedallocations, ofwhichN−1are strictlypositive
whenN>=2. Their coexistence does not imply a chronological series of transfers.

## Decision and next requirements
Retain this as a concrete content-bearing construction showing how different
messages can share first-orderstatistics. One narrowdesigngap is resolved: a
fully specified alphabet/framing/reader exists for the restricted module.
Unrestrictedprose,historicaluse,worddistributionfit,nativeglyphvalues,actualrow
scope and independently readable totals/recipients remain absent. No native
application,sourcefit or glyphmeaning is selected. A furthernative test needs
those bindings and an independently fixed falsifier; toyroundtrip alone supplies
none of them. No automaticextension to a decoder or fitting extra signs.
No native source/image, sealeddata, reserves or publicpush. Local only.
