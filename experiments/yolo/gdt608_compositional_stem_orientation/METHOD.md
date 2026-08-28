# GDT608 method

## Question

Do the 64 ordered GDT605 BPE merges transport formal edge roles from their
left and right components, or must all 98 units remain unrelated atomic signs?

## Inputs

Published GDT605 merge/inventory artifacts and published GDT606 guarded rows,
unit sequences, and category tables. The 68-train/23-held physical-folio split
is unchanged; f84 and f84r remain absent. No page, image, generated plaintext,
or sidequest meaning is read.

## Method

Every final-unit event receives chunk, physical-line, paragraph, neighbour,
folio, hand, section, and Currier context. Four fixed predictions are compared:
GLOBAL pooled context; ATOMIC exact merged-unit context; DIRECT, which takes
left/initial behavior from `L` and right/final behavior from `R` for
`L+R=M`; and SWAPPED with the two sides reversed. A leave-one-merge-out ridge
model tests whether the simple side rule can be improved without using the
omitted merge's atomic target profile.

All 64 merges are retained. A 1,000-replicate null replaces each component pair
with one of eight other merges matched on train frequency and folio mobility.
Scores are also computed separately for every held folio and for the nominated
`ol`, `or`, `ok`, `ot`, `dy`, and `aN` pairs.

## Decision rule and claim ceiling

DIRECT must beat GLOBAL, SWAPPED, and the mobile pair null to establish a
directed backoff. If ATOMIC remains better by more than 0.02 primary bits, the
result is partial composition with pair-specific residual identity. Formal
edge roles may be retained; no component receives a word, sound, language, or
meaning.
