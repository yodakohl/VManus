# GDT369 pre-score ordinal correction

The first freeze commit enumerated adjacency using the inherited TSV row order.
That table is lexicographically sorted by locus, so loci such as `.10` and
`.11` precede `.6`; it is not physical array order.

Before any GDT369 score was computed, the freeze was corrected to sort every
array by the explicit integer `ordinal`. The corrected exact orbit sizes are
2,080 for major-body count, 2,880 for terminal-arm count, and 120 for hue. The
superseded 1,040/8,640/120 freeze remains in git history. No result depends on
the erroneous ordering.
