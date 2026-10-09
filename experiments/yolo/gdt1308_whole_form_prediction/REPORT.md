# GDT1308: whole-form frequencies improve a fixed character predictor

**WHOLE_FORM_PREDICTIVE_LEAD.** A fixed50:50mixture of the position-aware
one-previous-unit model and empirical TRAIN whole-form frequencies improves
held prediction on41/46physical leaves in ZL3b. The gain survives the complete
cost of previously unseen words. Both alternate transcriptions meet their
sensitivity gates. No learned BPE merges or surviving-token selection occur.

This supports a whole-form weighting component in a predictive construction
model. It does not identify a human lexicon, sound, morphology, word meaning,
source language or original writing procedure. The aggregate improvement is
modest, not a translation percentage.

| Reading | Held words | Positive/all leaves | Equal-leaf gain, nat/word | Token-mean gain | Range in32fitted-M1 controls |
|---|---:|---:|---:|---:|---:|
|ZL3b primary|7628|41/46|+0.087350|+0.082567|−0.273810 to−0.225706|
|IT2a sensitivity|8623|37/46|+0.070620|+0.063738|−0.272245 to−0.223926|
|RF1b sensitivity|7245|38/46|+0.087732|+0.080386|−0.283355 to−0.238437|

All exceed the declared>=100words,>=10leaves, mean>=.01and two-thirds-positive
requirements, and their own largest control gain. The three readings describe
ONEmanuscript. No independent replication or distribution-free p-value is claimed.
ZL mean word loss changes from6.485169 to6.402602nats; predicting length and
Currier themselves is outside both models. ZLnegative leaves6,8,24,58,90remain
in the result, as do every IT/RFnegative leaf.

## What the writer comparison actually knows

Both predictors receive Currier and exact working-unit length. M1predicts the
first unit and then each unit from its exact position and preceding unit,
with additive0.5over22outputs. Its complete-word probability is the product.
Qis the exact whole-form frequency within the same TRAIN(Currier,length)cell.
MIX=(M1+Q)/2, except that a completely absent TRAINcell uses M1unchanged.
Both distributions normalize over ALL22^length strings, including unattested
ones. No weight, smoothing or feature was tuned after outcomes.

The unchanged1233cache supplies Pgroups with definite outside spaces and
unique22-unit parsing; only length>=4is eligible.915cached IDs/forms verify
Currier metadata. Odd physical leaves train, even leaves evaluate. All are
historically exposed, so this is an exploratory fixed comparison, not a fresh
reserved confirmation. No meaning was assigned to any string or component.

The cost of Qis visible: ZL7079TRAINwords,2094distinct whole forms and2329
whole-form/cell entries; IT7984/2323/2591; RF6664/2056/2299. The corresponding
M1tables contain922/960/936observed contexts. This is not a compact medieval
hand algorithm or minimum-description-length proof. No codebook-size price is
subtracted from the predictive scores; parameters are estimated before evaluation.

## Remembered and new forms

| Reading | Q-positive held words | Token gain | Q-zero held words | Token gain |
|---|---:|---:|---:|---:|
|ZL3b|5723|+0.340535|1905|−0.692419|
|IT2a|6427|+0.322354|2196|−0.693147|
|RF1b|5314|+0.361081|1931|−0.692070|

For every Q-zero word in a NONEMPTYTRAINcell, the loss is exactly log(2).
ZL2andRF3words have no TRAINcell at all and therefore zero change under the
registered fallback; ITnone. Globally TRAIN-unseen whole forms number
1592/1856/1640and also lose. They are not hidden or claimed as successful
novel-word generalization. A word known in another Currier cell can still
have Q=0here. Q-positive versus Q-zero are diagnostic outcome groups, not
separately renormalized prediction models or newly selected gates.

Post-result illustrations, selected for familiar structural forms, not as
evidence of meanings:

| Exact whole, ZL | Currier/units | TRAIN Q count/cell | M1 probability | Q probability | Held occurrences | Gain/occurrence |
|---|---|---:|---:|---:|---:|---:|
|daldy|A/5|2/529|.000879|.003781|2|+.975230|
|daldy|B/5|1/1621|.000347|.000617|3|+.328197|
|daiin|A/5|119/529|.172706|.224953|116|+.140858|
|qokeey|B/6|123/1462|.040641|.084131|92|+.428559|
|chedy|B/4|182/1682|.108012|.108205|186|+.000890|

These conditional probabilities concern entire unit tuples. Embedded daldy or
qokeey substrings are not pooled. The daldy examples are small and selected
after the result; their large local ratio is not the primary result or a word
translation. chedy illustrates a familiar whole whose empirical frequency is
already almost matched by M1.

## What the controls establish

For each reader,32fixed synthetic TRAIN/EVALpairs were drawn independently from
its TRAIN-fitted M1table, preserving every row's length, Currier, leaf and split.
Both predictors were refitted on each synthetic TRAINsample and scored unchanged.
All96whole-form mixtures lose. Thus the native gain is not also produced by
these particular fitted-M1worlds and estimation settings.

This is a conditional simulation diagnostic, not a universal rejection of
first-order mechanisms. The generator is fitted, the metadata/lengths are supplied,
and the simulation has no extra page-specific effects. Higher-order spelling,
latent families, stable frequency structure, topical/register heterogeneity or
other mechanisms remain possible explanations. A nonstationary character writer
has not been tested here. Nor does this prove humans memorize indivisible words.

Source-free binary fixtures have exactly normalized distributions: a uniform
four-bit model plus an even-parity whole-form distribution gives log(1.5)gain
on parity words and−log(2)on the others; matching uniform distributions gives
zero gain. These analytical examples check arithmetic, not native content or
external power calibration.

## Prior results and decision

1279's inner one-unit gain remains;1285's two-unit estimator remains failed.
1280's per-word-bigram ordering control remains stopped for capacity. This
comparison does not relax any of those gates.608's directed exterior backoff
and its original scoped residual remain, with1305/1306survival-selection caveats.
1308asks a different question on whole raw groups and therefore does not restore
608as a theorem of lexical exceptions.398's opaque-type clustering/frequency
failure is also unchanged; no327/336body was reopened.

For future comparisons, retain both reusable character connections and exact
whole-form frequency as demonstrated predictive components under this scope.
Do not assume an M1-only shape generator captures all observed frequency weight.
No automatic large decoder, lexical assignment, smoother search or alternate
mixture-weight optimization follows. A new construction needs its own mechanism
and distinguishing consequence, including its behavior on new words.

## Reproducibility and limits

Code/protocol/input hashes were sealed14:26:59UTC before model fitting.
A source-free bounded reviewer inspected the mathematical comparison and its
limits AFTER the empirical run; the reviewer knew the provisional positive status
from the route, but opened no counts, results or programs. This was not a blind
or pre-empirical review. Native data were processed only by root programs. The
separate same-author validator imports no runner: count vectors, log-domain
products and linear inverse-CDF draws reconstruct61181source joins,23496native
word scores, every fitted table, all96simulations and their gates. PASS checks
source/numerical fidelity, not palaeography or independent scientific confirmation.

Only guarded current caches were used; no new images/raw mixed TSVs, old327/336
body, f84/f84r/f116v/f1rbody or reserves. Experiment manifest binds the source,
protocol, runner, validator, fitted model, complete scores and control summaries.
The60minute inclusive work budget ends15:16UTC; no expansion beyond this contrast.
