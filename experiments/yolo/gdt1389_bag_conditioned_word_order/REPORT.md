# GDT1389 Whole form gain separates into bag preference and order cost

**NO_RETAINED_CONDITIONAL_ORDER_GAIN in all three readings.** When each word's exact working-unit inventory is fixed, the old whole-form mixture predicts the observed order worse than the frozen local M1 model on average. Its previously positive total gain comes from a positive bag-mass component, which more than offsets this negative order component. This preserves GDT1308's original positive finding while locating its contribution more precisely.

The observed conditional scores still exceed every fixed-M1 reference draw, giving an upper conditional tail of0.005 in each reading. This departure must be retained alongside the negative predictive gain. The result is neither proof that M1 is sufficient nor evidence that word order has no structure. No key, language or word meaning is identified.

## Complete fixed comparison

A bag is the full multiset of the22working units in one word, including repeated units. Currier and length remain fixed. The old position-aware M1=P and whole-frequency mixture M=(P+Q)/2 were not retrained or retuned. Empty TRAIN cells keep the original M=P fallback. Every distinct permutation of a bag is in the declared M1 support; the normalizers do not use only already observed variants.

| Reading | Held words | All physical leaves | Mobile words / leaves | Positive leaves | Conditional order gain, nat/word | Upper conditional tail |
|---|---:|---:|---:|---:|---:|---:|
| ZL3b |7628|46|6025 /46|11|−0.042531|0.005|
| IT2a |8623|46|6792 /46|11|−0.039471|0.005|
| RF1b |7245|46|5599 /46|15|−0.037633|0.005|

Capacity is adequate in every reader. Each mean first averages all original words within its physical leaf, then averages all46leaves equally. Mobility is used only for capacity; zero and negative contributions stay in the ALL denominator. The result fails both the positive-effect requirement of0.01nat/word and the two-thirds-positive-leaf requirement in every reading. This is not a capacity stop. Alternative readers describe one manuscript, not independent replications.

## Where the old gain resides

For an observed word w and its bag B,

    raw gain = log[M(w)/P(w)]
             = log[M(B)/P(B)] + log[M(w|B)/P(w|B)].

Both models are conditioned after the original mixture is formed. In a nonempty TRAIN cell, M(w|B)=(P(w)+Q(w))/(P(B)+Q(B)). Its mixture weight depends on the bag; averaging separately conditioned P and Q at50:50would be wrong.

| Reading | Original total gain | Bag-mass gain | Order gain |
|---|---:|---:|---:|
| ZL3b |+0.087350|+0.129881|−0.042531|
| IT2a |+0.070620|+0.110091|−0.039471|
| RF1b |+0.087732|+0.125365|−0.037633|

All entries are nats per word under the same original equal-leaf weighting; each row adds exactly before rounding. These are signed contributions, not independent experiments or percentages of information explained. GDT1308 remains positive overall. The new result does not erase1309's broad distribution of contributing forms,1374's class-stream coupling or the earlier directed-combination evidence.

For an unseen word with Q(w)=0 but Q(B)>0, the order term is negative: −log(1+Q(B)/P(B)). Only if Q(B)=0does its conditional order term vanish and the original nonempty-cell −log2penalty reside entirely in bag mass. All such cases remain in the comparison. The empty-TRAIN-cell fallback is still zero overall, not an invented unseen penalty.

## Why the reference departure and negative gain coexist

Under the fixed conditional P law, the mean log ratio to the competing conditional M is minus a KL divergence and is therefore nonpositive. The199reference means/ranges are:

| Reading | Mean reference gain | Range of199reference gains |
|---|---:|---|
| ZL3b |−0.066189|−0.090425 to−0.049484|
| IT2a |−0.065638|−0.080729 to−0.044401|
| RF1b |−0.068281|−0.085885 to−0.049914|

The native values are less negative than these draws but remain negative. Thus the fixed whole-form addition loses to P on average while the conditional reference still fails to reproduce its observed score distribution. The joint gate required positive gain and leaf consistency as well as the tail condition; a small tail alone cannot replace that gate. No mixture-weight adjustment, alternative rival or selected leaf subset was tried.

These are conditional references for the frozen fitted model on historically exposed data. They are not project-wide pvalues, proof that every first-order parameterization is wrong, or logical impossibility of a positive-probability writer. The smallest absolute native leaf mean is above0.00023nats, far from the declared numerical tolerance; no positive-leaf decision depends on floating-point zero noise.

