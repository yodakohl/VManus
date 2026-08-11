# ZCV001 — zodiac clothing-state capacity

Date: 2026-08-11

Status: `SCORE_BLIND_CAPACITY_ONLY`

## Question

Does the existing human zodiac documentation, conservatively supplemented by
source-bound native visual inspection, provide enough within-page and
within-ring DRESSED/UNDRESSED mobility for one formal-marker experiment?

This is a capacity audit. It does not score a clothing association and it does
not inspect or publish a candidate feature.

## State sources

The public Stolfi/Grove unit notes explicitly call figures *dressed*, *naked*,
or *partly dressed*. The frozen projection binds these four source documents:

- `f71r.S2`, SHA-256 `9b9df96ddd4d461c9a5e8b2623b6c85b9d35c72b81f3cde07a39c5b10cd21a18`;
- `f71v.S1`, SHA-256 `681a57432192ccb613c1d8eceffddafeb5776823daa650c7db14c1956c113eb0`;
- `f72r1.S2`, SHA-256 `4fb22fc16c4411d83bcbeaa6ff5798a4506f6edc8d035e8ccb24a4766d264e88`;
- `f72r2.S1`, SHA-256 `381a580a7a98d87f85f61350d0752b024410176127bbd4842ebb069215cf0347`.

Where those notes give a clock/Grove position but no clothing state, direct
native inspection uses the official Yale canvas `1006203`, labelled “71v and
72r”. The complete official image is 8865 by 3018 pixels and has SHA-256
`45f7caf4b58744fdcd4928887661b56a135538a5a40a24fea6ca6c5239898269`.
The Yale manifest has SHA-256
`317d58fd9ea90392a83d9858a91eada3d0b41416a3c835857dc0154bd123a309`.

Native grades use only the visible upper-torso garment boundary at the human
clock/Grove position. Unclear, obscured, partly dressed, carpet-overlapping,
and fold-edge figures are `UNCERTAIN`. No Voynich glyph, label surface, OCR,
CLIP output, embedding, sex inference, or object name enters a grade. Native
grades are machine-authored source-bound observations, not human annotations.

## Formal-source eligibility

The state projection is joined only by `source_record_id` to the validated
current-locus crosswalk. A row is strict only if it is primary-eligible, has a
current locus, its page and human `RING:GROVE_N` key agree, and every consensus
group at the locus is `kind=L`, `grammar_scope=DIAGNOSTIC_NONPROSE`,
`strict_zero_alternative=1`, and exactly indexed `1..consensus_group_count`.

ZL3b, IT2a, and RF1b are alternate readings of one manuscript, never three
replications.

## Target-blind feature capacity

For strict rows, construct the same family/member n-gram, prefix, suffix, and
whole-group feature universe frozen in PRC001R2. Exact member features require
byte-identical complete ZL/IT/RF STA-code sequences. Features are binary per
physical label and never cross group boundaries.

Without reading DRESSED/UNDRESSED states, retain a feature iff it occurs in at
least four strict labels and is present and absent in every page-by-ring
stratum. Serialize the sorted feature names privately as one UTF-8 feature plus
LF; publish only its count and SHA-256.

The future null is available only if every strict stratum contains both scored
states and the product of its retained-position cyclic rotations is at least
1000. Rotations will carry the complete DRESSED/UNDRESSED/UNCERTAIN state
vector, preserving state counts, clustering, and uncertainty geometry.

## Capacity gates and ceiling

Pass requires exactly 35 projected records, 33 strict labels, four mixed
page-by-ring strata, both scored states on both physical folios, at least 24
target-blind features, and at least 1000 cyclic worlds. Any later target must
be separately preregistered and hash-frozen before association scoring.

A capacity pass supplies no clothing word, person name, zodiac name, lexical
value, sound, language, cipher, plaintext, meaning, or translation.
