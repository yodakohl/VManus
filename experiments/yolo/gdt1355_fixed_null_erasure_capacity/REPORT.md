# GDT1355 — Exact fixed-null capacity stays below half of sign occurrences

**EXACT_FIXED_NULL_ERASURE_ENVELOPES.** If the same working-sign types are erased
everywhere and every retained whole group must keep a nonempty residual, at most
14.01–31.91%of the FULL working-unit occurrences can be erased, depending on the
transcription. On the recurrent-form sensitivity panels the maxima rise to
40.73–44.33%. Even those weaker panels do not permit erasing half the occurrences.

This condition excludes a majority-fixed-null writer on these panels. It does
NOT establish that any sign is a real null, identify meaningful residuals, reject
context-dependent nulls, or cover systems with entirely empty/padding groups.
Counts concern the stipulated22working units, not pixels, physical pen strokes,
ASCIIcharacters, phonemes or all manuscript text.

## Exact capacity bounds

| Reading / panel | Groups | Unit occurrences | Maximum erased occurrences | Fraction | Maximum null types |
|---|---:|---:|---:|---:|---:|
| IT2a FULL |22528|102247|32622|31.9051%|9|
| RF1b FULL |19321|86585|12134|14.0140%|8|
| ZL3b FULL |19332|89732|25941|28.9094%|11|
| IT2a GE2 |19687|85667|37559|43.8430%|13|
| RF1b GE2 |16786|71739|29217|40.7268%|13|
| ZL3b GE2 |16865|75199|33337|44.3317%|13|

GE2retains whole forms on at least two physical leaves. It does not diagnose
rare forms as errors, replace FULL, or create a holdout. The large RFchange from
14.01%to40.73%shows substantial sensitivity to rare whole-word premises. Readers
are alternative transcriptions of one manuscript, not independent replications.
Every maximum has an attaining set and an independently verified upper bound.
No posterior probability or actual null fraction is estimated; deleting nothing
is also feasible. Old pure-run/group-boundary ambiguities remain conditional.

The maximum number of null TYPES is a separate objective. More than half the
22types can be designated null on GE2, while fewer than half of occurrences can
be erased. The most frequent types cannot all be erased together without emptying
some words. Do not combine the last two table columns into an invented single
optimum: they need not be attained by the same set.

For ITGE2the occurrence-maximizing set has12types and erases43.8430%; the maximum-
13-type witness erases40.2045%. For ZLFULLthe mass witness has10types and erases
28.9094%, while the maximum11-type witness erases20.8086%. For ZLGE2the mass
witness has12types and erases44.3317%; the canonical13-type witness erases34.6707%.
All ties and the fixed lowest-mask tie rule are recorded, not selected by meaning.

## Why whole words constrain fixed erasure

LetNbe the globally erased types andS(w)the types appearing in a complete word.
The residual is empty exactly when S(w) is contained inN. Every feasibleN must
avoid that condition for EVERYretained word. A word containing only one sign
type, whether one occurrence or a repeated run, forces that type outsideN.
This does not assign the word a meaning; nonempty payload is the explicit model
premise. If a writer allows that entire group to be padding, the premise changes.

After those mandatory signs are retained, all remaining null subsets were
exhausted. The primary uses Boolean propagation to mark supersets of forbidden
word supports. Independent verification checks each candidate directly against
those supports in a different enumeration order. There are62,720candidate masks
across six panels after the mandatory reduction. This number is an arithmetic
verification detail, not six independent experiments or decipherment progress.

The actual globally mass-maximizing sets on FULL are recorded here as **capacity
witnesses only**, not proposed real null assignments:

- IT2a: cfh,ckh,cph,e,f,i,k,p,q.
- RF1b: cfh,ckh,cph,cth,f,i,p,q.
- ZL3b: cfh,ckh,cph,e,f,i,m,n,p,t.

Removing these stipulated sets leaves every sampled group nonempty. That alone
does not preserve distinctions between source words, establish a dictionary,
explain insertion choices or show plausible language statistics. No erasure set
has been adopted as a Voynich reading. Optimal masks, weights, source supports,
mandatory-word witnesses and residual-length histograms needed for reproduction
are retained in RESULT and the six compressed certificate files.

## Separate RF consequence: nullable CODE entries do not remove the old obstruction

IDEA001031concerns a different level. Suppose the written codebook is freely
uniquely decodable, as in1267, but allow arbitrary OTHER code-entry expansions
to be empty. RFhas complete wholek,e,s, so their own entries must still expand
to nonempty source words. Existing bound supports are:

- k:2occurrences on the single selectorf95v1, at.9G004and.10G004.
- e:1occurrence atf58r.9G009.
- s:141occurrences, with all original IDs retained in the prior/current packet.
- keeees:1occurrence atf21v.3G002, the same rare physical witness as before.

FreeUD fixes the last word's parse as k|e|e|e|e|s. Thus its source must still have
XU^4Y with nonemptyX,U,Y, even if every unrelated entry may expand empty. The
same five fixed1240/1267source populations lack such a word. This extends that
RF source/model exclusion to nullable OTHERentries; it is an old-premise logical
consequence, not a new source census or language rejection.

The rare RFpremises remain material. Do not transfer the argument automatically
to IT/ZL orGE2. Nor may the numerical global-sign erasure ceiling be transferred
to arbitrary parsed-entry nulling: an entry containing e could be null while
another entry containing e is not. Uniform deletion of the WORKING SIGN e is
stronger. The two claims are kept separate in RF_NULLABLE_COROLLARY.json and
in this report. No source word is translated or assigned an English function.

## Research decision and retained boundaries

The fixed global deletion family cannot explain a majority of the stipulated
unit occurrences as always-erasable padding while retaining nonempty groups,
even in these recurrent sensitivity panels. Higher deletion rates require a
changed writer premise, not another mask optimizer. Such changes are neither
forbidden in general nor selected automatically: context-dependent roles,
wholly empty groups, different units or boundaries need their own test.

This does not make1354's alternative codebooks into phonetic readings. Its exact
coverage and the1353/1354singleton classification stay unchanged. The old523/528
path-local semantic-null claims are historical assertions and were not reused
as lexical evidence or global null licenses. The old fixed-source failures are
retained, with only the narrowly stated RFextension above. Confirmed meanings
and sound assignments added:0.

## Source and validation

Only the existing1233strict internal P-group cache and oldallowlist enter the
new census. Original raw groups/readers/boundaries remain, with no raw mixedTSV,
image, reserve, f84/f84r/f116v/f1rbody or new external corpus. The protocol and
code/input hashes were frozen before capacity scores.384source-free support/
weight fixtures and a pure-run fixture matched the two independent algorithms
before native execution; a source-free peer checked scope and proof.

The validator imports no runner. It reparses all strings, rebuilds support and
frequency tables, exhausts all62,720reduced masks directly, checks both objective
maxima/ties/canonical witnesses and every residual, and verifies the RFcorollary's
unchanged exact premises/source-result counts. ArithmeticPASSdoes not validate
physical transcription, actual null identity or semantic content.
