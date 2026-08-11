# ZCV001 — zodiac clothing-state formal-marker target

Date: 2026-08-12

Status: `FROZEN_UNSCORED`

## Question and ceiling

Ask whether one recurrent source-native formal feature is associated with the
frozen DRESSED rather than UNDRESSED drawing state across four within-page,
within-ring zodiac strata on physical folios f71 and f72.

This is not a word-translation test. Even a pass establishes only an anonymous
formal-feature association with this small source-bound drawing-state panel.
It cannot establish that the feature means *clothed*, *person*, a zodiac name,
or any plaintext word.

## Frozen inputs

- `results/zcv001_zodiac_clothing_state_projection.tsv`, SHA-256
  `d1f74428e16e0674aad9e997df884067f8b778f31927d061b1def0a715c9ad68`;
- `results/zcv001_zodiac_clothing_native_visual_capacity.json`, SHA-256
  `a55b532b57e3c582a5da55ec782bb7f5f6df1eaa7e6b5204b67111dc6c887455`;
- `results/zcv001_zodiac_clothing_native_visual_capacity_validation.json`,
  SHA-256 `b2ce7bc0e1391142fb92954d58423bb573083660322ccc5d04b9c9395b2cbd76`;
- `results/existing_human_current_locus_crosswalk.tsv`, SHA-256
  `4a128ed3d4b87a9d804a336a6c22ced65839fa39c83f3ecf45092bbc64f2eabc`;
- `results/source_sta_family_consensus_groups.tsv`, SHA-256
  `a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225`;
- `results/source_sta_family_consensus_validation.json`, SHA-256
  `fcb6a53461b4f9df36f34161ed1d42087f4395988bea0d71f74a7dd635b68b76`.

ZL3b, IT2a, and RF1b are alternate readings of one manuscript, never
replications.

## Exact source reconstruction

Reconstruct the capacity contract byte-for-byte. Exactly 35 projected records
must yield exactly 33 strict labels and exclude only `STOLFI_BEST_0599` and
`STOLFI_BEST_0601`, both for absent consensus loci. The strict panel must be:

- f71r INNER: 4 DRESSED / 1 UNDRESSED;
- f71v OUTER: 7 DRESSED / 2 UNDRESSED / 1 UNCERTAIN;
- f72r1 INNER: 1 DRESSED / 3 UNDRESSED / 1 UNCERTAIN;
- f72r2 OUTER: 2 DRESSED / 9 UNDRESSED / 2 UNCERTAIN.

Order each stratum by integer Grove number. No state, row, page, or uncertainty
may be dropped after this freeze.

## Frozen feature universe

Reconstruct the PRC001R2 family/member n-gram, prefix, suffix, and whole-group
binary features. N-grams never cross a consensus-group boundary. Member
features are emitted only when the complete ZL/IT/RF STA-code sequences are
byte-identical.

The target-blind filter knows only strict label membership and page-by-ring
strata. Retain a feature iff it occurs in at least four strict labels and is
present and absent in every stratum. The unfiltered universe must contain 398
features. The 37 retained feature strings, sorted by UTF-8 byte order and
serialized as one feature plus LF, must have SHA-256
`e395dd0228fb8ad018dce53a5089892cec02af0267ce5751be556e03c269f05e`.
Any mismatch stops before state scoring.

## Statistic

For feature `g` in stratum `s`, ignoring UNCERTAIN rows, compute

`delta(g,s) = mean(1[g present] | DRESSED,s) - mean(1[g present] | UNDRESSED,s)`.

The f71 effect is the arithmetic mean of f71r INNER and f71v OUTER deltas. The
f72 effect is the arithmetic mean of f72r1 INNER and f72r2 OUTER deltas. The
feature score is the minimum of the two physical-folio effects.

The winner maximizes that score. Ties are broken by the larger arithmetic mean
of the two folio effects, then the lexicographically smaller UTF-8 feature
string.

## Exact cyclic max-feature null

For each stratum, retain the ordered complete state vector, including
UNCERTAIN. Independently rotate that complete vector over the fixed ordered
label-feature rows. No state is independently shuffled and no uncertainty is
discarded. The four rotation counts are 5, 10, 5, and 13, giving exactly 3,250
worlds. Rotation zero in every stratum is the observed world.

In every world, recompute all 37 feature scores and retain their maximum. The
inclusive exact max-feature p-value is

`count(null_maximum >= observed_winning_score) / 3250`.

Use Python binary64 comparisons with no tolerance and no plus-one correction.

## Frozen gates

All gates must pass:

1. every source, count, feature, and 3,250-world capacity invariant passes;
2. exact max-feature p <= .01;
3. winning score >= .50;
4. both physical-folio effects are >= .50;
5. every one of the four stratum deltas is >= .25;
6. the winner is present in at least four f71 DRESSED labels and at least two
   f72 DRESSED labels;
7. after excluding the two MEDIUM-confidence native UNDRESSED grades, the
   already frozen winner retains f72 effect >= .40; and
8. a nonimporting validator independently reconstructs every input, strict
   label, feature, rotation world, null maximum, gate, canonical result, and
   exact report.

No reverse UNDRESSED marker, alternative support filter, selected reading,
state regrading, ring deletion, substring tuning, or threshold change is
permitted after target access.

## Decisions

- Source or capacity mismatch:
  `STOP_UNPOWERED_BEFORE_CLOTHING_ASSOCIATION_SCORE`.
- Any substantive or robustness gate fails:
  `FINAL_NONCONFIRMATION_NO_RECURRENT_CLOTHING_ASSOCIATED_FORMAL_MARKER`.
- All gates pass:
  `PASS_RECURRENT_FORMAL_FEATURE_ASSOCIATED_WITH_CLOTHING_STATE`.

A pass licenses only separately justified inspection of the frozen winning
formal feature. It does not license a clothing gloss, zodiac name, sound,
language, cipher, plaintext, meaning, or translation.

## One-shot outputs

The runner writes only:

- `results/zcv001_zodiac_clothing_formal_marker_target.json`;
- `results/zcv001_zodiac_clothing_formal_marker_target_report.md`.

The independent validator writes only the corresponding `_validation.json`
and `_validation.md`. All four paths must be absent when this specification,
runner, validator, and exact hashes are first published. Every writer is
no-clobber.
