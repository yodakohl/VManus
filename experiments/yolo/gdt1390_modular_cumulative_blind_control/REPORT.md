# GDT1390 — the bounded full-scale search fails its blind control

**CONTROL_RECOVERY_FAIL_SEARCH_FAILURE.** None of the 12 positive control
messages was recovered exactly. All 12 returned winners score below their true
key under the very same complete likelihood. Thus this search demonstrably
misses a better candidate; its failure cannot reject the cumulative writer or
any Voynich language. The native pilot is not run.

| Controls | Exact messages | Matching characters | Winner minus true-key log likelihood |
|---|---:|---:|---:|
| Six historical source packs,77 characters each |0/6|18/462|−91.24 to−118.95|
| Same six packs, disjoint120 character fragments |0/6|28/720|−137.87 to−215.42|
| Six shuffled 77 character sources |0/6|14/462|+21.22 to+43.67|

Positive character agreement is 46/1182 (3.89 percent). Exact effective-key
recovery is also zero. The negative controls produce higher-scoring wrong
outputs; that is not evidence of readability. No fluency threshold was fitted,
and no output is adopted as a manuscript reading.

## What this control adds

C1064 already specified the cumulative reader c_i=h(w_i)-h(w_(i-1))+b. Here
the writer has a complete fixed probability for every packet of 1..27 working
units, with positive coverage of every state for every allowed key. The
22 weights and offset are unknown to the search. This is a real unrestricted
parameter search, unlike GDT1324's small enumerated supplied-bank example.

The choice law uses 8273 old IT2a/CurrierB TRAIN groups. Existing length>=4
counts match GDT1308 exactly. Missing shorter tables and the all-length
distribution are explicitly new model assumptions. There is no added whole-
word table, target fitting or higher-order spelling repair. The normalized
likelihood includes P(w)/Z_K(state) and a mixture of six complete-message
source likelihoods. Languages do not switch independently at each character.

Each source pack supplies separated training-prefix and control-suffix data.
They are varied historical corpora, not a representative sample of all
medieval languages or medicine. The controls have the77/120 character lengths
of the contemplated passage experiment, but no actual passage is decoded.
No phonetic mapping or native word meaning is assigned.

## Search and blinding

All 18 anonymous cases received 32 random starts and 256 single-weight proposals
per start, with the frozen Metropolis schedule. Each proposal evaluates all
18 invertible scales and 27 offsets with exact normalization. All 576 starts
finished; there was no timeout, reduced sample, true-key initialization,
plaintext-guided restart, or outcome-driven code change.

Code and public models were locked at 03:11:14 UTC. The runtime gate used 100
independent random keys on a separate 120 packet fixture. The full search took
63.664 seconds. This exceeded its optimistic 32 worker extrapolation of 10.378
seconds but stayed within the independently recorded conservative single-
worker estimate of 307.335 seconds and the inclusive budget. Walltime does not
measure search adequacy.

Recovery outputs were frozen at 03:14:31 UTC. Only then, at 03:15:07 UTC, was the
generator seed, true keys and source association released. Input/output hashes
and all restart winners are retained. Generator truth did not enter candidate
selection or stopping.

## Independent checks and interpretation

A separate validator rebuilt the 8273-group selection and all six source-model
tables, reproduced every released-seed control draw, and recomputed all true
and winning likelihoods. Independent backward and forward residue calculations
agree, including state masses near 2e−38; an independent 486 candidate orbit
check agrees with the engine. Scientific accounting validation passes while
the registered recovery gate fails.

For 9 of 12 positive controls the 23 parameter columns have full rank modulo 3.
Conditional on their exact complete plaintext, that certifies a unique key
and offset modulo 27. Three other controls contain an unused unit. This does
not make the plaintext globally identifiable, but missing unit parameters
cannot explain away all 12 failed messages. The observed score deficit directly
establishes search failure regardless of that parameter issue.

The true key's better score does not prove it is the global maximum, that the
source prior is correct, or that another search would succeed. Conversely,
this failure does not show that the writer is informationless or historically
impossible. GDT602/604's earlier caution about language-model outputs remains.

**Decision:** stop this bounded decoder attempt. Do not transfer its outputs
to Voynich, repeat the same starts with a larger count, or automatically change
the source model, word bank, alphabet, resets or message length. A future
recovery proposal requires a genuinely different predeclared strategy and
the same honest full-message control; a native reading requires a separate
selection. The ten-hour research request is still not fulfilled. Confirmed
Voynich word meanings remain zero.

Reproduction inputs and source attributions are in `artifacts/MODELS.json`
and `artifacts/SOURCE_ATTRIBUTIONS.json`. See the preregistration, method,
generator, frozen engine/driver, primary analysis and independent validator.
