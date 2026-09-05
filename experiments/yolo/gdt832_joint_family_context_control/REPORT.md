# GDT832 — context recovers wholeword values; joint recovery criterion fails

6 September 2026. Scientific status: **CONTROL_RECOVERY_FAIL**.
Independent software/source validation: **PASS**.

## Result

All three FULL keys recover **8/8 wholeword values and 3/3 active suffix values**.
Removing word context at wholeword interfaces makes all eight wholeword values
wrong in every key. Context therefore addresses the specific identification
failure motivating this control. However, the family term adds no exact held
recovery over OFF, and the remaining literal errors miss every registered
recovery floor. This is a qualified control result, not a successful joint
decoder or a Voynich reading.

Each row below summarizes three keys on the same 13,826 held words in 325
paragraphs. They are key robustness replicates, not independent content tests.

| Model | Exact held words | Aligned characters | Correct W values | Correct active S values | Exact paragraphs |
|---|---:|---:|---:|---:|---:|
| FULL | 93.33–93.35% | 98.81% | 8/8 | 3/3 | 32/325 |
| CUT, context reset at W interfaces | 77.60–77.61% | 90.76% | 0/8 | 3/3 | 1/325 |
| OFF, no family term | 93.33–93.35% | 98.81% | 8/8 | 3/3 | 32/325 |
| REWIRED family membership | 93.33–93.35% | 98.81% | 8/8 | 3/3 | 32/325 |

On the prospectively fixed 8,509-token macro-or-novel-form subset, FULL improves
over CUT by **25.561 percentage points** on average; each key improves. Its gain
over OFF is **0.000 points** in each key, against the required two-point mean.
Over all held words, the FULL–CUT difference is 15.731 points.

FULL falls below all four preregistered reconstruction floors:

| Endpoint | Observed | Required |
|---|---:|---:|
| Exact words | 93.33–93.35% | 95% |
| Aligned characters | 98.81% | 99% |
| Novel composed-form occurrences | 88.88–88.92% | 90% |
| Novel joined-lemma occurrences | 88.62% | 90% |

The positive order diagnostic survives: real FULL has p=.001 for each key,
whereas pseudo FULL has p=.311/.559/.219. Shuffled text can still yield correct
word values; recovery alone is not evidence of a coherent text. Three pseudo
replicates do not establish a general false-positive rate.

## Objective diagnosis

FULL identifies only 21/24, 22/24 and 21/24 supported literal rules. For every
key its selected wrong mapping scores **184.4667 nats above the true mapping**.
The family contribution is identical for truth and selected FULL keys
(993.3333 nats). OFF and REWIRED reproduce the same recovery metrics, with
family contribution zero. The implemented co-lemma factor neither distinguishes
these residual literal errors nor supplies the promised extra recovery.

This is more than inadequate convergence: the known true key cannot be the
maximum of this objective while a wrong legal key scores strictly higher.
More optimization alone cannot make truth the preferred key under the frozen
objective. No alternative key, normalization, threshold or model is rescored
to rescue the experiment. The factor tested here is limited attested family
membership; this does not reject every stronger historical paradigm model.

### Post-result reference audit

The unchanged reference contains **zero `v`, zero `k`, 175,049 `u` and 139 `z`**.
The control has 289 `v` occurrences in discovery and 899 in held text. All
three FULL fits map the literal `v` carrier to `z`. Among 920–922 wrong held
word tokens, 890 involve this wrong `v`, 30 the wrong `z`, and zero or two the
wrong `k`: **96.5–96.7% of wrong words involve `v`**. These are observed source
and fixed-key counts, not replacement-key scores.

This is consistent with a reference-orthography mismatch: the control's `v`
has discovery evidence, but the reference text and its attested family-form
inventory have none. The audit does not independently establish that a specific
normalization would fix recovery. No `v/u` collapsing, replacement mapping,
rescoring or rerun was performed. The registered failure remains. Source and
fixed-fit bindings are in `artifacts/POST_RESULT_AUDIT.json`; the reproducer
is `src/post_result_audit.py`.

## Source design and chronology

The control has 128 discovery paragraphs/5,336 words, 325 held paragraphs/13,826
words and 335,601 independent ITTB reference words. There are 397 observed
source-family edges; 254 share attested reference lemmas. Held novelty counts
are 5,352 composed-form and 3,181 joined-lemma occurrences.

The initial local source-capacity gate stopped because one of four mandatory
suffix rules occurs in neither partition. Before any key or fit, an explicit
design correction restricted identification to observed rules, as already
done for unused letters. The original STOP artifact remains byte-unchanged.
Text, book split, nominal deck and recovery/gain thresholds did not change.
The actual observable class has 24 L, three S and eight W rules; three nominal
parameters receive no identification credit. This was a disclosed **pre-fit
correction**, not a publicly preregistered source-capacity pass.

Fit code, inputs and exact criteria were then published at commit
`8beefeec1db6a17e1e3e816159d622d617782d48` before fitting. All 120 restart fits and
15 discovery-selected keys were fixed before evaluation opened key truth.
The fit lock SHA256 is
`5593244dce9ef3548416b1a28b501cf5bdf7937add4a49ff027c732553bbb2cd`.
No fitter, source input or registered threshold was changed after publication.

## Validation and reproducibility

Fourteen independent toy checks cover probability normalization, context,
family-degree rewiring, C++/Python objective equality, segmentation invariance,
key legality and more than 8,800 incremental mutation checks. Independent source
reconstruction verifies all 453 control paragraphs and original/final capacity
decisions. The final validator reconstructs **120 C++ objectives, 15 selections,
207,390 held word predictions and 5,994 null scores**, including source/key
commitments and all decision gates. Validation passing does not change the
scientific failure status.

Compact result: `artifacts/RESULT.json`; detailed evaluation and independent
replay: `artifacts/EVALUATION.json` and `artifacts/VALIDATION.json`. The original
fit lock, all restart keys and now-released control truth are retained.
`src/summarize.py --check` verifies the compact projection. For a fresh fit,
use the preregistration commit; the current runner refuses to overwrite a
locked fit set. See METHOD.md for source rebuilding and the evaluator/validator
CLI for independent replay.

## Interpretation ceiling

Continuous word context has demonstrated identification value **in this known
mixed control architecture**. The tested family factor has no demonstrated
additional recovery benefit, and full reconstruction remains unsuccessful.
Known role classes and boundaries are supplied; no unknown segmentation or
complete historical paradigm inference was solved. No Voynich source was
opened, fitted or translated. GDT616/CDA001 stay closed; no successor fit is
selected by these results.