## Existing whole forms inspected without new meanings

The four forms already illustrated in GDT1308—daldy, daiin, qokeey and chedy—were inspected after this result, across all three readers and both A/B cells. The full artifact retains every relevant held ID, negative component and absent cell. These examples were not selected to maximize the new result.

- For **daiin**, given its five working units, M1 already assigns99.82–99.98percent probability to the observed order across the retained cells. The extra order gain is only0.000107–0.001090nat per occurrence. This is a model probability conditioned on the inventory, not certainty about pronunciation, meaning or native glyph identity.
- **daldy** retains a positive order gain of0.023–0.056nat per occurrence. Its cells contain only1–3held occurrences and1–2TRAINoccurrences, so it is a rare illustrative case. In ZL/A its old total gain0.975230splits into0.929002bag gain and0.046228order gain.
- **qokeey** has small positive order gains in both A and B cells. **chedy/B** also gains slightly in order; in ZL its bag component is negative. The three chedy/A cells have no held occurrence. These retained counterexamples prevent turning a negative overall mean into a claim that whole-form information never helps ordering.

No English word value, grammatical role, numeral or source-letter assignment follows from these probabilities. The units and their grouping are the existing analytical transcription convention.

## Consequence for the proposed cumulative writer

Every additive packet code assigns the same state to every permutation of a given bag. Fixing all bags therefore fixes every state and, in the cumulative1064channel, the entire source-character sequence for each particular key and offset. The source probability and state normalizers cancel when comparing within-bag orders. Under the stipulated spelling-choice law, the remaining conditional distribution is exactly P(w|B), independently of the unknown key or source language.

This reasoning requires the stated full M1 support and order-invariant framing/selection. A hard bank that excludes some permutations, copied/history-dependent choices, or another word grammar changes the contract. Length and Currier remain supplied covariates. No actual bank, length law, source law or state occupancy has been fitted here.

The new comparison does **not** supply the registered positive rival gain needed to close this choice-law route on that criterion. It also does **not** validate M1, because the reference departure remains. C1064's small numerical reading rule still lacks a justified complete word-choice mechanism and a native key. The useful research correction is to separate selection of the working-unit inventory from ordering it; interpreting the earlier whole-form gain as automatically requiring an independent meaning or ordering rule for every whole word was unwarranted. This is a predictive decomposition, not a reconstruction of the scribe's causal workflow.

## Verification and reproduction

The17-file protocol/input/code lock was written at01:57:20.150896UTC on16October2026, before any native bag normalizer or order score. Source-free primary controls check eight completely enumerated bag masses and24categorical cases. Independent exact-fraction controls check1,092small words across83bags, including repeated units, empty Q support, mixture conditioning and the nonpositive expected log ratio. A misleading unseen-penalty sentence was corrected before the lock; the formulas were already correct.

Native normalization covers all7,144reader/Currier/bag cases. Backward remaining-count DP uses no duplicate-position multiplicity factor. Independent forward used-count DP with layer scaling reconstructs every mass and all23,496original event probabilities, conditional scores, bag scores, leaf denominators and597reference draws. ValidationPASS. Primary normalizers completed in approximately0.52seconds across52cells; no resource ceiling or case omission occurred. Computational checks are not independent manuscript confirmation.

No raw mixed TSV, new page/image, source-language corpus, reserve, f84/f84r,f116v,f1rbody or327/336body was accessed. GDT1323's different capacity stop and1375/1379's original failed criteria remain unchanged. No old report was overwritten.

Run `python experiments/yolo/gdt1389_bag_conditioned_word_order/src/run.py`, then the corresponding `src/validate.py`. Fixed inputs, full bag certificates, occurrence scores, all reference values and the post-result illustrations are retained. Preparation began01:40UTC; the75minute inclusive budget ends02:55UTC. This completed comparison is a checkpoint, not fulfillment of the outstanding ten-hour request.

Evidence: [protocol](PREREGISTRATION.md), [frozen inputs and code](src/REGISTRATION_LOCK.json), [result](artifacts/RESULT.json), [independent validation](artifacts/VALIDATION.json), [interpretation review](artifacts/INTERPRETATION_REVIEW.json), [all four form illustrations](artifacts/FORM_ILLUSTRATIONS.json).
