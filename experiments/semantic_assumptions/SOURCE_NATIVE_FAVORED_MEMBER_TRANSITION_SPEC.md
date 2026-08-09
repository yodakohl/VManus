# Exact-member refinement of favored source-family transitions

Status before member-pair inspection: **FROZEN_DESCRIPTIVE_REFINEMENT**

## Capacity and scope

Refine only the six physical family pairs selected by the already frozen
family atlas: `DA`, `AQ`, `QK`, `KJ`, `LJ`, and `PK`. This does not search the
other 570 family pairs. Among their 17,335 physical occurrences, retain only
the 16,876 whose two adjacent STA member codes agree exactly in ZL3b, IT2a,
and RF1b. The readings are alternate transcriptions, so this is a confidence
filter, not three replications.

Frozen exact-event capacities are:

| shell | events | folios | Currier A | Currier B |
|---|---:|---:|---:|---:|
| AQ | 6,361 | 94 | 1,695 | 4,666 |
| DA | 3,519 | 93 | 677 | 2,842 |
| KJ | 2,565 | 92 | 450 | 2,115 |
| LJ | 1,151 | 81 | 175 | 976 |
| PK | 534 | 78 | 119 | 415 |
| QK | 2,746 | 94 | 815 | 1,931 |

## Leave-folio-out member baseline

For each shell, physical folio, and orientation, fit on every other folio a
Dirichlet-.5 baseline for the current exact member code conditioned on shell,
Currier, complete group length, and exact ordinal position, but not the
previous member code. Use the complete official destination-family member
inventory for smoothing. Score held observed and baseline-expected member-pair
counts, context opportunities, folio excess, and Currier-specific effects.

The manuscript view evaluates `left_member -> right_member`; the reversed view
evaluates `right_member -> left_member`. The physical occurrence count must be
identical, and both views must pass the same direction before labeling.

## Frozen classification

A held folio is eligible for a context member with at least three opportunities.
Require at least 10 eligible folios in each orientation.

`FAVORED_MEMBER_PAIR` requires in both orientations:

- observed count >=20 and expected count >=5;
- log observed/expected ratio >=log(2);
- positive held-folio excess in at least 70% of eligible folios;
- each Currier register has >=15 context opportunities, expected count >=2,
  and log ratio >=log(1.2).

`DISFAVORED_MEMBER_PAIR` requires in both orientations:

- expected count >=15 and log ratio <=-log(2);
- negative held-folio excess in at least 70% of eligible folios;
- each Currier register has >=15 context opportunities, expected count >=5,
  and log ratio <=-log(1.2).

All other official within-shell member pairs are `UNRESOLVED`. These are
descriptive decomposition rules, not member-pair p-values or independent
confirmation of 685 candidates.

## Ceiling

A positive result identifies exact all-three-reading member combinations that
carry part of a confirmed neutral family adjacency beyond shell, Currier,
length, exact position, and held folio. It cannot choose the physically correct
fine reading, a spoken direction, sound, letter, syllable, morpheme, prefix,
root, suffix, word, syntax, language, cipher operation, meaning, plaintext, or
translation.
