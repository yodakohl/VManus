# GDT1380 — Certified contextwise consonantal cost bound on a new admitted projection

## Decision and budget

GDT193/194 local-search failures are not exhaustive key exclusions. IDEA1052
replaces search with a rigorous optimistic bound for a NEW, explicitly scoped
193-style injective model. Unknown: whether even independently optimal local
assignments cost more than a matched anonymous code. A positive certified margin
stops every global key for this fixed cost/model/input conjunction; a nonpositive
margin is inconclusive, not a key or model success. Budget35minutes including
scope/proof, source preparation, implementation, validation and publication.
No automatic tightening, new corpus, key search or decoder repair afterwards.

## New native scope and exact representation

Use the six existing915SOURCE DISCOVERY/EVALUATION caches,631allowlist, readers
ZL3b/IT2a/RF1b separately. No old016consensus rows or old193totals. Select admitted
kindP loci, excluding f1r,f116v,everyf84prefix and oldunknown f102v2.33. A line
here means a complete transcribed P-locus, not a proven sentence or uninterrupted
physical writing event. Reset at each such selected source locus.

Before retaining any body require unique original indices1..source_group_count,
nonempty complete literal words in the exact old25ASCII alphabet
`abcdefghijklmnopqrstuvxyz` (no w), exact edition|locus|GNNN IDs, and reciprocal
DEFINITE_SPACE at every inner seam. Outer separators unrestricted. Reject the
WHOLE line if any gate fails; do not create neighbors across omitted groups.
Metadata/page/edition must agree with source. All fixed lines and exclusions kept.

Recreate old012/189 string transformations mechanically, independently perreader:
1. Remove the first matching nonempty prefix from che,ch,sh,t,s,d,q only when a
   remainder exists; then remove terminaldy only when remaining length>2.
2. Remove terminalm if length>1; remove the first fitting tail from
   aiin,air,ain,ar,al only when a remainder exists. If original removed prefix
   wasch/che/sh, remove initiald if length>1.
3. Count these preparsed hosts across this reader's eligible corpus. License h
   if h,oh,oth all occur, plus fixed ar,al,ol. From each prehost remove initialot,
   otherwiseo, iff the remainder is licensed. No cross-reader licensing.

These are inherited lossy conventions, not identified morphemes or phonemes.
The resulting NEW_PAGE_HOST is a new projection: separate readers, restricted
scope, complete loci, newly determined license inventories. It neither reruns
nor globally certifies the old193stream, which included240outside-scope records.
Use its ASCII characters, NOT22working-unit parsing. Preserve one SPACE between
hosts. Build order2context counts with typed BOS and SPACE; reset histories at
locus starts while retaining accumulated KT counts. No EOS event.

## Frozen external probability models and paid comparison

Hashcheck all six existing prepared packs against gdt001_language_pack_manifest:
latin,middle_high_german,middle_french,old_italian_tuscan,medieval_czech,
old_hungarian. No corpusbuilder or normalization changes. Per original prepared
line, delete a/e/i/o/u within words, omit empty words, join remaining words by
oneSPACE; discard empty lines. Train integer order2counts with line-reset BOS.
Dirichlet0.5 uses21consonants bcdfghjklmnpqrstvwxyz plusSPACE: probability
(2count+1)/(2context_total+22). No vowel smoothing cells. Sourcepack text stays
local; publish model counts, exact provenance/hashes and source-counting code.
Source validation starts from published counts; optional reconstruction uses
only hashmatched prepared packs. This is not a newlanguage/genre identification.

For mactive ordinary nativecharacters, map injectively into21consonants. m>21
means EMPTY_INJECTIVE_FAMILY, no cost certificate; zeroevents means NO_EVENTS.
SPACE is fixed target26, BOS is history27. Internal native storage may use
strings ' ' and '^' respectively; neither is an ordinary letter.
Key cost=log2(21!/(21-m)!), language selector=log2(6). Common order/model overhead
identical on both sides cancels. Compare with order2KT over mordinary types plus
SPACE on exactly the same NEW_PAGE_HOST events, no oldbaseline substitution.

## Exact optimistic bound

For each native contextc=(u,v), ordinary context positions may independently
choose ANY target consonant; SPACE/BOS positions are fixed. Equality constraints
between ordinary context positions and their next-symbol assignments are
intentionally dropped. For each targetcontext, sort its21ordinary targetcosts
ascending and positive native next-character counts descending. Pair them;
add observedSPACEcount times fixedSPACEcost. Take the minimum over all allowed
targetcontexts. Different native contexts may choose incompatible assignments.

Every true global injection appears among these relaxed possibilities in each
row. Consequently the sum of independent row minima is no GREATER than its
true total. This sorted pairing is exact for the relaxed rank-one assignment
cost, not a local optimizer. Record all native row counts, minimizing target
context and each conservative row bound for every pack/reader.

This bound is injective only.194's many-to-one keys are not covered. Example:
weights1,1 and targetcosts0,100 give injective minimum100 but merged minimum0.
Do not transfer an injective lower bound to homophony or omit a negative cost.

## Certified numerical contract

All costs are intervals in integer ticks of2^-32bits. Decimal precision60:
correctly rounded ln(integer) is enclosed using next_minus/next_plus;
ln1=0exact. Directed FLOOR/CEILING subtraction and division by the enclosedln2
produce log2(D/N) enclosures for positive integers N<=D. If reduced N,D are
both powers of2, use exact integer log2difference. Floor lower endpoint and
ceil upper endpoint to ticks. Cache by integerarguments. Thereafter all weighted
sums, sorting, row minima and margins use exact Pythonintegers.

For KT, percontext counts n_x and totalT give
sum_(j=0..T-1)log2(2j+K) - sum_x sum_(j=0..n_x-1)log2(2j+1), K=m+1.
Build upper cost from numerator-upper minus denominator-lower and lower vice
versa. This equals sequential KT with accumulated counts and locus-reset
histories. No floating lgamma or roundedprobability conversion.

Perreader/pack: certified paidLB=(sum rowlower)+keylower+selectorlower;
margin=paidLB-KTupper. If margin>0, CERTIFIED_NO_KEY_BEATS_MATCHED_KT;
otherwise BOUND_INCONCLUSIVE. Report integercertificate and bit conversion.
A finite-union exclusion for a reader requires every frozenpack certified.
No root-key recovery, mapping stability, plaintext or universal language ban.

## Validation and claim ceiling

Freeze input/LMcount hashes, full protocol, both programs and prospective proof
before nativeprojection. Source-free tiny alphabets exhaust all global injections
and compare with relaxedrowbounds; exerciseSPACE/BOS, repeatedcontext symbols,
injective sortedassignment and the invalid194transfer. Check certified intervals
with independently computed higherprecision enclosures and exact power-of2 cases.
Independent validator reconstructs all nativeeligibility/hosts/licenses/counts,
all modelcost intervals, every minimum and same-stream KT without primaryimports.

Old193/194numericalfailures and corrected local-search scope remain. A new positive
bound would certify this code-length comparison, not the same oldfullinput and
not an entirelanguage, allconsonantal scripts, a natural alphabet or meaning.
A nonpositive bound may simply be too optimistic. No automatic solver expansion.
f84/f84r,f116v,f1rbody and reserves remain closed. No relation-edge score.
