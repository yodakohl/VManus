# GDT1305: token selection can create an exact-form boundary advantage

**SOURCE_FREE_SELECTION_COUNTEREXAMPLE.** Two fixed merge rules create a
40%word-final rate for a surviving compound token, while its surviving right
component has25%. The generating source has independent characters and a
memoryless word-ending probability. No source-side lexical exception memory
is required for this single-feature difference.

This is a mathematical control result, not a new Voynich observation. GDT608
already explicitly allowed a graphemic/BPE explanation, and the8October scope
review already rejected treating ATOMIC's advantage as a universal argument
against composition. The present result makes one selection mechanism concrete;
it does not overturn those records or measure their native effect size.

## The small construction

Generate nonempty words over abstract A,B,C with probabilities1/4,1/4,1/2.
After each character stop with probability1/4; otherwise draw another independent
character. The mean raw length is4. There is no learned word or pair-dependent
continuation parameter. Then apply two fixed analysis rules in order:

1. `A B → M`
2. `M C → N`

For example, `AB` becomes `M`, but `ABC` becomes `N`. An internal `AB` followed
by `C` no longer contributes to M's final-token profile, whereas every word-final
`AB` still does. Its letters have not disappeared; they are counted inside N.
The representations contain pair-sensitive rules even though the source does not.

| Token/profile | Expected count per word | Expected final count | Final rate |
|---|---:|---:|---:|
|Raw B|1|1/4|1/4|
|AB after first merge only|3/16|3/64|1/4|
|M after both merges|15/128|3/64|**2/5**|
|Bare B after both merges|13/16|13/64|**1/4**|

A following C absorbs fraction `(3/4)(1/2)=3/8` of AB occurrences, so
M survives with fraction5/8. Terminal AB always survives. Hence
`(3/64)/(15/128)=2/5`. These are token-weighted population rates: ratios of
expected counts, not averages of per-word ratios.

Using M's own40%population rate to predict its final flag beats using the right
component B's25%by0.078071905bits per M event. This is the Bernoulli cross-entropy
difference for one feature, not the full GDT608score, an empirical held-sample
result, or a p-value. New IID words have the same population law; individual
finite samples need not all exhibit the same sign.

## Why the distinction matters

An exact compound profile can predict better than a component profile because
the two profiles count differently selected surviving occurrences. This example
therefore blocks the inference that such an advantage by itself requires a
stored lexical exception or a source-side nonlinear composition rule. Removing
the second merge returns M's end rate to25%. Applying the same no-following-C
selection to the component also removes this particular mismatch.

It does NOT show that GDT608's observed residual is wholly or mainly a parser
artifact. It does not remove its directed backoff, cross-folio effects or any
raw-word result in a different representation. The actual source and its learned
merge tree are not evaluated here. In particular these two toy rules are FIXED,
not claimed to be the first two merges a frequency-trained BPE learner would
choose on this source. No inference about native meanings or morphemes follows.

Operational consequence: when comparing a new word-construction hypothesis with
such profiles, account for the tokenization and occurrence-selection mechanism.
Do not require the hypothetical scribe to implement an exception table solely
because an analysis-token ATOMIC model outperforms direct component inheritance.
No new decoder, fitted Markov text generator or native reanalysis is selected.

## Exact verification

The producer reviewed the infinite expectation formulas before program execution.
Protocol, programs, proof receipt and cited prior scope documents were hash-locked
at12:37:10UTC before the run. The runner uses two explicit replacement passes and
closed-form expectations. Its finite check enumerates all9840nonempty three-letter
words through length8, using exact probability weights.

A separate validator uses a streaming transducer rather than replacement passes.
An exact rational15-state absorbing system recovers the infinite expectations;
eight reward systems cover the with/without-second-merge cases. All9840finite
words and weighted aggregates agree, and the expected loss difference is checked
by separate cross-entropies. **VALIDATION PASS**. Finite truncation is explicitly
separate from the infinite source; its rates are not substituted for the above.
Both programs are root-authored. Software agreement is not an independent native
or semantic experiment.

No new manuscript row, image, source language or word meaning was used. Old
GDT608bytes and decisions stay unchanged. The new artifact is a scope witness,
not new decipherment progress. All outputs and replay commands are hash-bound
in experiment.json. Inclusive budget12:30–12:50UTC; no automatic expansion.
