# GDT1148 — immediate context does not recover a portable ain/aiin choice

**Registered result: NO_JOINT_TRANSFER.** Both BARE and NONBARE are NO_MATERIAL_TRANSFER. Every stratum meets the declared occurrence/leaf capacity, but the complete-neighbour predictor fails the predeclared0.01-nat physical-leaf-average improvement in both primary readings. This is an actual executed crossed prediction, not a new guessed glossary. It is not a refutation of aiin morphology, quantity, grammatical marking or longer context.

## What was predicted before evaluation

For every eligible occurrence, predict the exact choice between `prefix+ain` and `prefix+aiin`, training without ANY occurrence of that orthographic prefix and without ANY leaf in its physical-leaf modulo5fold. Both recto/verso and all panels are grouped. Bare `ain`/`aiin` are an entirely separate withheld prefix. The alternative form need not itself occur for this prefix; all eligible events are retained. The two alternatives are supplied by the registered family definition, not discovered plaintext.

All family neighbours matching `.*ai+n` are masked; only definite-space, same-line, pure-letter immediate whole neighbours enter. Baseline B uses physical position, section, Currier and hand; L/R add separate exact neighbour counts and C averages them. Fixed shrinkage20, no optimisation or post-result repair. Context support must come from different prefixes and other folds. GDT802 supplied this instrument for l/m; new target is ain/aiin, not a new generic holdout method. GDT999 failed its specific ykar frame;1047 assessed host existence; neither is rerun or overwritten.

## Complete inventory

Counts below are occurrences in the179-selector P-prose snapshots, not the whole manuscript. No reader pooling or uncertain-spelling correction.

|Reading|Bare ain|Bare aiin|Bound ain|Bound aiin|All aiiin, separate unscored stratum|
|---|---:|---:|---:|---:|---:|
|ZL3b|100|422|1435|2914|103|
|IT2a|82|389|1506|2971|99|
|RF1b|110|436|1333|2677|98|

There are14,375 binary reader-events plus300 separate aiiin events. These are alternate readings of the same manuscript. No arithmetic value is assigned to one/two/three minims. Nonbare residual prefixes number504/542/508 across both tails, not504/542/508 established lexical stems. The raw prefix and full form are retained.

## Actual out-of-training predictions

Gains are natural-log loss reduction versus B; positive is better. Primary is equal physical-leaf weighting.

|Reading / stratum|Events|Leaves|Left gain|Right gain|Combined gain|Required combined gain|
|---|---:|---:|---:|---:|---:|---:|
|ZL3b / BARE|522|65|+0.001986|+0.001428|+0.001951|+0.010000|
|ZL3b / NONBARE|4349|90|+0.000220|-0.001061|-0.000049|+0.010000|
|IT2a / BARE|471|64|+0.002695|-0.000841|+0.001210|+0.010000|
|IT2a / NONBARE|4477|90|+0.001374|+0.000737|+0.001434|+0.010000|
|RF1b / BARE|546|67|+0.000779|+0.002914|+0.002101|+0.010000|
|RF1b / NONBARE|4010|89|+0.001924|-0.000629|+0.000965|+0.010000|

|Reading / stratum|Baseline exact-choice accuracy|Combined accuracy|Left context with training support|Right context with training support|
|---|---:|---:|---:|---:|
|ZL3b / BARE|78.93%|78.93%|79/522|170/522|
|ZL3b / NONBARE|65.67%|65.65%|1075/4349|1623/4349|
|IT2a / BARE|79.62%|79.41%|133/471|152/471|
|IT2a / NONBARE|65.16%|65.11%|1232/4477|1707/4477|
|RF1b / BARE|75.82%|76.01%|113/546|161/546|
|RF1b / NONBARE|65.81%|65.96%|914/4010|1326/4010|

Bare-form exact choice is largely explained by its strong aiin frequency imbalance; high raw accuracy is not semantic success. The small positive leaf-average bare gains coexist with negative event-average gains in ZL/IT (−0.000926/−0.000660): weighting matters and both are retained. No side is consistently selected across readings.

## Limits that matter

Exact full-word context support is sparse after crossed exclusion and echo masking. Many cases necessarily use the baseline fallback. Passing the registered occurrence/leaf capacity does not make every neighbour cell well supported. This test therefore rejects selection of this particular sparse predictor as a shared functional rule; it does not show no context information exists. It neither resolves attachment nor compares conjunction, article, number and suffix semantics. Immediate adjacent words are not independently identified syntactic arguments. The result supplies no reason to merge free aiin with embedded aiin, or to treat them as necessarily different meanings.

RF has more uncertain raw groups (3,707 versus1,016ZL/42IT), all explicit in RESULT. Uncertain literal ain/aiin groups are56/4/322; other pure groups containing aiin outside the registered tail pattern are33/21/37. These were counted separately, not repaired or cherry-picked. Paragraph flags are not used. Original rows remain in pinned915snapshots.

## Decision and reproducibility

Do not promote a portable immediate-neighbour ain/aiin rule, and do not tune this predictor or append word meanings after its result. Existing directed composition, overall-form effects,1047left-host compatibility and759boundary observations remain. The useful acquired constraint is narrow: a shared local context rule of this explicit kind has failed to predict withheld prefix families materially beyond layout/register. Further work needs a declared different dependency, such as independently defined larger construction roles; another similarity census is insufficient.

Local registration at18:50:00UTC,2026-10-02 preceded this occurrence extraction and scoring. Source snapshots were previously exposed to the project; computational training exclusion is not historical blindness or reserved confirmation. No new images/admissions, f84/f84r/f116v, reserves or contacts. No suitable whole-search null and no significance, calibrated translation probability or confirmed word. Independent meaning-confirmation capacity0.

Run `python3 experiments/yolo/gdt1148_aiin_crossed_context_prediction/src/run.py` and `python3 experiments/yolo/gdt1148_aiin_crossed_context_prediction/src/validate.py`. The readable PREDICTION_TABLE.tsv retains EVERY exact-form prediction; LEAF_RESULTS/PREFIX_RESULTS retain every subgroup. EVENTS/FOLDS/PREDICTIONS are losslessly archived as deterministic JSON.gz to avoid large files; only storage format was compacted after execution, with exact value equality checked. RESULT retains all aggregate metrics and exclusions. Independent validator recomputes extraction and every probability without importing the runner; SEMANTIC_REVIEW checks claim scope, not meanings.
