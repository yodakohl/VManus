# GDT231 — q13 visual-homolog family atlas

## Question

Do labels placed in the same independently human-described visual unit share
more source-native family structure, and where does the exposed f82r
left/right “waterfall” pair rank?

This is an exploratory semantic-grounding atlas.  Human descriptions nominate
the units before formal families are joined, but the specific pair and metric
were inspected before this method.  All probabilities are descriptive
postselection diagnostics.

## Inventory

Use all exact-locus annotation rows on f75–f83, excluding every f84 row at the
raw-line gate.  Retain rows explicitly tagged `LABEL`.  A visual unit is the
existing `(page, unit, unit_description)` key; no new ownership is invented.
Join only whitelisted loci to the strict source-native family-consensus group
table.  Preserve `|` between source groups.

For every unordered pair within a visual unit report:

- leading common-family length;
- trailing common-family length;
- normalized Levenshtein similarity;
- exact-family equality;
- human certainty and local-relation metadata.

The f82r pair `f82r.35/.38` is compared with all same-page pairs, all same-unit
pairs, and length-matched same-unit pairs.  The f82v direct “pool” pair
`f82v.3/.45` is a mandatory counterexample.  No display-form substring is used
for scoring.

## Ceiling

A shared family prefix can nominate a local apparatus/referent-class marker.
It cannot establish `dar`, `BAC(A)`, or any source group as “water,” “flow,”
“waterfall,” a noun, morpheme, sound, language, plaintext, or translation.
