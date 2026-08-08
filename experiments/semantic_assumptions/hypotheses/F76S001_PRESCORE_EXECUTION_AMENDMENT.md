# F76S001 prescore execution amendment

Date frozen: 2026-08-09
Status: **FROZEN BEFORE CORRECTED CODE; TARGET REMAINS FORBIDDEN**

This amendment responds only to the four blockers in the independent prescore
audit. It does not alter the target triplet, representation, statistic, gates,
or claim ceiling in the original preregistration.

## 1. Separate provenance bindings

The production runner and validator must bind these as distinct artifacts:

- alignment/source report:
  `results/f76r_keylike_sequence_source_audit.md`, SHA-256
  `27593399b74b00e72cbd939519d324d5ace1c4846b457435263b92a3c3104744`;
- current-locus crosswalk:
  `results/existing_human_current_locus_crosswalk.tsv`, SHA-256
  `4a128ed3d4b87a9d804a336a6c22ced65839fa39c83f3ecf45092bbc64f2eabc`.

The crosswalk is retained only as a provenance dependency. It is not evidence
for the nine f76r pairings.

## 2. Prospective conservative-tie fixture

Before modifying the scorer, freeze a synthetic nine-position panel in which
positions 1, 2, 4, and 9 have identical values in all three structural
channels but distinct surface strings. The other five positions have mutually
distinct channel values. All three alternate-reading panels are identical.

For the target positions 1, 4, and 9, exactly the four three-member subsets of
the four identical positions must tie at the maximum synchronous score.
Therefore the conservative upper tail must contain exactly 4 subsets, the
strictly-greater count must be 0, and the tied-at-target count must be 4. One
control assertion must require all three values. This distinguishes `>=` from
strict `>` without inspecting manuscript target features.

## 3. Exact target-row cardinality and scope

Before feature extraction, both implementations must require exactly one input
row for each of the 27 frozen `(reading, prose locus)` keys. Every such row
must have page `f76r` and grammar scope `CONFIRMED_PROSE`. Missing rows,
duplicate rows, or scope/page drift must stop execution rather than overwrite
one row with another.

## 4. Complete future validation contract

Before numerical reconstruction can pass, the nonimporting validator must:

1. rehash the input, alignment report, crosswalk, original preregistration,
   this amendment, runner, validator, and corrected control result;
2. verify the control artifact's experiment, mode, status, complete binding,
   and passed assertion gate;
3. verify the target artifact's experiment, mode, status, exact nine pairings,
   complete binding, and exact claim ceiling;
4. independently enforce the 27-row cardinality/scope contract; and
5. reconstruct all numerical results, channel deletions, gates, and decision.

The corrected anonymous controls may be run and published. The manuscript
target must remain absent until a new independent prescore audit explicitly
passes these corrections.
