# Source-native conditional STA member-resolution test

Status: **PREREGISTERED — TARGET UNSCORED**

## Question

Do exact STA member-code distinctions carry transferable FIRST-versus-LAST
endpoint information after their coarse STA-family shells are conditioned out?

This is an incremental resolution test inside the already confirmed
source-native family-edge grammar. It is not a selected minimal-pair search and
does not reopen the f57v glyph-substitution route. STA member codes are
transcription symbols; the test cannot identify physical glyphs or sounds.

## Frozen inputs

- `results/source_sta_family_consensus_groups.tsv`, SHA-256
  `a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225`
- `results/source_sta_family_consensus_validation.json`, SHA-256
  `fcb6a53461b4f9df36f34161ed1d42087f4395988bea0d71f74a7dd635b68b76`
- `results/source_native_edge_grammar.json`, SHA-256
  `2a4a246bf1d8de1f2bed76e4e790d44832e9c5ba85cc8d3ad6f2e832b035ea88`
- `results/source_native_edge_grammar_validation.json`, SHA-256
  `0a87ffb2c23fdc6882887e5a854112d678cb6c1de1946407068462ce91fca712`
- `results/source_member_resolution_capacity.json`, SHA-256
  `5a4058ff814366509d9726e39c481739e7f1bc9c33dee5ec87ac3b96c3525769`
- `results/source_member_resolution_capacity_validation.json`, SHA-256
  `3143a7a69dff1fe4443361b292c581a51f1b6259d7d1e1d6192831232265132b`
- `transcription/sources/sta/STA-Eva_def.bit`, SHA-256
  `7f37853510144fb3e2dc3ee9458d634f41e6d95bc1fbf1c4b8f479a53a021f81`
- this specification and the eventual runner, committed before the target is
  scored.

The existing family-only held score table must reconstruct SHA-256
`c27eaee78ec21c8f392157603c585cb44edaee8ad87d72363b9296cf05894b9f`.

## Panel and split

Use only strict, zero-alternative, multi-group loci. Each locus contributes its
FIRST and LAST synchronized group. Fine features are available only when the
complete member-code sequence is exactly identical in ZL3b, IT2a, and RF1b.
The held unit is the physical folio.

Both endpoint family surfaces must occur outside the held folio. Every fine
feature used by either endpoint must also occur outside the held folio in both
roles. The two disjoint panels are then fixed by complete fine-surface reuse:

- calibration: both complete member surfaces occur outside the folio; expected
  783 loci on 97 folios;
- target: at least one complete member surface is unseen outside the folio;
  expected 285 loci on 81 folios, with target-ID SHA-256
  `f569e1a9cc4dd13f7339b6d3216fff3d0920ed69f0fbaaace8de1b578b19d225`.

The target must not be scored unless the calibration and independent preflight
validation both pass without changing this specification, model, or gates.

## Frozen member-within-family score

For exact code sequence `c` with family sequence `f`, use four namespaced pairs:

- `P1`: first code conditioned on first family;
- `P2`: first two codes conditioned on first two families, or the whole
  one-code sequence;
- `S1`: last code conditioned on last family;
- `S2`: last two codes conditioned on last two families, or the whole
  one-code sequence.

For role `r`, namespace `j`, fine value `c_j`, family shell `f_j`, held folio
`h`, and Jeffreys `alpha=.5`, estimate only from exact-member endpoints outside
`h`:

```text
log P(c_j | f_j, r, not h)
  = log((N(c_j,r,not h)+alpha) /
        (N(f_j,r,not h)+alpha*K(f_j)))
```

`K(f_j)` is the product of the official STA member counts for the family or
family pair in `STA-Eva_def.bit`. The member coefficient is the FIRST log
probability minus the LAST log probability. Sum the four coefficients for an
endpoint. The paired member residual `M` is member-score(FIRST endpoint) minus
member-score(LAST endpoint).

For the already frozen family-only paired contrast `B`, define combined
contrast `B+M`. Define proper incremental log gain per locus as
`log(sigmoid(B+M)) - log(sigmoid(B))`, evaluated for the true FIRST-before-LAST
direction with a stable log-sigmoid implementation.

All locus values are averaged within folio, then folios receive equal weight.
The one-sided sign test is exact binomial on nonzero folio member residuals.

## Controls and preflight gates

Before the target can be joined, an independent implementation must reproduce
the calibration and all of these gates:

1. exact 783 calibration loci on 97 folios and exact target-ID digest while
   target member residuals and gains remain uncomputed;
2. positive equal-folio calibration member residual and log gain;
3. at least 55% positive nonzero calibration locus residuals;
4. calibration folio sign p at most .01;
5. combined calibration locus accuracy strictly exceeds family-only accuracy;
6. minimum leave-one-folio-out member residual and log gain are positive;
7. maximum absolute folio contribution is at most .10 for both residual and
   gain;
8. calibration confirmed-prose, Currier A, and Currier B residuals and gains
   are all positive, with at least 80, 45, and 35 folios respectively;
9. collapsing every fine code to its family produces exactly zero member
   coefficient, residual, and gain within `1e-12`;
10. swapping FIRST/LAST training roles negates every member coefficient within
    `1e-12`; held-folio label mutation cannot change fitted tables;
11. official inventory, finite-value, deterministic serialization, frozen
    family-score hash, source-hash, and no-target-score guards all pass.

A preflight failure ends the experiment with the target unopened.

## Frozen target gates

If and only if preflight passes, all of the following are required:

- exact 285 target loci on 81 folios;
- equal-folio member residual at least `max(.05, .25 * calibration residual)`;
- equal-folio incremental log gain at least
  `max(.002, .25 * calibration log gain)`;
- at least 55% positive nonzero locus residuals and one-sided folio sign
  p-value at most .01;
- combined locus accuracy strictly exceeds family-only accuracy;
- minimum leave-one-folio-out residual and gain positive;
- maximum absolute folio contribution at most .10 for residual and gain;
- confirmed-prose residual and gain positive on at least 70 folios;
- Currier A residual and gain positive on at least 35 folios;
- Currier B residual and gain positive on at least 30 folios;
- every score finite and the independent nonimporting reconstruction exact.

All gates pass: `CONFIRMED_INCREMENTAL_STA_MEMBER_EDGE_INFORMATION`.
Otherwise: `NONCONFIRM_INCREMENTAL_STA_MEMBER_EDGE_INFORMATION`. No retuning,
feature deletion, code subset, reading selection, threshold change, or second
target run is allowed.

## Claim ceiling

A pass establishes only that exact source-agreed STA member-code resolution
adds transferable endpoint-position information beyond its coarse STA-family
shells. It cannot establish physical glyph identity, allography, pronunciation,
linguistic morphology, wordhood, an alphabet, a cipher alphabet, lexemes,
meaning, plaintext, a language, or a translation.
