# GDT885 — no nontrivial reversible three-state common-endpoint machine

Every one of the 1,048,576 sign assignments has exact rank20 over F3.
The independent forward-array computation matches every byte of the producer's
reverse-scan/bitset rank vector. Hence no fixed character permutations on at
most three states, with a nontrivial start orbit, take all413 selected lines
from one common start to one common endpoint. This answers the point-action
case explicitly left open by GDT882; it does not equate endpoints with group
products. No language, writing-rule identification or meaning follows.

The reduction is exact: all six permutations of three states are
x -> epsilon*x+b over F3. For fixed signs the line endpoints from0 are linear
in the20 translations b. Rank20 of all line/reference differences forces every
b to zero, so every character fixes0. The endpoint was never required to equal
the start; the result forces that degenerate outcome. A two-state active orbit
can be embedded by fixing a third state and is covered as well.

Source scope is unchanged from882:413 complete all-reading-concordant literal
lines,43 odd physical leaves,20 EVA characters, reference f19r.8. The three
transcriptions are alternate readings. No new source query, even-leaf reveal,
image, visual admission or sealed data was used. Source scope or representation
errors remain limitations on applying the theorem to authorial writing.

The producer completed every mask in2.52seconds of native elapsed time with16
workers; independent validation also completed all masks, with zero missing
masks and zero rank disagreements. Source reconstruction and algebra fixtures
passed. This is a finite exact mechanism exclusion, not a million independent
manuscript observations. The larger-state class remains open; no automatic
extension is selected. Confirmed meanings remain zero.

Protocol and both implementations were public in c4c85285 before execution.
Reproduce with src/run.py and src/validate.py. INPUT.tsv is the unchanged
882 projection; RANKS.bin and INDEPENDENT_RANKS.bin each store one rank byte per
sign mask in fixed numeric order. Their common SHA-256 is
82df21b2451b8f84425bfa137129ade6b39ece9ed9f3086161b366cd1238a4f4.
