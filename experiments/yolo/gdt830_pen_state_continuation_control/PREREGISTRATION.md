# GDT830 — artificial-cut continuation control

2026-09-05. Registered before pixel feature extraction or retrieval scoring.
The user authorized continuing the visual production-path proposal. This unit
tests one fixed measurement procedure on selected, apparently continuous rows.
It does not score the disputed f32v/f55v/f82r writing paths, even if it passes.

## Source scope and reference assumption

Only native official JPEGs of already admitted f76r, f77r, f81r and f83r enter.
Their hashes and dimensions are in SOURCES.json. The source reviewer viewed
the native images and selected fixed central row strips by geometry, using
dark-pixel row occupancy only to locate body centers. This was not an ink-state
comparison. ROWS.tsv freezes those strips before feature extraction. They are
not a paragraph-complete or diplomatically word-aligned inventory.

Within each strip, left-to-right spatial continuation is the reference label.
It is not independently observed medieval chronology. Odd numbered source rows
calibrate the nuisance model; even rows are held from calibration. All four
pages must remain represented. No whole folio is withheld, so this is a
within-page detector control, not cross-folio production-model transfer.

## Fixed measurement

Split each strip into twelve equal-width windows, zero indexed. Context is
columns 2 and 3. Columns 4 and 5 are omitted; column 6 is the true spatial
continuation. Thus the comparison is separated by two full windows rather
than touching strokes. Columns 8 and 10 are mandatory same-row decoys. Two
other-row decoys come from column 6 of different held rows on the same page,
matched to the true target using nuisance features only. No ink residual or
retrieval score participates in selection. There is one query per eligible row.

Estimate the local light background with a 15-pixel maximum filter followed by
Gaussian radius 5, within the fixed strip. Foreground has relative mean-RGB
darkness greater than .15. Compare centers of horizontal foreground runs
2–10 pixels wide with at least four of five vertically adjacent foreground
pixels. These are comparable near-vertical stroke elements, not identified
letters. A window requires at least 24 such samples and 40% nonforeground.

Primary ink features are the three median log ratios of estimated background
RGB to sampled ink RGB, using +1 to avoid zero division. These are digital
contrast measurements, not physical ink concentration, age or timestamps.
Width, occupancy, background color/variation/gradients and image position are
nuisance features. Fit a fixed ridge regression of ink on nuisance features
using calibration windows only, with separate page intercepts. Scale residual
ink using calibration residual variability. SPEC.json fixes every parameter.

The primary predictor extrapolates the last two residual ink vectors over
three window steps: r3 + 3*(r3-r2). It ranks the five candidates by negative
mean squared error. Comparators are nuisance similarity, constant residual
ink r3, and the reversed trend r2 + 3*(r2-r3). Tied best candidates receive
fractional credit. A separate three-way evaluation includes only the true
candidate and the two same-row decoys, testing against simple row identity.

## Controls, capacity and decision

Synthetic image fixtures check light-field normalization, recovery of the
registered stroke contrast, and rejection of blank/insufficient windows.
Synthetic descriptor fixtures check that the scorer can recover a planted
trajectory, handles ties, and cannot fit through held-row leakage. These are
instrument checks and do not establish pen physics.

Fixed quality rejection is applied before scores. A held query needs both
context windows, the true window, both same-row decoys and two eligible
other-row decoys. Do not move a failed window or query to another position.
Capacity requires at least 24 calibration rows, 24 held queries, all four
pages, and at least four queries per page. Missing capacity stops the route.

If capacity holds, all of these operational success gates must pass:

- Primary five-way top1 credit at least .40 (equal-choice reference .20).
- At least .10 top1 gain over nuisance and .10 over constant-ink prediction.
- At least .05 gain over reverse-trend prediction.
- Same-row three-way top1 credit at least .50.
- Positive primary-minus-nuisance gain on every page.

These deliberately demand incremental continuation information. They are
fixed operational detector thresholds, not a historical causal significance
test. Geometry-defined labels are not automatically exchangeable, and shared
decoy rows create dependence. No independent-binomial p-value will be claimed.

Status is CONTROL_CAPACITY_STOP, CONTROL_NOT_SUPPORTED, or
CONTROL_LOCAL_CONTINUATION_ONLY. No post-score threshold, feature, column,
page or model change rescues a failure. A software error may be corrected with
an explicit audit; it cannot silently change the scientific question.

## Scope of any conclusion

Even a pass supports only this artificial-cut retrieval task. Spatially
correlated parchment, residual shape effects and within-row execution remain
possible causes. Artificial cuts do not reproduce actual pen lifts, changes
of posture or redipping. Directional prediction is not an independent clock:
the chronological direction was assumed in the control labels. Production
order and intended reading order remain different questions. No split-block
order, transcription change, sound, language, semantic edge or meaning follows.

DIC001 already tested drawing-interruption glyph profiles and is not repeated.
Earlier overdraw chronology studies sought separate physical layers; this
registered control instead concerns measured continuity between separate marks.
The targeted internal duplicate audit found no equivalent trajectory-retrieval
test. No public approach search was performed.

Before registration, synthetic end-to-end review found that a 9-pixel maximum
filter left darkness inside permitted 9–10-pixel strokes. The final 15-pixel
filter was selected to clear the entire registered width band before any
manuscript feature extraction. The control now checks the full width interval.
