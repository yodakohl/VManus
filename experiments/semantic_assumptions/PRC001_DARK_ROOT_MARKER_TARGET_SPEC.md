# PRC001 — held dark-root marker target

Date: 2026-08-11

Status: `FROZEN_UNSCORED`

## Question and ceiling

Ask whether one source-native formal feature of the now ownership-secure
pharmaceutical labels is recurrently associated with the inherited human DARK
root state across the two mixed held folios and transfers to both untouched
DARK labels on a third folio.

This is not a test for the word *dark*, *root*, a plant name, or a language.
Even a pass establishes only a cross-folio association between a formal label
feature and this small human-described drawing state. The label may identify a
plant or another property correlated with root colour.

## Frozen inputs

- `results/pharma_root_color_native_visual_ownership.tsv`, SHA-256
  `eb1b5563fa0d775a662f27b566d9c1acd75eba59fdf690e3fc8ac9ab9e225a7b`;
- `results/pharma_root_color_native_visual_ownership_validation.json`, SHA-256
  `2eb90320045ac0742294f649f73ec4beff00028ca7e94523490af3535d6da03c`;
- `results/source_sta_family_consensus_groups.tsv`, SHA-256
  `a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225`;
- `results/source_sta_family_consensus_validation.json`, SHA-256
  `fcb6a53461b4f9df36f34161ed1d42087f4395988bea0d71f74a7dd635b68b76`.

The ownership panel contains no Voynich string. No target locus in the family
table was inspected while this specification was written.

Use the 21 rows with `eligible=1`. The mixed discovery panel is f89 (2 DARK,
9 LIGHT) plus f100 (2 DARK, 6 LIGHT). The exact conditional orbit has
`C(11,2) * C(8,2) = 1,540` assignments. The two f102 DARK rows are a sealed
directional transfer panel and must not affect feature construction, filtering,
selection, or tie-breaking.

ZL3b, IT2a, and RF1b are alternate readings, never replications.

## Target-source reconstruction and capacity stop

For each eligible mapped locus, load all rows from the consensus table, order
by integer `consensus_group_index`, and require:

1. exact locus uniqueness and one page;
2. `kind=L`, `grammar_scope=LABEL`, and `strict_zero_alternative=1` for every
   group;
3. indices exactly `1..consensus_group_count` with the same count on every row;
4. nonempty `family_surface` and nonempty ZL/IT/RF STA-code lists;
5. concatenating the initial character of each reading's STA codes reproduces
   `family_surface` group by group; and
6. every reading's code-initial sequence reproduces the same frozen family
   surface. Exact member features are created only for groups whose complete
   ZL/IT/RF STA-code sequences are byte-identical; a reading disagreement does
   not remove the family features or the label.

STOP_UNPOWERED before state scoring if any eligible label fails, if the mixed
panel is not exactly 19 labels with margins 2/9 and 2/6, if the transfer panel
is not exactly two DARK f102 labels, if the exact orbit is not 1,540, or if the
unsupervised feature filter below retains fewer than four features.

## Frozen feature universe

Build each label as an ordered list of complete groups. N-grams never cross a
group boundary. A feature is binary presence/absence at the physical label.

For each group create, in this exact order:

1. `F:N:n:value` for every distinct contiguous family n-gram, n=1,2,3;
2. `F:P:n:value` and `F:S:n:value` for family prefixes and suffixes, n=1,2,3
   up to group length;
3. `F:W:value` for the complete family surface;
4. `M:N:n:value` for every distinct contiguous all-reading-identical STA-code
   n-gram, n=1,2,3, codes joined by one ASCII space;
5. `M:P:n:value` and `M:S:n:value` for STA-code prefixes and suffixes, n=1,2,3;
6. `M:W:value` for the complete STA-code sequence joined by one ASCII space.

Items 4--6 are emitted only for a group with byte-identical complete ZL/IT/RF
STA-code sequences.

Deduplicate within a label. Candidate feature order is lexicographic UTF-8 byte
order over the complete feature string.

The filter is target-blind and uses only f89/f100 feature presence. Retain a
feature iff it is present in at least three discovery labels and, separately
on each mixed folio, is present in at least one label and absent from at least
one label. DARK/LIGHT values and f102 feature presence may not enter this
filter.

## Frozen statistic and exact null

Encode DARK=1 and LIGHT=0. For feature `g` and folio `f`, compute

`delta(g,f) = mean(x_g | DARK,f) - mean(x_g | LIGHT,f)`.

The feature score is

`score(g) = min(delta(g,f89), delta(g,f100))`.

The observed winner maximizes this score. Ties are broken by larger arithmetic
mean of the two deltas, then lexicographically smaller UTF-8 feature string.
The primary statistic is the winning score.

Enumerate all 1,540 assignments obtained by choosing two DARK labels in f89
and two DARK labels in f100, preserving every label feature and both folio
margins. Recompute the maximum score over the complete frozen filtered feature
set in every world. The inclusive exact p-value is

`count(null_max_score >= observed_max_score) / 1540`.

Binary64 arithmetic is sufficient because all means have denominators
2, 9, 2, or 6. Comparisons use exact Python binary64 values with no tolerance.
The observed assignment is one member of the orbit; no plus-one correction is
added.

## Frozen transfer and robustness gates

The result passes only if all gates hold:

1. all capacity gates pass;
2. exact max-feature p <= .01;
3. winning score >= .50;
4. both discovery-folio deltas for the winner are >= .50;
5. the frozen winner is present in both f102 transfer labels;
6. after deleting each one of the four discovery DARK labels in turn, the
   already frozen winner retains delta >= .50 on both mixed folios (the affected
   folio then has one DARK label); and
7. the result and a nonimporting validator agree on inputs, labels, features,
   all 1,540 maxima, winner, gates, and canonical report.

The transfer panel is opened only after the discovery winner and all discovery
statistics are fixed in memory. It is never used to rescue or select a feature.
No LIGHT-associated reverse analysis, selected substring length, selected
reading, widened feature universe, relaxed support, alternative root-state
coding, or f88 development-folio rescue is permitted after unsealing.

## Decisions

- Capacity failure: `STOP_UNPOWERED_BEFORE_STATE_SCORE`.
- Primary or robustness failure:
  `FINAL_NONCONFIRMATION_NO_RECURRENT_DARK_ASSOCIATED_FORMAL_MARKER`.
- All gates pass:
  `PASS_RECURRENT_FORMAL_FEATURE_ASSOCIATED_WITH_HUMAN_DARK_ROOT_STATE`.

A pass licenses a later, separately justified inspection of the winning formal
feature's exact source-native realizations. It does not license the gloss DARK,
ROOT, colour, a plant name, a sound value, language, cipher, plaintext, or
translation.

## Outputs and one-shot rule

The runner will write only:

- `results/prc001_dark_root_marker_target.json`;
- `results/prc001_dark_root_marker_target_report.md`.

An independent validator will write only the corresponding `_validation.json`
and `_validation.md`. All four paths must be absent before the target run. Every
writer is no-clobber. The specification, runner, validator, input hashes, and
output absences must be committed publicly before the target is opened.
