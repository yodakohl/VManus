# GDT268 — q13 wrapper-stage transfer to Q20

## Frozen prediction

GDT267, published before this score, predicts that q-wrapped rendering is
enriched in earlier records and bare/`NONE` rendering in later records.  Test
that direction unchanged in the independent Stars/Q20 record register.

## Q20 panel

Use the existing f84-free GDT127 field inventory: 170 star-defined records on
13 pages in each of the alternate ZL3b/IT2a/RF1b readings.  Alternate readings
are sensitivities of one manuscript, not replications.

Within each page, sort the human-defined star ordinals.  Compare the first and
last `floor(n/2)` records, excluding the middle record on odd-sized pages.
Aggregate all compiler cells inside each selected record, then compute per-
group `EARLY - LATE` rate differences for `q` and `NONE`.  This exactly
normalizes opportunity before combining pages.

The ZL3b reading is primary.  Enumerate all `2^13 = 8,192` page-level sign
flips and share them across the two frozen directions.  Report local and
max-two p-values.  IT2a and RF1b repeat the unchanged calculation as reading
sensitivities.

## Decision

Transfer requires the predicted sign for both `q` and `NONE` plus ZL max-two
`p <= .05` for both.  Same-direction but nonpassing results are a weak
cross-register tendency and do not globalize the q13 function.  No result
assigns a topic, word, morpheme, semantic operator, sound, plaintext, or
translation.  The input contains no f84 row and no new f84r access occurs.
