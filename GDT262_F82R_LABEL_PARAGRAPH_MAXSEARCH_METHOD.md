# GDT262 — f82r label/paragraph max-search method

GDT260 selected f82r.10 from human attachment evidence and found its left
four-member neighborhood concentrated in P2. GDT262 measures how surprising
that result is after the actual page-local search freedom is exposed.

For each of the 13 f82r graphical labels and each reading, concatenate the
label's source-native member sequence and enumerate every distinct contiguous
four-member window. There are 32 windows per reading. Search every window at
Hamming distance at most one inside each f82r prose group. f82r.10 targets its
mechanically following P2; the 12 lower labels target the preceding P3. Each
test receives the same conditional line-level hypergeometric tail used by
GDT260. The page statistic is the minimum tail across all 32 windows.

Two search controls are retained:

1. 100,000 seeded random assignments of the 32 physical lines to paragraph
   blocks of size 9/9/14, with the minimum recomputed over all windows;
2. all 32 circular shifts of every fixed hit mask against the real paragraph
   blocks, preserving physical order, local clustering, and line opportunity.

The first asks whether arbitrary paragraph membership explains the lead. The
second is the stronger page-topology control because nearby lines and their
window opportunities remain together. A 32-test Bonferroni value is reported
as a conservative analytic reference. Alternate readings are sensitivities of
one manuscript.

This is exposed max-search calibration, not confirmation. Only the published
f80r/f82r projection and corrected f82r paragraph coordinate are used. They
contain no f84r row. GDT257 remains disclosed; no new f84r access occurs.
