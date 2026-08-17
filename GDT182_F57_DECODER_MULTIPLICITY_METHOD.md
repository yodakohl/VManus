# GDT182 — f57 local-decoder multiplicity audit

## Question

GDT179 found a perfect exposed two-coordinate reading for each four-label f57
register, and GDT180 reused one register's state coding on f77.  With only four
positions, however, a pair of shallow binary string predicates can often make
a complete 2×2 grid.  GDT182 asks whether the selected shared terminal-`y`
axis is unusual after enumerating the full simple feature family actually
available to the exposed search.

This is a falsification audit of the active YOLO theory, not a new semantic
fit.  It does not change the source-frozen W.73 phase or the observed f77
topology.

## Input and feature family

The only target data are the eight already published rows of
`gdt179_quality_decoder.tsv`.  For each register and each alternate reading,
the scorer expands bracketed alternatives, treats uncertain or manual
separators as substring barriers, and enumerates:

- literal prefix predicates of length 1--3;
- literal suffix predicates of length 1--3;
- within-segment substring predicates of length 1--3.

A predicate is true for a locus only if it is true in every expansion of all
three readings.  Constant predicates are removed.  Predicates with identical
four-position masks remain aliases of one effective binary coordinate.

A mask pair is a complete decoder when its two bits distinguish all four
positions.  The audit counts all such pairs and identifies the GDT179 choices.

## Register-alignment null

The N1 position order is held fixed.  The four D1 labels are permuted across
the four positions in all 24 exact worlds while every label's features remain
unchanged.  For each world the scorer asks whether any literal predicate name
common to both registers obtains the same nonconstant four-position mask in
both.  This is the search-adjusted diagnostic because terminal `y` was selected
after the labels and positions were exposed.

The narrower `END1:y` tail is also reported descriptively, but it is not the
primary evidence.

## Decision

The local state reading remains a useful generative scaffold only if reported
with the decoder multiplicity.  It is not promoted if the observed shared-axis
alignment lies in more than 5% of the exact worlds after searching the common
literal feature family.

No global `ot`, `ok`, or `y` value is tested.  No prose, image, new page, or
f84r material is accessed.
