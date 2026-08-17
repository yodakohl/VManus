# GDT185 — f57 R2 to f67v1 17-sector reference alignment

## Question

GDT184 leaves f57v R2 as a fourfold 17-position reference/calibration
sequence.  Independently, the human page inventory describes f67v1 as 17
radial text sectors.  If the R2 sequence is a reusable sign key or index, its
most direct manuscript-internal prediction is that its ordered signs should
recur in the corresponding f67v1 sector texts under one common cyclic phase.

This test assigns no sign value, sound, number, word, or meaning.

## Frozen target and search

- Source: the source-native STA alignment, streamed so that only `f57v.3` and
  `f67v1.13`–`f67v1.29` are retained or parsed.
- R2 key: the first physical 17-position period in each alternate reading.
- Target: the 17 radial loci `f67v1.13`–`.29`, in catalogue order.
- Alternate readings are sensitivities, not replications.
- Search all 17 rotations and both directions.
- Score six fixed views: exact STA code or STA family, each tested anywhere in
  the sector, at its first sign, and at its last sign.
- For every view retain the best of the 34 cyclic alignments.

## Null and decision

Use 65,536 deterministic position permutations per reading.  Each world keeps
the complete R2 sign multiset and every f67v1 sector unchanged, destroying
only their correspondence.  Report inclusive plus-one local tails and a
max-six standardized tail.  A reusable reference alignment requires:

1. max-six `p <= .05` in ZL3b;
2. the same direction and rotation in all three readings; and
3. no alternate-reading local tail above `.10` for the selected view.

Failure closes only this exact f57-R2 to f67v1-sector indexing proposal.  It
does not exclude a page-local reference, ornament, alphabet-like apparatus,
or other target.  f84r is neither retained, parsed, joined, nor scored.
