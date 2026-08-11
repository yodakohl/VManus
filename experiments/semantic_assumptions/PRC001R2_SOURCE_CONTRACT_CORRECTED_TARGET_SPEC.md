# PRC001R2 — source-contract-corrected dark-root marker target

Date: 2026-08-11

Status: `FROZEN_UNSCORED`

## Why one corrected version is permitted

PRC001 stopped before state scoring. Its frozen source contract required
`grammar_scope=LABEL`, while the validated consensus table records these
`kind=L` rows as `grammar_scope=DIAGNOSTIC_NONPROSE`. The runner therefore
constructed zero features, scored zero DARK/LIGHT associations, and evaluated
zero null worlds. That exact stop and its independent reconstruction are bound
below.

The stop also exposed two row-specific source conditions. `STOLFI_BEST_1163`
maps to a locus with `strict_zero_alternative=0`, and
`STOLFI_BEST_1267` maps to a locus absent from the consensus table. PRC001R2
changes only the source contract: it accepts the actual diagnostic-nonprose
label scope and excludes exactly those two source records. No feature,
statistic, threshold, transfer rule, or robustness rule is changed. Because
PRC001 scored no association, this correction is frozen before any target
result exists.

## Question and ceiling

Ask whether one source-native formal feature is recurrently associated with
the inherited human DARK root state across the two mixed held folios and
transfers to both untouched DARK labels on a third folio.

This is not a test for the word *dark*, *root*, a plant name, or a language.
Even a pass establishes only a cross-folio association between a formal label
feature and this small machine-inspected, human-described drawing state.

## Frozen inputs

- `results/pharma_root_color_native_visual_ownership.tsv`, SHA-256
  `eb1b5563fa0d775a662f27b566d9c1acd75eba59fdf690e3fc8ac9ab9e225a7b`;
- `results/pharma_root_color_native_visual_ownership_validation.json`, SHA-256
  `2eb90320045ac0742294f649f73ec4beff00028ca7e94523490af3535d6da03c`;
- `results/source_sta_family_consensus_groups.tsv`, SHA-256
  `a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225`;
- `results/source_sta_family_consensus_validation.json`, SHA-256
  `fcb6a53461b4f9df36f34161ed1d42087f4395988bea0d71f74a7dd635b68b76`;
- `results/prc001_dark_root_marker_target.json`, SHA-256
  `d0b6b0e12bbe4175ce8ba70fcab58f73b5f51bf3a067046cd2cbd9e22a8e5f6b`;
- `results/prc001_dark_root_marker_target_validation.json`, SHA-256
  `52055cee342d2cfaa5bed548c64000d3adbf6eed1243d8c7c4ec268cd6c0eeb0`.

ZL3b, IT2a, and RF1b are alternate readings of one manuscript, never
replications.

## Corrected source reconstruction and frozen capacity

Start from all 21 ownership rows with `eligible=1`. Verify before exclusion:

1. `STOLFI_BEST_1163` has a mapped consensus locus and at least one row with
   `strict_zero_alternative=0`;
2. `STOLFI_BEST_1267` has no row in the consensus table; and
3. no other source record is excluded.

For each of the remaining 19 labels, order all rows at its mapped locus by
integer `consensus_group_index` and require:

1. exact locus uniqueness and one page;
2. `kind=L`, `grammar_scope=DIAGNOSTIC_NONPROSE`, and
   `strict_zero_alternative=1` for every group;
3. indices exactly `1..consensus_group_count`, with the same count on every
   row;
4. nonempty `family_surface` and nonempty ZL/IT/RF STA-code lists; and
5. concatenating the initial character of each reading's STA codes reproduces
   `family_surface` group by group.

Exact member features are created only for groups whose complete ZL/IT/RF
STA-code sequences are byte-identical. A reading disagreement does not remove
family features or the label.

The corrected complete panel is frozen at 19 labels: 17 discovery labels and
two f102 transfer labels. Discovery margins are f89 = 2 DARK / 7 LIGHT and
f100 = 2 DARK / 6 LIGHT. The transfer panel is exactly two DARK f102 labels.
The exact conditional orbit is
`C(9,2) * C(8,2) = 1,008`.

