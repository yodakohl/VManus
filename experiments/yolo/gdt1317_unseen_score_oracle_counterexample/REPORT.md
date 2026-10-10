# GDT1317: even an exact true half-generator can lose the raw unseen-word comparison

**ORACLE_RAW_UNSEEN_COUNTEREXAMPLE_VERIFIED.** In one fully specified artificial
example, the fitted half-generatorH is EXACTLY the true generating distribution.
Its50:50mixture with M1improves expected complete-word logscore overall by
+.894359nats/word, yet loses−.121259nats on the TRAIN-unseen subset. All components
needed for the unseen word were learned. This is not a missing-fragment example.

This control disproves the universal implication that a true half-generator must
win that raw unseen-word comparison. It does not show Htrue for Voynich, explain
the native1316failure, change its scores or registered decision, or license a
retuned split, mixture or replacement gate. No new manuscript data were examined.

## Complete finite example

Use22abstract symbols A..V, a single supplied word length4, and the fixed cut2.
TRAINcontains54words:

| Whole | TRAINcount | TrueHprobability |
|---|---:|---:|
|AACA|12|40/162|
|AACB|3|5/162|
|BACA|12|32/162|
|BACB|0|4/162|
|ABCA|3|9/162|
|ABCB|24|72/162|

All other four-symbol words have trueHprobability0. The source draws left halves
AA,BA,ABwith probabilities5/18,2/9,1/2. After a left endingA, the probabilities
of rightCA/CB are8/9and1/9; afterB they are1/9and8/9. This is precisely the
fixed-half/seam construction, not a source-language or native glyph assignment.

Fitting the empirical half-tables to this TRAINmultiset reproduces those oracle
probabilities EXACTLY. All six outputs are possible; BACBis the one absent whole.
Its prefixBAoccurs inBACAand its rightCBafterAoccurs inAACB. No unsupported left,
missing seam, smoothing change, mistaken source value or model approximation is
needed. The TRAINmultiset has positive probability under independent draws from
that veryH: approximately.000145199. This probability establishes compatibility
of the example, not the frequency of a failure event or native calibration.

## Why the unseen score is negative

Fit the same position-aware one-previous-symbol M1as1316, with additive1/2over
all22outputs at each context. The exact M1factors forBACBare:

    5/26 ×25/46 ×55/76 ×11/26 =75625/2363296.

This is GREATER than its trueHprobability2/81. WithM=(M1+H)/2:

    M(BACB)/M1(BACB) =10852217/12251250 <1.

The only positive-true-mass TRAIN-unseen word isBACB, so its conditional expected
RAWgain is exactly log(10852217/12251250)=−.12125858169044743. M1overallocates
probability to that word relative to the true distribution and receives the better
raw score when evaluation is confined to that subset.

This comparison uses complete-word probabilities. It does not normalize M1orM
within the unseen set. A conditional renormalization would be a different task;
none is installed as a replacement gate, and no native probabilities are rescored.

## Why the overall score is positive

LetP=M1and letHbe the true distribution. Log-concavity gives

    E_H log((P+H)/(2P)) >= (1/2) KL(H||P) >0.

The inequality is strict here becauseP has positive probability outside H's
six-word support. Direct expected scoring gives+.8943585124773443nats/word.
Thus both directions occur for the SAMEtraining sample and exact true generator.

The verifier does not rely on floating-point signs. Each trueHweight is an integer
multiple of1/162. Raising each exact probability ratio to its integer weight and
multiplying yields a rational number>1forALLand<1forUNSEEN. These complete exact
sign certificates are inRESULT.json; decimal logvalues serve only readability.
BothH andM1normalize, including M1's unobserved symbols and contexts.

## Consequence for the live research decision

GDT1316remains **NO_PRODUCTIVE_HALF_FORM_LEAD under its registered conjunction**.
Its aggregate improvement, failed raw-unseen gate, incomplete fragment coverage,
substantial table cost and original no-retuning stop all remain. Do not turn this
control into a laterPASSor a decipherment lead. A better overall predictor can
still be less useful under the specific raw-score requirement on unseen words.

However, that failure must not be promoted to a structural rejection of midpoint
recombination or evidence that the author could not use such a construction.
Proper logscore favors truth in expectation under the full true distribution;
it need not favor it on every TRAIN-defined subset when using unnormalized full
word probabilities. Here even perfectHknowledge fails that subset requirement.
This is stronger than saying an empirical model may miss a rare fragment.

The observed native failure contains many H=0words; this oracle example contains
none among its true-positive support. It therefore does NOT estimate the reason
or size of the actual native loss. No error rate, sampling-power claim, per-leaf
result or implementation of the full native≥100word/≥10leafgate follows from six
toy words. The toy was deliberately constructed AFTERthe native outcome and is
a logical counterexample, not an independent calibration sample.

## Validation and scope

The source-free producer supplied the finite construction and proof before root
computation. Spec, protocol and both programs were hash-locked before execution.
The primary uses weighted counts and rational probabilities; the independent
same-author verifier expands54toy occurrences, constructs the oracle separately,
checks full M1normalization by a22-state forward probability sum, recomputes the
multinomial probability and exact sign products, and checks logs at90digits.
PASS verifies this mathematical example, not the manuscript or source language.

Only invented A/B/Cstrings and abstract unused alphabet symbols are computed.
No native model/event payloads, rawTSV, image, new source, f84/f84r/f116v/f1rbody,
old327/336body, reserved material or word meaning. Inclusive08:29–08:54UTCbudget
10October2026 includes proof, implementation, validation and publication.
