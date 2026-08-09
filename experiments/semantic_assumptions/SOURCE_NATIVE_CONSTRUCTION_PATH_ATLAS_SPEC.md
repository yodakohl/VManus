# Source-native construction-path atlas

Status: **FROZEN_DESCRIPTIVE_COMPOSITION**

This atlas combines, without refitting, the confirmed exact-position local
transition grammar with the strict all-reading source-family prose groups. It
does not search for new favored edges. The favored directed graph is fixed as
`DA`, `AQ`, `QK`, `KJ`, `PK`, and `LJ`; the 52 disfavored edges are read from
the already validated transition atlas.

For every one of the 21,899 strict confirmed-prose groups, the builder shall:

- classify each physical adjacent family pair as favored, disfavored, or
  unresolved;
- split the group into maximal contiguous favored runs of at least two
  symbols;
- enumerate every graph-valid contiguous subpath of length at least two;
- record only aggregate path counts, distinct groups/loci/folios, Currier and
  section counts, and exclusive `WHOLE/OPENING/CLOSING/INTERNAL` positions;
- label a path `WIDESPREAD_BOTH_REGISTERS` only when it occurs in at least 20
  physical loci, 20 folios, and at least 10 groups in each Currier register.

The result must report total transition and symbol coverage, the number of
groups containing any favored edge, the number wholly composed of one favored
path, and the maximal-run length distribution. A clean-room implementation
must reconstruct the source join, all 13 possible graph paths, every aggregate
row, and output bytes.

This is a neutral finite-state construction inventory. It may identify reusable
opening, closing, whole-group, or internal path shapes. It cannot establish
reading direction, wordhood, morphemes, syntax names, sound, language, cipher
operation, meaning, plaintext, or translation.
