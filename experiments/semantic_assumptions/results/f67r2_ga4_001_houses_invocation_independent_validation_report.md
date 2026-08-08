# F67R2-GA4-001 houses invocation independent validation

Date: 2026-08-08
Decision: **PASS_INDEPENDENT_RECONSTRUCTION_OF_STOP**

A standalone validator reconstructed the locked houses invocation with exact
rational arithmetic and a structurally independent exhaustive CUDA enumerator.
It imported and executed neither `run_houses_invocation.py` nor
`global_alignment_core.py`. Its GPU kernel assigns one thread to each complete
lexicographic factoradic permutation rank and reduces counters by block; the
production prefix-plus-five-element-tail enumeration is not reused.

Forty checks pass with zero failures. The validator independently confirms
`STOP_HOUSES_GLOBAL_ALIGNMENT_GATE_FAILED`.

## Integrity and exact preprocessing

- The stored result SHA-256 is
  `c9e24c4a6c0b0015e401f765445337493e57963f76656e8eaac1919ee0be18c6`.
- All eight invocation bindings, all sixteen package-lock hashes, corrected
  runner hash `1ebae5f782d6678d53a5d3afaf3f9fe2f641a72ba2869c42b702c9e4086a29c5`,
  and execution-amendment hash
  `cb4840ecdfc9cc3b565edc29c8c19cf76af432195b78ab8849d79bee7f4e09e3`
  match current bytes and the stored manifests.
- The validator rebuilt both raw 12-by-12 signed-Jaccard matrices directly
  from the locked per-record atom sets in `SOURCE_PACKAGE.json`; every exact
  cell and signed set matches `SOURCE_CAPACITY_RESULT.json`.
- Independent original-position distance-ring means, exact residuals, signed
  scale-100,000 quantization, and the two full quantized-matrix SHA-256 values
  match. Both ordered centered correlations reproduce exactly as positive
  `0.1108148561295027`, including covariance and variance fractions.
- The exact locked retained gates reproduce: one automorphism, richness pass,
  atom-robustness/dominance pass, nonzero variances, zero ring sums, and the two
  positive leave-one-view correlations. Only the audited sorted-row-fingerprint
  gate is excluded.
- The pointwise inverse control matches for all 40,320 permutations with digest
  `09e3579404f5d8f676fe74cb9d0e0b824d1862fd17268d9496bf8be352d5b74e`.

## Exhaustive result

| Space | Total | Greater than identity | Equal to identity | Identity score |
|---|---:|---:|---:|---:|
| Full 12 records | 479,001,600 | 90,034,289 | 29 | 21,405,245 |
| Delete H01 | 39,916,800 | 11,462,929 | 4 | 11,140,261 |
| Delete H02 | 39,916,800 | 11,406,527 | 7 | 11,140,261 |
| Delete H03 | 39,916,800 | 708,301 | 216 | 49,091,400 |
| Delete H04 | 39,916,800 | 11,397,377 | 7 | 11,140,261 |
| Delete H05 | 39,916,800 | 3,275,627 | 8 | 34,405,261 |
| Delete H06 | 39,916,800 | 35,197,809 | 14 | -18,751,139 |
| Delete H07 | 39,916,800 | 11,256,084 | 4 | 11,140,261 |
| Delete H08 | 39,916,800 | 8,020,314 | 7 | 15,717,400 |
| Delete H09 | 39,916,800 | 2,068,746 | 8 | 44,514,261 |
| Delete H10 | 39,916,800 | 10,209,554 | 7 | 11,140,261 |
| Delete H11 | 39,916,800 | 2,348,396 | 168 | 38,982,400 |
| Delete H12 | 39,916,800 | 35,926,460 | 192 | -14,174,000 |

Every full and deleted factorial space has exact coverage. Every independently
rebuilt deletion matrix hash, support, identity score, greater/equal count,
tie-inclusive rank, exact p, and decision matches the frozen result. Kernel
timings are necessarily run-specific and were checked only for well-formed
finite nonnegative values.

The identity is not the unique global maximum in the full comparison or in
any deletion. Even the closest deletion, H03, has 708,301 assignments above
identity and an identity-equal count of 216. The frozen houses-first rule therefore stops all
of `F67R2-GA4-001`: no months or zodiac review, W.73 rescore, further rescue,
or Voynich target access is authorized. This is a source-capacity failure and
identifies no manuscript system, meaning, lexeme, plaintext, language, or
translation.

## Validation artifacts

| Artifact | SHA-256 |
|---|---|
| `validate_houses_invocation_nonimporting.py` | `a3af157c5b6176dd93ff7b1c7e05fc076af772c98190d9adf91853fdd31cc3f7` |
| `HOUSES_INVOCATION_VALIDATION.json` | `a06f36edeb3028b582cd523f360ce2d1bb1089e4cd284050a57353b6c428ff70` |
