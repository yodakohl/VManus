# Source-native within-group monotone-stage grammar

Status: **REGISTERED_TARGET_UNOPENED**

## Frozen representation and split

Use the 21,899-row target-masked capacity panel. Physical folios were frozen
before fitting: 47 TRAIN folios / 10,753 groups, 23 CAL folios / 5,516 groups,
and 24 TEST folios / 5,630 groups. Currier A and B are fit separately under one
common model family and stage count; selection uses their combined CAL
likelihood. TEST is opened only after selection is final.

The target is each complete source group's official STA-family sequence over
the fixed 24-family alphabet `ABCDEFGHJKLMNPQRSTUVWXYZ`. Groups are complete
manual source-separated units, not legacy cleaned words or partial-parser
nodes.

## Models

All multinomial emissions use symmetric Dirichlet `alpha=0.5`.

- `K1`: one exchangeable family distribution per Currier.
- `FIXED_K`, K=2..5: deterministic equal-width position bins
  `min(K-1, floor(K*j/L))`.
- `LATENT_K`, K=2..5: a group has K ordered contiguous stages. Empty stages
  are allowed. Conditional on length L, every weak composition of L into K
  stage lengths has equal prior probability. Likelihood sums exactly over all
  `C(L+K-1,K-1)` paths.

Fit latent emissions by deterministic EM initialized from midpoint equal bins,
at most 40 iterations, stopping at maximum emission change below `1e-11` or
per-unique-sequence log-likelihood change below `1e-12`. CAL selects the single
candidate with maximum total log likelihood per symbol; exact ties follow the
listed order K1, FIXED_2..5, LATENT_2..5. The best FIXED model is selected
separately on CAL as the adaptive-boundary comparator.

## Frozen TEST summaries

For each test group compute selected-minus-K1 and selected-minus-best-FIXED log
likelihood. Sum within physical folio and divide by that folio's symbol count;
then weight folios equally. Compute exact one-sided folio sign probability,
all folio deletions, maximum absolute folio contribution, Currier A/B views,
and the same selected-minus-K1 effect on complete `(Currier, family sequence)`
surfaces unseen in TRAIN.

`POSITIONAL_PASS` requires:

- non-K1 selection; exactly 5,630 test groups and 24 folios;
- equal-folio gain at least .02 nat/symbol, at least 18/24 positive, exact
  sign p at most .01, positive minimum deletion, and maximum contribution at
  most .15;
- at least 500 unseen test groups, unseen equal-folio gain at least .015 and
  positive minimum deletion;
- Currier A and B each have gain at least .01, positive minimum deletion, and
  at least 70% positive folios.

`LATENT_STAGE_PASS` additionally requires selection of `LATENT_K`, latent-minus-
best-FIXED equal-folio gain at least .005, at least 17/24 positive folios,
positive minimum deletion, and positive gain in both Currier registers.

`POSITIONAL_PASS` alone establishes only complete source-native within-group
position structure. `LATENT_STAGE_PASS` establishes a transferable flexible
ordered-stage grammar and authorizes a neutral S0..S(K-1) parse atlas.

## Target-free calibration

Before opening any family sequence, use only the masked panel and generate:

- 32 Currier-specific iid `NULL` worlds;
- eight three-stage variable-boundary `LATENT` worlds at strength .65;
- eight equal-position `FIXED` worlds at strength .65;
- eight B-only `CURRIER_ONE` worlds at strength .65;
- eight `ONE_FOLIO` worlds at strength .65.

Synthetic noise is independent across TRAIN/CAL/TEST but grouped into 128
deterministic unit buckets for speed; planted state-family maps are shared
across splits. Require at most 1/32 positional null passes, at least 7/8 latent
worlds passing both gates, at least 7/8 fixed worlds passing positional but
zero passing latent, zero positional passes in both adversarial families,
exact capacity, fixed permutation-of-all-24-label invariance, complete reversal
invariance, finite values, schema mutations, target isolation, and absent
target outputs. Use 32 forked workers with every numeric thread count one.

## Frozen inputs and ceiling

- `results/source_native_within_group_stage_masked.tsv`, SHA-256
  `16d7395ae0410c8fc72b5e5462d6d425cd3a2685e7ea70eee0677bd936106ae5`
- `results/source_native_within_group_stage_capacity_validation.json`, SHA-256
  `2a95ce3183b72540f39a8ef0f68129d1f7ccf2e688683a9f2989360f84c20007`
- `source_native_within_group_stage_core.py`, SHA-256
  `ce1cd0854426b34e8b3e9ba0e6057352f9a5b99737e9e148e791e02979bc65dc`

Only an independently reconstructed passing calibration authorizes one
separately frozen target run. Structural stages remain neutral: neither result
identifies prefix, root, suffix, morpheme, sound, word, part of speech,
language, cipher operation, meaning, plaintext, or translation.
