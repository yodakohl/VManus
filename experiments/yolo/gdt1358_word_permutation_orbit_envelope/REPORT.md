# GDT1358 — Reordering cannot hide enough repeated words in the fixed profiles

**All24fixed comparison-profile/family/reader combinations violate a necessary
frequency bound.** Even arbitrary reordering of a fixed base spelling per exact
source word cannot reproduce the corresponding fixed8000-group target prefix.
At least1116–1665whole target-group replacements (13.95–20.8125%) would be needed
before the necessary frequency inequalities could hold. These are LOWER bounds,
not optimal repairs, measured manuscript error rates or a language exclusion.

The native-only result is separate: quotienting by cyclic rotation leaves
96.9–97.6%of FULL raw word types distinct; even quotienting by ALL permutations
leaves81.6–83.3%. A cut rule has limited ability to make these observed forms
variants of the same fixed source spelling. No actual synonym classes follow.

## Native inventories, without selecting a source language

| Reading | FULL groups | Raw types | Cyclic classes | Multiset classes |
|---|---:|---:|---:|---:|
| IT2a |22528|4272|4141|3484|
| RF1b |19321|3818|3706|3182|
| ZL3b |19332|3773|3684|3142|

The source would need at least the corresponding number of exact token types
under each family. Several source words may share a class, so members of a
native class are NOT thereby the same source word. This is not a count of
linguistic lemmas or phonemes. Working units and source-word/group boundaries
remain inherited assumptions. These are alternate readings of one manuscript.

The comparison uses a newly declared FIRST8000prefix of each reader's strict
1233cache, in stored order. These overlapping prefixes are not identical physical
token selections and are NOT the1174native samples. All data were already exposed.
No old1174+/-400tolerances, threshold or independent-holdout claim is imported.

| Reading | Prefix raw types | Cyclic classes | Multiset classes | Cyclic Top10 | Multiset Top10 |
|---|---:|---:|---:|---:|---:|
| IT2a |2127|2080|1830|1258|1265|
| RF1b |2051|2008|1775|1246|1250|
| ZL3b |2019|1987|1751|1278|1285|

## Source-profile comparison and a transparent certificate

Each of the four existing1177comparison sources contributes its unchanged first
8000stored tokens. Source type counts b4/w1/bs1/gr1 are1131/1275/1105/1199.
Case, punctuation (including separately stored punctuation tokens) and editorial
projection are retained. None of these profiles is identified as the original
Voynich source or a universal representative of its language or manuscript genre.
The results do not automatically extend to other passages of these same books.

The target eligibility filter retains only strict internal groups, while these
source prefixes have no matched eligibility filter. Exact correspondence of the
selected8000source tokens to the selected8000target groups is therefore part of
the hypothetical comparison, not an established alignment. The result does not
exclude a writer generating a larger text followed by selective target filtering;
that would require a separately specified selection model. No such model is fitted.

Minimum required target-group replacements, a necessary lower bound only:

| Source | IT cyclic | RF cyclic | ZL cyclic | IT arbitrary permutation | RF arbitrary permutation | ZL arbitrary permutation |
|---|---:|---:|---:|---:|---:|---:|
| b4 |1398|1318|1314|1350|1310|1288|
| w1 |1284|1165|1163|1200|1151|1116|
| bs1 |1418|1290|1297|1307|1281|1262|
| gr1 |1665|1595|1580|1626|1588|1552|

For example, the 35 most frequent distinct w1 source words occupy 3820 positions. Whatever
fixed base spellings are assigned, these 35 word types must occupy at most 35 multiset
classes. Those classes therefore need at least3820positions. The35largest ZL
prefix multiset classes contain only2704positions. Their deficit is1116. Changing
one target group can increase that largest35-class total by at most1, so at least
1116changes are necessary even before testing integer grouping or a full writer.
The stronger-end certificate compares4283source occurrences with2618target
occurrences at k36for gr1/IT cyclic, yielding1665.

## Why this covers more than one rotation recipe

IDEA001034moves the beginning of each word according to the previous word length.
The present test grants MUCH more freedom: each exact source token can receive
any fixed nonempty base spelling over the working units, and every occurrence
may choose ANYrotation, or ANYpermutation for the larger family. No22-letter
source alphabet, practical selection rule, cost limit, injective codebook or
unique inverse is demanded. Different source identities may share an orbit.

Nevertheless each exact source token always maps to one orbit. Thus target
orbit frequencies must be sums of source-word frequencies. Their type count
cannot exceed source types; their largest-k counts must be at least the source
largest-k counts for every k. We checked the complete cumulative vectors with
zero padding. D is the maximum of all positive deficits and the type deficit,
never their sum. In these comparisons the prefix-frequency bound is stronger.

These inequalities do not solve integer bin assignment. For example source
counts[2,2]and target counts[3,1]pass them but are not a possible coarsening.
D=0would therefore not establish a writer. No count repair, mapping optimizer,
plaintext search, threshold tuning or new source was performed after the result.

## Relation to prior results and decision

1256already excludes the fixed Deot/literal-letter permutation case using one
rare six-unit multiplicity witness. We did not recount or reopen it.1202allows
at mosttwo whole spellings per source word; this family allows unlimited order
variants subject to the actual orbit.1323's within-page anagram-neighbor test
stopped for capacity and remains stopped. This global frequency calculation is
a different necessary consequence, not a rescore of those older tests.

Keep IDEA001034source-unspecified and inconclusive as a manuscript hypothesis.
It has a valid formal inverse, but no independent source/phonetic binding. The
new counts close its enlarged fixed-base/reordering family on these four exact
comparison prefixes. Do not run an alphabet or cut optimizer for those same
conjunctions. Context-dependent changes to the unit multiset, changed group
boundaries, distinct source profiles and different writing mechanisms remain
outside this result; none is selected as a retrospective repair. No broad claim
that meaningful or phonetic text is impossible, and no native meaning assigned.

## Reproduction and validation

Protocol, code, independent validator, controls, proposal, source-free peer proof
review and inputs were locked at13:24:49UTC before native orbit counting. The
runner controls covered21504small frequency/map cases,167196one-replacement
cases and1092short words. The independently written validator did not read or
import the runner; its own controls included4330coarsening assignments,
45076one-replacement cases,1092words and a necessary-but-not-sufficient fixture.

Native validation independently groups by multiplicity and explicit cyclic
membership, then reconstructs canonical representatives. It checks all61181raw
native groups,12panels,36120orbit-member rows,32000source-prefix tokens and24
comparison certificates: PASS. Every member, exact source ID, frequency vector
and maximum-gap witness is retained. This is arithmetic/provenance verification,
not independent palaeography, semantic confirmation or inferred error frequency.
No raw TSV, image, new corpus, reserve, f84/f84r/f116v or f1rbody was accessed.
