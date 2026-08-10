# LRS001 source-native masked-record capacity specification

Date frozen: 2026-08-10

## Question

Can a later held experiment test whether the distant fields of one corrected
prose record predict an interior complete source-native group, beyond page
inventory, exact position, length, metadata, and immediate-neighbour grammar?

This file freezes **capacity only**.  It may inspect record geometry, split
membership, and complete STA-family surfaces.  It may not fit a predictor,
open a real context/target association, compute a likelihood gain, or assign a
linguistic or English label.

## Inputs

- `results/drawing_reset_segment_atlas.tsv`
- `results/source_native_within_group_stage_masked.tsv`

The first input contains the corrected source-group records split at unanimous
drawing interruptions.  The second contributes the already frozen physical-
folio `TRAIN`/`CAL`/`TEST` split.  The join key is
`consensus_group_id == unit_id`; it must be one-to-one for every admitted row.

## Fixed capacity universe

1. Keep only `CONFIRMED_PROSE` segments with 5--12 complete source groups.
2. A possible target is a `CORE` group; `FIRST` and `LAST` groups are never
   targets.
3. Learn the target vocabulary from `TRAIN` CORE groups in the same 5--12
   group universe.  A complete `family_surface` is eligible only with at least
   20 TRAIN CORE occurrences on at least 10 TRAIN physical folios.
4. A TEST target is null-movable only when its exact `(page,
   segment_group_count)` cell contains at least two complete records.  The
   future null will permute whole donor-record contexts synchronously inside
   those cells; target identities, pages, lengths, and positions remain fixed.
5. Capacity counts use physical folios, never editions.  ZL3b/IT2a/RF1b are
   alternate readings already collapsed into each consensus group.

## Gates

Capacity passes only if all of the following hold:

- at least 1,500 movable TEST targets;
- at least 400 target-bearing TEST segments;
- at least 40 TEST pages and 20 TEST physical folios;
- at least 250 movable targets in each Currier state A and B;
- at least 250 movable targets in each of sections B, H, and S;
- no physical folio contributes 20% or more of movable targets;
- every eligible target surface occurs in the movable TEST panel;
- the exact within-page/length whole-record permutation space has at least
  64 bits of capacity.

## If capacity passes

Only a separately frozen, target-blind synthetic calibration may follow.  The
future real target must keep the exact eligible-surface list and TEST panel
bound here.  Its added model may see source-native groups at distance at least
two from the target; it must beat both a nuisance baseline and an unordered
distant-context control.  The target and its immediate neighbours may not
enter the added record-schema representation.

## Claim ceiling

A pass establishes only that a fair held masked-record experiment is
possible.  It establishes no reusable record schema, word, part of speech,
recipe field, language, sound, cipher, plaintext, or translation.
