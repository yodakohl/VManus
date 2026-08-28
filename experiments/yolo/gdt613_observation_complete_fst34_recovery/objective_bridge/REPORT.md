# GDT613 scratch bridge audit: pure real-Latin generative cross-entropy

Date: 2026-08-28

Decision: **`PURE_LATIN_CE_FAILS_AT_LEAST_ONE_DECLARED_BRIDGE_GATE`**

## Result

Removing the destroyed-LM subtraction, lexicon reward, grammar costs and key
prior repairs the coarse seven-key ordering: planted truth is rank 1/7 against
all six archived GDT612 pseudokeys under all eight explicit fit/score x
real-Latin panels and under both event-count and square-root weighting.  It
does **not** identify the exact
planted key.  Among all 1,888 declared same-role, same-length, one-primitive
mutations, at least one exposed wrong output beats truth under every model and
232 unexposed mutations tie it exactly.

The audit keeps two contracts separate.  `LEGACY_CONTINUOUS_CHUNK` exactly
retains GDT612's continuous-reference fit and chunk-reset scoring mismatch.
`RESET_MATCHED_WORD` uses the current GDT613 `fst.py` fit construction (three
start boundaries and one terminal boundary per reference word) and resets the
score for every decoded word.  The invariant wrong mutation is primitive 28
(`t`), syllabic output `que -> qua`.  It beats truth in primary bits per
predicted symbol under both contracts:

| contract / LM fit | truth | `que -> qua` | decoy minus truth |
|---|---:|---:|---:|
| legacy / full Latin reference | 2.101683120864 | 2.100615864304 | -0.001067256560 |
| legacy / LM-fit 40% | 2.211424029515 | 2.210435351386 | -0.000988678128 |
| legacy / LM-confirm 20% | 2.328646315785 | 2.327313889858 | -0.001332425927 |
| legacy / synthetic-held only | 2.404527306830 | 2.403346745684 | -0.001180561146 |
| reset-matched / full reference | 2.247816692838 | 2.246749436082 | -0.001067256756 |
| reset-matched / LM-fit 40% | 2.358008100028 | 2.357019454413 | -0.000988645615 |
| reset-matched / LM-confirm 20% | 2.477457578787 | 2.476125114226 | -0.001332464561 |
| reset-matched / synthetic-held | 2.554820656961 | 2.553640366563 | -0.001180290398 |

The current GDT613 FST reports the same likelihood with a letter-only
denominator (boundary cost remains in the numerator).  That normalization does
not rescue truth: on full reference, legacy truth/decoy are
2.462152118600/2.460901812132 bits per letter and reset-matched truth/decoy are
2.633349707934/2.632099401236.  All fixed-length local ranks are unchanged.

This mutation touches three train chunk types and sixteen of 14,553 train
events.  It changes neither emitted length nor boundary count.  On the full
reference model its advantage decomposes into 102.607920 fewer letter bits and
3.480584 fewer boundary bits over the count-weighted stream.  The failure is
therefore not a length-count artifact: the language prior simply prefers the
wrong locally more probable Latin-looking realization over the planted but
less probable one.

## Exact local ranks

| contract / LM fit | truth rank among 1,889 | exposed decoys beating | exact ties |
|---|---:|---:|---:|
| legacy / full reference | 3 | 2 | 232 |
| legacy / LM-fit 40% | 4 | 3 | 232 |
| legacy / LM-confirm 20% | 3 | 2 | 232 |
| legacy / synthetic-held | 2 | 1 | 232 |
| reset-matched / full reference | 3 | 2 | 232 |
| reset-matched / LM-fit 40% | 4 | 3 | 232 |
| reset-matched / LM-confirm 20% | 3 | 2 | 232 |
| reset-matched / synthetic-held | 2 | 1 | 232 |

All 232 ties are exhausted by the already known zero-train-exposure primitives
`F`, `K`, `f`, and `i`: their declared same-length alternatives number
5 + 180 + 26 + 21.  Among the 1,656 exposed decoys there are no ties, but truth
still loses to `que -> qua` in every panel.  The full-reference model also
prefers literal `q -> x` by 0.000026171197 bits/symbol; here letter cost worsens
by 39.222450 bits while boundary cost improves by 41.823946 bits.  The
LM-fit model additionally prefers wholeform `in -> et`; that lead is also
boundary-driven.  Thus explicit boundary decomposition matters, even though
the invariant `que -> qua` failure is supported by both letter and boundary
terms.

## Coarse pseudokey discrimination and length/boundary decomposition

Under the full-reference/count primary, truth emits 84,850 letters and 14,553
boundaries, exactly one word per train event.  Its letter-only cost is
2.300535 bits/letter and boundary cost 0.942292 bits/boundary.  The best archived
wrong key, seed 7001, emits 206,125 letters and 55,058 boundaries, with
4.141080 letter bits and 2.533097 boundary bits; its total is 3.802114
bits/symbol, 1.700430 worse than truth.  Every other wrong key is worse still.
Under the corrected reset-matched/full-reference contract truth costs 2.247817
bits/symbol; the best wrong key is seed 7002 at 4.250555, 2.002738 worse.
Truth remains rank 1/7 in all sixteen contract x reference x weighting panels.  This is a useful
coarse bridge, but it cannot overcome the exact local counterexample.

## Independent split checks

The exact prospective GDT613 partitions replay independently from GDT612 at
hashes `2255b67f...` (`LM_FIT_40`, 8,209 tokens) and `73d40ca5...`
(`LM_CONFIRM_20`, 4,104 tokens).  The legacy LM-fit model scores confirmation
at 2.298712 bits/symbol, while the confirmation model scores LM-fit at
2.500887.  The corresponding reset-matched values are 2.432180 and 2.626128.
The legacy model fit only
to the 3,639 synthetic-held plaintext words scores the full reference at
2.908024; its reset-matched counterpart scores 3.183736.  All are well below
the uniform 27-symbol baseline of 4.754888.
These are disjoint splits of one Caesar reference source, not independent
historical corpora.

## Hard falsifiers

The local-rank falsifier triggers for all eight explicit model contracts.  The seven-key,
length/boundary-invariance, split-sanity and input-scope falsifiers do not.
Independent validation replays twenty-three checks and returns
`INDEPENDENT_VALIDATION_OK`.

## Consequence

Pure real-Latin character cross-entropy is a major repair over GDT612's broken
margin objective but is still not an identifying objective.  More optimizer
starts cannot repair an oracle truth that loses to an enumerated one-site key.
The next control must first expose every truth item and must make exact truth
beat same-length local substitutions prospectively.  Passing this audit would
still establish only a local synthetic objective bridge, never a Voynich
language, key, plaintext, meaning, or translation.
