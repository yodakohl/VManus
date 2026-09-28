# GDT1080 — exact `chor`/`shor` against frozen reproductive drawings

Status: frozen before reading target occurrences in the visual panel. This is a
small, postexposure exploratory comparison, not a fresh holdout.

## Decision note

GDT768 leaves `chor=flower, shor=fruit/seed` and its exact reverse tied.
GDT364's anonymous family atlas found no adjusted three-class signal, and
GDT366's two within-folio image contrasts failed. They did not score the two
complete words directly against all frozen GDT364 image classes. The question
here is whether that remaining exact-word directional contrast is large and
consistent enough to prefer one **working** rendering. A null or reversed
contrast leaves both renderings tied. Even a positive contrast changes only a
C0 display preference: image content is not an independently owned word
referent, and the prose may mention a different plant part.

Smallest adequate test: one exact-form page table for the entire previously
annotated GDT364 panel, its within-folio pairs, and three alternate readers.
Budget: 20 min preparation, 25 min implementation, 15 min validation, 15 min
publication; stop expansion at 75 min and reassess. No decoder, morphology,
new visual labels, or new admission.

## Frozen data and representation

Use all GDT364 `gdt364_panel.tsv` rows whose page is present in the admitted
179-selector word-profile cache, without selecting pages on target occurrence.
The panel SHA256 is
`76b51f8bf05459e8d86650e14810b7b6e5775e0c8906c091efcd2bb61db24235`.
Two panel selectors (`f54r`, `f90v2`) are absent from that cache and remain
explicitly unscored; do not substitute f90r1 or another part of the foldout.
This membership correction was made after a pre-data assertion failed, before
any target-group query or result. The cache
receipt must match the admitted allowlist SHA256
`f0def5a04bd91443cf4770c78f1b67e62cac2060627d8de38faba27899188483`
and source SHA256
`4b649c8290d5afc7a5fbcc8e98db2bc123a1ceb5f3858d3befa781ce96b680f0`.
Reject any `f84*` row, including `f84` and `f84r`. Use only `kind=P` groups.
Count exact raw whole groups `chor` and `shor` separately in ZL3b, IT2a,
RF1b; they are alternative readings, not replicate manuscripts. Page length
is all admitted `kind=P` groups in the corresponding reading. The panel image
classes are `FLOWER_SIDE`, `BERRY_NO_CIRCLES`, and `NO_FRUIT_OR_FLOWER`.

## Frozen comparison and decision

Primary ZL3b contrast: for each of FLOWER_SIDE and BERRY_NO_CIRCLES, aggregate
exact `chor` and `shor` counts and all prose groups. Report per-1000-group
rates, the within-class `chor/shor` ratio, and the cross-class odds ratio
`(chor_F+0.5)*(shor_B+0.5)/((shor_F+0.5)*(chor_B+0.5))`. A value above 1
favours `chor=flower`; below 1 favours the reverse. Report the third class
without using it as a zero-meaning proof. Report all page counts, including
zero pages, rather than picking examples.

A directional C0 **preference**, not translation, requires: at least three
occurrences of each target in each of F and B in ZL3b; cross-class odds ratio
at least 2 for one direction (or at most 0.5 for reverse); same sign in both
other readings; and same sign for the *sum* of the two frozen within-folio
berry-minus-flower contrasts f4 and f17. Report each pair separately, including
zero counts. If any gate fails, retain the tied directions. No significance
claim: this pair was selected after extensive exposure, the image classes are
imperfect proxies, and no suitable control for the entire selection process
exists. No meaning, plant name, or lexical component is confirmed.

Dependencies: exact transcription/word boundary; visual descriptions reflect
drawn organs; prose refers to the depicted plant and perhaps its depicted
organ; page-level scope is sufficient to see a tendency. The last two are
unverified and are the chief alternatives to a lexical explanation.

For the pair gate, compute the same continuity-corrected F-versus-B log odds
on f4v/f4r and f17r/f17v separately, then add the two log odds. Its sign must
match the all-page log odds; individual pairs may disagree and are displayed.
