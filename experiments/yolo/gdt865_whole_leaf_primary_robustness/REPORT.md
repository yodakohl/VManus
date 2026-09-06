# GDT865: both primary thresholds survive whole-leaf exclusion

**COMPLETE_PRIMARY_WHOLE_LEAF_ROBUSTNESS_AUDIT.** Both unchanged CORE13 primary
models retain their predeclared nuisance-score thresholds after excluding all
training material from the held physical leaf as well as the held carrier.
This strengthens the specific structural transfer finding beyond the previously
used page-face holdout. It does not establish a translation or reproduce the
full original GDT808 verdict, which required further controls outside this test.

| Primary variation | Old nuisance macro AUC | Whole-leaf nuisance macro AUC | Paired change | Carriers above 0.50 |
|---|---:|---:|---:|---:|
| L: ol / eol | 0.611534 | 0.616364 | +0.004830 | 10/13 |
| DY: edy / eody | 0.753049 | 0.750323 | -0.002726 | 11/13 |

AUC is ranking discrimination, not percentage transcription or translation
accuracy. The fixed threshold was nuisance carrier-macro AUC at least0.60 and
at least9/13carrier AUCs strictly above0.50. Here nuisance is the original sum
of topic, line-template and form/regime scores; it is not a semantic predictor.

## What changed, and what remained fixed

The 1777 test events, their 963 original carrier/page-face test groups, labels,
feature definitions, Q152 masking, full-corpus ending catalogue, feature-support
gates, smoothing and weighting all remain unchanged. Training membership changes
in855folds:505/569L and350/394DY. The108unaffected folds have exactly unchanged
serialized predictions. All963whole-leaf folds retain both classes and all12
non-held carriers. Their ordered training memberships are independently
reconstructed and checked by digest; test coverage is exactly once per event.

The old baseline matches all1777published prediction rows, including all25score
and known-feature fields, and all1777event metadata/feature-hash records. The
original paragraph feature contexts remain confined to each event's page.
The strict source allow-lists agree, and raw mixed sources were read only through
selector-first guarded queries. No scope or visual admission changed.

## Local context remains a small additional contribution

| Variation | Whole-leaf augmented AUC | Whole-leaf local-only AUC | Old augmented-minus-nuisance | New augmented-minus-nuisance |
|---|---:|---:|---:|---:|
| L | 0.617431 | 0.541764 | 0.005609 | 0.001067 |
| DY | 0.763678 | 0.620007 | 0.016854 | 0.013356 |

The added local-context gains are smaller after the exclusion. This is a
measured descriptive comparison, not proof that local context has no role.
No old null ranks or full local-operator verdict are transferred to these fits.

Removing one test leaf at a time from metric calculation, without refitting,
yields nuisance AUC ranges0.603737–0.630188 across89L test leaves and
0.734283–0.767415 across51DY test leaves. The corresponding positive-carrier
counts range9–12 and11–12. These are sensitivity ranges, not confidence
intervals; the folds, carriers and leave-one-leaf summaries are dependent.
All eight original channels, paired per-carrier changes and every deletion are
retained in the compact result artifacts.

## Validation, runtime and limits

Public preregistration/source commit3c5c7212 was confirmed at09:11:28UTC before
new guarded target reads or fits. The paired runner took25.245seconds using16CPU
workers. It reused the baseline bundle for unchanged training memberships in108
folds; the independent validator separately refitted the four primary decks in
all963whole-leaf folds, including those108, and passed. Its rank-sum AUC,
source-parity, coverage, exclusion, capacity and decision checks also passed.
The cached metric replay is a separate arithmetic check, not a further model fit.

The total work budget was08:55–09:35UTC including feasibility, programming,
source preparation, validation and publication. By09:13:28UTC both paired fits
and the independent full four-deck refit had finished. Total publication timing
is recorded in the session log; computation time is not total task time.

This retrospective comparison preserves cohort and catalogue choices made on
previously observed data. Excluding another page also removes training examples;
score changes do not isolate a causal leakage effect. There are no new refitted
nulls, ALL28 sensitivity fits, independent semantic bindings or GDT388 relation
packets. Confirmed translated lexemes remain0. The specific stronger primary
threshold claim is supported; no automatic model or semantic follow-up follows.

Reproduce with the manifest run command, then
`python3 experiments/yolo/gdt865_whole_leaf_primary_robustness/src/validate.py --refit --workers 16`.
Default validation uses public artifacts and guarded original projections; the
optional independent refit uses feature arrays rebuilt by the run under ignored
runtime. Original GDT808 source bytes are unchanged. Task staged privacy/scope
checks pass; unrelated pre-existing GDT600 binding and historical TSV-index debt
remain outside this result.
