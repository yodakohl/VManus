# `cho/che` scope synthetic preflight v2 — arithmetic-only amendment

Status before execution: **REGISTERED_V1_INVALID_TARGET_UNOPENED**

This amendment changes no scientific question, panel, score, averaging order,
synthetic world, seed domain, assignment count, threshold, gate, or claim
ceiling in `CHO_CHE_SCOPE_SYNTHETIC_PREFLIGHT_SPEC.md` (SHA-256
`b2b51a91b999ae926170a76ce8ffe8f5b8a7d01f3e71200e93b26cefce900c94`).

V1 stopped on `rotation_multiset_preservation`. Its result (SHA-256
`203ab1e60c83f43f6cb095b095c461cf7742ba30fecf6ff0cc2b79925c82331e`)
is invalid for every null and power score. The bound audit (SHA-256
`0b0c2c864ff5b375c0eb2530f344dd19b63a5eab69bdcac27335c8ae19ae4255`)
reproduced 2,079 violations in the first 16 assignments and identified one
implementation defect: unsigned `j-shift` wrapped at `2^64` before modulo `n`.

V2 replaces only

`(uint64(j)-uint64(shift)) mod n`

with the mathematically equivalent non-underflowing expression

`(uint64(j)+uint64(n)-uint64(shift)) mod n`.

The repaired core SHA-256 is
`b77dd67d49c4e173d16bce2409c8f691e9cf7aae30b1333ee0eeffd9a98193b8`.
Before the full synthetic run it must preserve the exact one-count in every
rotation stratum for assignments 1 through 512 under both ensembles. V2 writes
new `_v2` artifacts and may not overwrite v1. The manuscript source outcome
table remains existence-test-only, and target outputs must remain absent.

Only an all-gate v2 pass followed by an independent reconstruction may
authorize a separately frozen one-time target run. No manuscript scope,
authorial paragraph, sound, word, language, cipher operation, meaning,
plaintext, or translation follows from this repair or preflight.
