# Source-separator impact audit

## Question

Which claims and descriptive inventories built on the legacy ASCII-cleaner
projection are changed by the complete source-group transcription?

This is a deterministic provenance audit.  It may correct counts and claim
boundaries, but it may not infer a new parse, role, word, or meaning.

## Frozen inputs

- the source-separator transcription atlas and result;
- the legacy pre-grounding interlinear;
- its retained-node residual atlas;
- the one-sided candidate lattice;
- the exact cross-reading spacing inventory;
- the parser-free USR002 exact-`y` capacity table.

All inputs are hash-bound. ZL3b, IT2a, and RF1b remain alternate readings of
one manuscript.

## Deterministic classifications

Each legacy ASCII fragment is mapped to its unique source group and legacy
surface position. A retained formal node is mapped to a legacy position by the
same unique order-preserving whole-fragment alignment used in the coverage
correction.

An omitted legacy fragment is:

- `COMPLETE_SOURCE_GROUP` if its containing source group emits exactly one
  legacy fragment;
- `INTRA_SOURCE_FRAGMENT` if that source group emits two or more fragments.

A formal adjacency is:

- `INTRA_SOURCE_GROUP` when both nodes derive from one source group;
- `ADJACENT_SOURCE_GROUPS` when their groups are consecutive;
- `SKIPS_SOURCE_GROUPS` when one or more source groups intervene.

For adjacent groups, retain the exact IVTFF separator state.  A cross-reading
fusion event is source-safe only when both the separated residual occurrence
and the fused occurrence each belong to a one-fragment source group.  USR002
capacity is source-safe only when all 90 reading-specific target-containing
groups are one-fragment groups whose raw source spelling equals the relevant
legacy token.

## Hard gates

- reconstruct all 15,985 source rows and 115,470 atlas groups;
- reconstruct the exact 3,838 retained-node residual events;
- classify every residual event and every consecutive formal-node adjacency
  exactly once;
- reconstruct all 4,737 registered hard-edge occurrences and their source
  topology/separator state;
- reconstruct all 3,838 candidate-lattice event IDs;
- reconstruct all 312 directed fusion events;
- test all 90 USR002 reading-specific target groups;
- emit only provenance/structural corrections, with zero English glosses.

## Claim ceiling

A pass can distinguish source groups from cleaner fragments, correct affected
counts, and identify source-safe subsets of previous structural evidence.  It
cannot expand special glyph entities, choose authorial spacing, repair the
missing formal parser, assign grammar to an unparsed group, identify a sound or
language, or provide plaintext or translation.
