# Source-native within-group stage preflight v2 amendment

Status: **REGISTERED_SYNTHETIC_ONLY_TARGET_UNOPENED**

The v1 synthetic grid is preserved unchanged. It stopped solely because the
frozen `complete_reversal_invariance` predicate compared every numeric and
categorical diagnostic. That predicate is incompatible with v1's deterministic
`floor(K*j/L)` fixed-position comparator: when `L` is not divisible by `K`,
reversing a group moves the surplus position between the two ends and can
change which `FIXED_K` wins. This is an instrument-control contradiction, not
a manuscript result. The target source was existence-tested only and no target
sequence or target score was opened.

V2 changes only that impossible control. It reuses the exact 64 v1 synthetic
worlds and recomputes every one after complete within-group reversal. Require:

1. all v1 gates except `complete_reversal_invariance` are true, and that gate
   alone is false;
2. the reversed grid has at most 1/32 `NULL` positional passes, at least 7/8
   `LATENT` worlds passing both gates, at least 7/8 `FIXED` worlds passing the
   positional gate and zero passing the latent gate, and zero positional passes
   in `CURRIER_ONE` and `ONE_FOLIO`;
3. every world's positional and latent pass decisions are identical before
   and after reversal;
4. in every `LATENT` world, the selected latent model is identical before and
   after reversal, and the complete selected-minus-K1 TEST summaries are equal
   within `1e-10`: global per-symbol gain, equal-folio gain summary, unseen-
   surface gain summary, and Currier-A/B gain summaries;
5. both orientations of every `LATENT` world independently satisfy the frozen
   selected-minus-best-FIXED adaptive-boundary gates. The identity of the best
   `FIXED_K` and its numeric margin are explicitly allowed to differ;
6. the exact capacity, label-permutation, mutation, finite-value, isolation,
   and target-absence gates remain true.

This tests reversal robustness of the scientific decisions without pretending
that an orientation-asymmetric nuisance comparator is numerically invariant.
No thresholds, models, worlds, strengths, target definition, or scientific
claim gate change.

Frozen v1 inputs:

- v1 result SHA-256
  `6e11363eb76ec056504b349764fc998a0b9561dbef25c83a095fadc786071b11`;
- v1 report SHA-256
  `3ddbcba4868e754a8c63ed27745481f4ff0da79f1370ff0d7a5e7163865912c8`;
- v1 runner SHA-256
  `211452815b78c9e01f4548b6a61226730bf36080b5185697dc9ac041f0abceaf`;
- v1 specification SHA-256
  `e3758d2a4c8d5d306b38602e8a1663ebc42a78db2abecd5905fe191a5d983d47`;
- core SHA-256
  `ce1cd0854426b34e8b3e9ba0e6057352f9a5b99737e9e148e791e02979bc65dc`.

Only an independent reconstruction of a passing v2 preflight may authorize a
separately frozen one-time target run. The claim ceiling is unchanged: a
future target pass can establish complete source-native positional structure
and, under the stronger gate, flexible neutral stages. It cannot identify a
prefix, root, suffix, morpheme, sound, word, part of speech, language, cipher
operation, meaning, plaintext, or translation.