Before any state association is scored, the target-blind reconstruction must
produce exactly 306 unfiltered discovery features and exactly 48 filtered
features. The filtered feature list is sorted by UTF-8 byte order, serialized
as one feature plus LF per row, and has SHA-256
`1691d552609b5651f6f0505795a747bc15c3206486252d8b9f9c134e85dfd65a`.
Any mismatch stops before state scoring.

## Frozen feature universe

Build each label as an ordered list of complete groups. N-grams never cross a
group boundary. Features are binary presence/absence at the physical label.
For each group create, in this exact order:

1. `F:N:n:value` for each distinct contiguous family n-gram, n=1,2,3;
2. `F:P:n:value` and `F:S:n:value` for family prefixes and suffixes, n=1,2,3
   up to group length;
3. `F:W:value` for the complete family surface;
4. `M:N:n:value` for each distinct contiguous all-reading-identical STA-code
   n-gram, n=1,2,3, with codes joined by one ASCII space;
5. `M:P:n:value` and `M:S:n:value` for STA-code prefixes and suffixes,
   n=1,2,3; and
6. `M:W:value` for the complete STA-code sequence joined by one ASCII space.

Items 4--6 are emitted only for a group with byte-identical complete ZL/IT/RF
STA-code sequences. Deduplicate within a label.

The target-blind filter uses only f89/f100 feature presence. Retain a feature
iff it is present in at least three discovery labels and, separately on each
mixed folio, is present in at least one label and absent from at least one.
DARK/LIGHT values and f102 presence may not enter this filter.

## Frozen statistic and exact null

Encode DARK=1 and LIGHT=0. For feature `g` and folio `f`, compute

`delta(g,f) = mean(x_g | DARK,f) - mean(x_g | LIGHT,f)`.

The feature score is `min(delta(g,f89), delta(g,f100))`. The observed winner
maximizes this score. Ties are broken by larger arithmetic mean of the two
deltas, then lexicographically smaller UTF-8 feature string.

Enumerate all 1,008 assignments choosing two DARK labels in f89 and two DARK
labels in f100. Recompute the maximum score over all 48 frozen features in
every world. The inclusive exact p-value is

`count(null_max_score >= observed_max_score) / 1008`.

Use exact Python binary64 comparisons with no tolerance. The observed
assignment is one member of the orbit; no plus-one correction is added.

## Frozen transfer and robustness gates

The result passes only if all gates hold:

1. every corrected source and exact-capacity gate passes;
2. exact max-feature p <= .01;
3. winning score >= .50;
4. both discovery-folio deltas for the winner are >= .50;
5. the frozen winner is present in both f102 transfer labels;
6. after deleting each of the four discovery DARK labels in turn, the already
   frozen winner retains delta >= .50 on both mixed folios; and
7. a nonimporting validator independently reconstructs inputs, exclusions,
   labels, features, all 1,008 maxima, winner, gates, canonical result, and
   canonical report.

The f102 feature sets are constructed only after the discovery winner and all
discovery statistics are fixed. They cannot select or rescue a feature. No
LIGHT-associated reverse analysis, substring tuning, selected reading,
widened feature universe, relaxed support, alternative state coding, or f88
development-folio rescue is permitted.

## Decisions

- Source or exact-capacity failure: `STOP_UNPOWERED_BEFORE_STATE_SCORE`.
- Primary or robustness failure:
  `FINAL_NONCONFIRMATION_NO_RECURRENT_DARK_ASSOCIATED_FORMAL_MARKER`.
- All gates pass:
  `PASS_RECURRENT_FORMAL_FEATURE_ASSOCIATED_WITH_HUMAN_DARK_ROOT_STATE`.

A pass licenses only separately justified inspection of the winning formal
feature's source-native realizations. It does not license the gloss DARK,
ROOT, colour, a plant name, sound, language, cipher, plaintext, or translation.

## Outputs and one-shot rule

The runner writes only:

- `results/prc001r2_dark_root_marker_target.json`;
- `results/prc001r2_dark_root_marker_target_report.md`.

The independent validator writes only the corresponding `_validation.json`
and `_validation.md`. All four paths must be absent before the target run.
Every writer is no-clobber. This specification, runner, validator, exact input
hashes, and output absences must be committed publicly before target access.
