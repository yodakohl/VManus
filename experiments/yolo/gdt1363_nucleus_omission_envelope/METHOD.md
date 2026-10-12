# GDT1363 — Minimum missing whole-word nucleus carriers

Decision note:1042proves zero-exception impossibility for≤8fixed carriers, but
not how many whole words need an exception. This magnitude changes whether we
may claim substantial omission is necessary, versus a small unresolved tail.
1355optimized SIGNmass with zero empty words, a different objective. No old
source-book experiment is reopened. Smallest test: exact support coverage on the
same cache, two independent implementations, complete optimum witnesses.
Budget35minutes including preparation, proof, nativecount, validation/publication.
No arbitrary small/large cutoff, phonetic classifier, new corpus or decoder.

## Assumptions and implication

All1042carrier premises apply to each non-exception group: nonempty intact
unit-aligned carrier code over the same22workingunits; fixed≤Kcodeforms or
≤Kfamilies each retaining a commonunit; writtenwholeword ownership. Choose one
unit from each code/family. Every word not hit by these representatives lacks
all such carriers. Minimize misses over arbitrary≤Krepresentatives to obtain a
necessary lower bound on carrier-free group occurrences. This generously relaxes
actual code matching; a hit could be a consonant and does NOT establish a vowel.

K is fixed to3,5,7,8. Minimize occurrence count and wholeform type count
SEPARATELY. Do not combine their optima into an invented common key. ExactK
suffices for the≤K problem by monotonicity. Lowest numeric representative-mask
wins ties, with lexicographically sorted FULL22unit alphabet in each reader.
No carrier, vowel identity, omitted-vowel explanation, error or actual source
language will be assigned to an optimal set or missed word.

FULL and GE2 (wholeform on≥2physicalleaves) are separate predeclared panels.
GE2is sensitivity, not confirmation or a rare-word repair. Physical leaves
collapse recto/verso/foldout suffixes. Readers remain separate readings of one
manuscript. All original exact forms and counts retained; no string cleaning.

## Frozen outputs

For every reader/panel/K/objective, save optimum missed count, canonicalRmask,
representativeunits, both missed-occurrence and missed-type counts at that
witness, total affected physical leaves, and full missed-form list with exact
frequency, first source ID and leafset. Denominators are panel groups/types.
No per-language significance score. If bounds are small, say explicitly that
the zero-exception obstruction alone cannot demand a large omission mechanism;
if large, require an account of at least that mass. Neither implies an abjad.
Existing1228/1230/1255/1239source/model exclusions retain their original scope.

## Computation and access

Hash-fixed1233GROUPS.json.gz plus631PAGE_ALLOWLIST.tsv,1042proposal/proof,
new1043RAW and1355RESULT/manifest for scope and oldzero-exception comparison.
Only already admitted strict Pgroups with both outside gaps definite. No rawTSV,
newimage,websource,source-language corpus,f84/f84r/f116v/f1rbody or semantic edge.

Primary subset-zeta transform: F(M)=sum of frequencies (or types) whose word
support lies insideM. Misses forR areF(Sigma minusR). Enumerate everyR withKbits.
Independent validator enumerates representative combinations with covered-word
bitsets, not this transform. Source-free small support/weight cases are checked
before hashlock; nativecounts follow lockedprotocol, code and proofreview.
