# F69LS001 source-surface recovery

Status: `REGISTERED_AFTER_UNSCORED_INPUT_STOP`.

The first invocation of the committed F69LS001 runner stopped before feature
construction, matrix construction, or scoring. No result artifact was written.
The exact blocker was `RF1b|f69v.26|G002`: its manual IVTFF source group is the
extended EVA form `@152;`, so the legacy ASCII-fragment compatibility field is
empty even though the source group is present.

A complete target-panel audit found 100 source group-readings. Ninety-five have
one legacy ASCII fragment, four have multiple fragments because an embedded
extended EVA form was omitted, and one has zero fragments. Therefore a
one-locus substitution is forbidden.

The recovery uses the existing source-preserving alignment table for **all 100
group-readings**:

- `experiments/semantic_assumptions/results/source_sta_group_alignment.tsv`
  SHA-256 `f23654f1d4c854db6d458b418a0d3530115731604854cf0a0495565e58341840`.

Each source-group ID, edition, locus, group index/count, and left/right separator
must agree exactly with `source_separator_transcription.tsv`. The surface value
is the alignment table's `nearest_basic_eva_primary`, which must be a nonempty
lowercase ASCII string. All 100 target rows pass that format condition. This
field applies the repository's source-native STA-to-basic-EVA mapping uniformly;
for example RF `Ba`/`@152;` becomes basic EVA `d`, while preserving the RF
reading as an alternate reading rather than copying ZL or IT.

The feature families, duplicate collapse, support rules, paired-null variance,
two exact 16,384-state nulls, thresholds, gates, and claim ceiling remain
unchanged. One recovery invocation is authorized only after this correction is
committed and public. Because target input was opened during diagnosis, any
positive result remains explicitly recovery-qualified, post-selection, and
one-folio provisional; it is not a translation.
