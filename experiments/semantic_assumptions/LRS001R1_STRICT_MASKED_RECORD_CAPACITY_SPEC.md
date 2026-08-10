# LRS001-R1 strict masked-record capacity specification

Date frozen: 2026-08-10

## Why this amendment exists

The first score-blind LRS001 capacity pass used donor cells defined only by
page and record length.  A design audit made clear that such cells can mix
editorial code, drawing-interruption state, and record geometry.  A later
positive result could therefore rediscover those states, unordered page/record
vocabulary, or propagated first-order grammar.  No predictor or real
context/target association has been opened.  This versioned correction is made
before calibration and supersedes the first capacity for future execution.

## Fixed target universe

1. Keep complete `CONFIRMED_PROSE` records of 5--12 source-native groups.
2. Only `CORE` groups are possible targets; `FIRST` and `LAST` never are.
3. Learn the target class inventory from TRAIN CORE groups in this universe.
   A complete `family_surface` class must have at least 20 TRAIN occurrences
   on at least 10 TRAIN physical folios.  This retains the previously frozen
   66 classes; no spelling or semantic selection is allowed.
4. The future proper score predicts the exact complete class.  Known target
   `symbol_count` may restrict candidates, but every retained length stratum
   must contain at least two classes.

## Strict donor cell and null

A TEST record is movable only when at least two complete TEST records share
the exact key:

`(page, segment_group_count, code, segment_count, segment_index,
starts_after_drawing, ends_before_drawing, group_count)`.

One null assignment maps one whole donor record to each recipient inside every
cell.  At target ordinal `j`, all context comes from donor ordinal positions
while excluding `j` and `j±1`.  The same donor map is used for every target
ordinal, both model channels, all robustness views, and all source-reading
sensitivities.  Identity permutations are allowed; derangements are never
forced.  TRAIN/CAL fitting is fixed before every TEST assignment.

## Required future comparison

- `NUIS`: metadata; exact position, length, code, drawing and record geometry;
  complete immediate-neighbour 648-block representations; within-target class
  length; and page inventory computed without the entire current record.
- `BAG`: NUIS plus the unordered sum of the same distant group blocks used by
  ORDER.
- `ORDER`: BAG plus only zero-sum position-tagged contrasts of those distant
  blocks.  It may not infer an alignment, choose a field count, or invent
  columns.

The two primary channels are `ORDER - BAG` and `ORDER - NUIS`.  Both must pass
one synchronous two-channel maxT gate.  `BAG - NUIS` is descriptive only.
This is what distinguishes LRS001 from the archived arbitrary-column,
paragraph-ordinal, local-trigram, exact-neighbour, and chained-line routes.

## Capacity gates

- at least 1,500 movable TEST targets in 400 records;
- at least 100 strict cells, 40 pages, and 20 physical folios;
- at least 75% of supported TEST targets remain movable;
- Currier A and B each retain at least 250 targets and 8 folios;
- sections B, H, and S each retain at least 200 targets;
- no physical folio contributes 20% or more of targets;
- all 66 supported classes remain, with at least two classes per symbol count;
- after deleting any record whose complete class sequence occurs in another
  record, at least 1,500 targets on 20 folios remain;
- the exact whole-record permutation space has at least 64 bits.

## Calibration required before target

A separate preregistration must freeze representation, rank/ridge grid,
TRAIN/CAL selection, probability floor, 8,192 TEST assignments, aggregation,
and confirmation gates.  Synthetic controls must yield 0/64 null passes, 8/8
full and 8/8 reduced distributed ordered plants, and 0/8 for every page-topic,
fixed-column, length-by-column, code/drawing, ordered-length-shape,
unordered-bag, pure-first-order-chain, one-folio, one-Currier, one-section,
one-position, one-length, one-surface, exact-duplicate-only, random-donor, and
reversed-mapping family.  Production-free reconstruction is mandatory before
any manuscript association.

## Claim ceiling

A capacity pass says only that this stricter held experiment is possible.  A
later fully gated target pass could say only that ordered nonadjacent content
predicts supported masked complete forms across folios beyond page inventory,
record geometry, immediate neighbours, first-order grammar, and unordered
record content.  It cannot name a field, word, part of speech, sentence role,
recipe, language, sound, cipher, plaintext, or translation.
