# GDT865: whole-leaf exclusion of the two published primary models

GDT858 found that 855 of the 963 GDT808 CORE13 primary folds retained training
examples from the opposite face of the held leaf. This is a new, explicitly
chosen falsifier of the positive primary threshold claim, not a rerun of a failed
semantic route. GDT858 did not measure its effect. We now measure that effect.

## Frozen comparison

Reconstruct GDT808 ALL28 events first so the original event IDs are retained;
select its unchanged CORE13 set (1777 events) and its two EXACT primary models
M01_L_TO_L and M02_DY_TO_DY. Keep the original event definitions, labels, source
scope, Q152 mask, full-corpus ending-class catalogue, paragraph contexts, feature
definitions, alpha=0.5, carrier-by-class weights and scoring. The old feature
vocabulary still requires two training carriers and two training page faces.
The original three-folio cohort eligibility also meant page faces: no claim of
three-leaf eligibility is introduced. Do not modify physical_folio globally.

For each original (held carrier, held page face) test group, compare original
training exclusion with training exclusion of that carrier and the whole held
physical leaf (page prefix matching ^(f[0-9]+)). No test events are removed or
regrouped. Rebuild all training-dependent vocabularies, counts, weights and
smoothing denominators. Original paragraph contexts are confined to their page;
verify this property in reconstruction. All 963 new folds must retain both
classes and all 12 non-held carriers, with zero held-carrier or held-leaf training
overlap. Capacity failure stops the comparison; do not drop inconvenient folds.

Before accepting corrected predictions, reproduce every old published score and
known-feature count for these two models, plus the original feature hashes and
event metadata. All 108 folds with no opposite-face training must have exactly
unchanged serialized predictions. Any failure is an implementation stop, not a
scientific negative result. Preserve old source bytes and original artifacts.

## Outputs and decisions

Publish paired event predictions, fold membership/count audits, all eight
original score-channel metrics and per-carrier paired changes. For each axis,
PRIMARY_THRESHOLD_SURVIVES_WHOLE_LEAF_EXCLUSION means nuisance carrier-macro AUC
at least 0.60 and at least 9 of the 13 carrier AUCs strictly above 0.50. Otherwise
report PRIMARY_THRESHOLD_NOT_RETAINED. This tests only these two original
primary thresholds. It is not the full original PORTABLE_RECORD verdict, which
also depended on ALL28 sensitivity and refitted nulls that are outside this test.

Report descriptive leave-one-test-leaf-out ranges of nuisance, augmented and
slot metrics and paired differences, without refitting. These are sensitivity
ranges, not confidence intervals or independent replications. Carrier-wise and
leaf-wise dependencies remain; do not recycle old null ranks or claim new
statistical significance. Report changes even if both thresholds survive.
Reduced performance could reflect less training data as well as removal of
opposite-face dependence; the difference is not a causal leakage estimate.

This is retrospective robustness of a previously observed cohort and feature
catalogue, not untouched prospective validation. No translation, semantic
operator, authorial relation or new GDT388 packet is established. No ALL28 fits,
cross-axis fits, ED1 variants, label nulls, hyperparameter tuning, renderer edits
or automatic model rescue. A surviving result supports only transfer of these
structural statistical patterns beyond a physical leaf. A lost threshold
withdraws that stronger transfer claim for the affected axis.

## Execution and audit

Read mixed TSV sources only through selector-first guarded queries with the
fixed 179 allowed selectors and explicit columns; f84 and f84r remain sealed.
Use at most 32 CPU workers and no external model service. Publicly freeze this
protocol and executable source before any new target read or fit. Independently
validate coverage, source parity, fold exclusions, unchanged-fold parity and AUC
decisions. Total work budget: 08:55–09:35 UTC, including feasibility, source work, checks
and publication. Before fitting, reassess code readiness and remaining time.
Review measured runtime after 20 minutes of fitting or at 09:35 UTC, whichever
comes first; interruption
means incomplete, never a favourable or unfavourable result. No GPU is required
for these small count models. Publish compact reproducible outputs after staged
privacy gates; keep any bulky event cache under ignored runtime.
