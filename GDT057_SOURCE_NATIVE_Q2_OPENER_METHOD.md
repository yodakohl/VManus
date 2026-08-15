# GDT057 — source-native Q2 probabilistic line opener

## Question

Does the source-native STA member class `Q2` occur at the first physical group
of a line more often than expected from its distribution within that same
line? This tests a formal coordinate, not a word, morpheme, sound, punctuation
mark, grammatical category, or meaning.

## Frozen inventory and exclusions

- Start from `gdt016_group_state_inventory.tsv` and retain only complete
  physical lines.
- Join groups to the synchronized source-native family-consensus table.
- Retain a line only when the first STA member of every group agrees in ZL3b,
  IT2a, and RF1b. The editions are alternate readings, not replications.
- Skip f84r before parsing or retaining source-native fields. It remains
  sealed and is not opened, queried, joined, or scored.

## Exact test

For every stable first-member class with at least 20 group occurrences, fix
the observed number of occurrences in each line and permute their group
positions exactly within that line. The probability of occupying the single
line-initial position is hypergeometric. Convolve the per-line distributions,
report the inclusive upper-tail probability, and Bonferroni-correct across all
supported first-member classes.

Report precision (fraction of member occurrences that are line-initial),
endpoint recall (fraction of complete lines beginning with the member),
register-specific effects, and the minimum effect after deleting each physical
folio. A positive result establishes only a transferable probabilistic line
opener class.

## Relationship to GDT046

GDT046 tested whether Q2-open lines preferentially pair with B3 endings. That
paired frame was weak after its opener-class max-search. GDT057 asks the prior
and logically separate question whether Q2 itself is enriched at line entry.
The two outcomes must not be conflated: a strong Q2 opener effect does not make
Q2+B3 a mandatory or confirmed frame.
