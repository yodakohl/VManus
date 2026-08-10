# LRG002 zero-gloss score-band atlas

Status: `REGISTERED_DESCRIPTIVE_DERIVATIVE`

Reconstruct the validated LRG002 opposite-parity raw score and exact
page-by-symbol-count average rank for all 5,824 fixed B/P prose groups. Bind the
rank digest to the confirmed target before output.

Map the bounded rank to five deterministic bands:

`R = clamp(1 + floor(5 * (rank + 0.5)), 1, 5)`.

`R5` means only the top relative fifth of the local label-profile score and
`R1` the bottom relative fifth. Ties retain the same average-rank band. Emit the
band, corrected segment coordinate, source-native family surface, and frozen
metadata, but never a raw score, numeric rank, learned family weight, EVA
string, or English gloss. Render one compact line per corrected segment.

This is a deterministic reading aid, not another hypothesis test. Bands may be
used as structural observations after exact independent reconstruction. They
are not words, names, identifiers, nouns, POS, semantic classes, confidence in
a translation, plaintext, or translation.
