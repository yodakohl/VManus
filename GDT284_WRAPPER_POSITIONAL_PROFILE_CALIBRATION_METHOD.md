# GDT284 — wrapper positional-profile architecture calibration

## Question

GDT283 found a transferable but opaque Voynich wrapper/host form channel.  In
the standard held-folio endpoint the gain was positive at host `INITIAL` and
`INTERNAL` characters but negative at `FINAL` and `EOS`; three Latin
diplomatic controls were positive at all four positions.  GDT284 asks whether
that positional fingerprint is reproduced by any already-frozen known
architecture.

This is calibration, not a new Voynich model.  GDT283 and every control world
are byte-frozen.  No semantic field, PAGE_HOST substring, threshold, parser,
or synthetic encoder is selected or changed here.

## Frozen panels

Use the 8,448-event native observation panels already published by GDT278:

- ordinary Nuremberg expanded text;
- Nuremberg diplomatic abbreviation;
- held-book MAP and sampled learned-abbreviation outputs;
- Augsburg structured accounts;
- GDT172 lexical codebook A;
- GDT172 factorial technical notation B;
- GDT173 human-grown distributed notation B2;
- the three GDT283 Latin diplomatic anchors; and
- the Voynich reference.

Architecture labels come only from `gdt278_control_manifest.tsv`.  Oracle
fields are not scored.  All panels have equal event counts, so no
renormalization or matching to Voynich is performed.

## Frozen instrument

Reproduce GDT283 exactly:

1. the no-wrapper and full eight-class wrapper contexts;
2. held-physical-folio scoring;
3. `INITIAL`, `INTERNAL`, `FINAL`, and `EOS` codelength components;
4. the nested eight-bucket test that excludes all training occurrences of
   every exact host identity in the target bucket; and
5. 64 wrapper permutations within exact
   `section × Currier × hand × within-field position × host length × first
   host character` strata.

The host bucket and permutation seed families are unchanged from GDT283.
Apply the shared-world maximum statistic across all twelve panels as a
calibration diagnostic.  Alternate readings are not independent samples.

## Frozen fingerprint comparison

For each panel and for both standard and nested modes, report:

- the four signed component gains in bits/event;
- `ONSET_BODY = INITIAL + INTERNAL`;
- `TERMINAL = FINAL + EOS`;
- total gain;
- the exact four-component sign pattern, where zero is its own state;
- component rank from greatest to least gain; and
- unscaled Euclidean distance from the corresponding Voynich four-vector.

The distance is a predeclared descriptive coordinate, not an optimized
classifier or composite evidence score.  Rank the controls by that distance.

## Frozen decision

Use the standard fingerprint for the architecture classification:

- `VOYNICH_POSITIONAL_PROFILE_NOT_ARCHITECTURE_SPECIFIC` if the exact Voynich
  sign pattern occurs in at least two independently labelled non-Voynich
  architecture categories;
- `VOYNICH_POSITIONAL_PROFILE_CATEGORY_LOCAL` if it occurs in one category
  only; or
- `VOYNICH_POSITIONAL_PROFILE_DISTINCT_IN_CURRENT_CONTROLS` if no control
  reproduces it.

The nested fingerprint, null p-values, nearest controls, and component ranks
are mandatory sensitivities and cannot change that frozen label.  A distinct
profile identifies only a residual coordinate missing from this finite
control panel; it does not identify a language or notation architecture.

## Claim ceiling and seal

At most this experiment says whether the opaque wrapper-conditioned character
gain has a positional profile represented among the current frozen controls.
It cannot establish morphology, abbreviation, lexical identity, function,
sound, language, meaning, plaintext, or translation.

Only the already-published f84-free native inventory is read.  No f84 row may
be opened, parsed, retained, joined, or scored.
