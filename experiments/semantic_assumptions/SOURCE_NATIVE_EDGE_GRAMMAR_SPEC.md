# Source-native productive locus-edge grammar

## Purpose

Test whether reusable STA-family edge features distinguish the first from the
last synchronized construction group of a multi-group locus when at least one
endpoint family form has never occurred as a complete endpoint form outside
the held physical folio.

This asks whether line/record-edge structure is compositionally transferable
in the new lossless source-native layer. It does not reuse the missing formal
parser, legacy roots or roles, or the failed boundary-confidence target.

## Frozen inputs

- `results/source_sta_family_consensus_groups.tsv`, SHA-256
  `a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225`
- `results/source_sta_family_consensus.json`, SHA-256
  `193ac76bd14b3967844035e8c3997f402d556c7aecf3190145c5295b4eeab3f7`
- `results/source_sta_family_consensus_validation.json`, SHA-256
  `fcb6a53461b4f9df36f34161ed1d42087f4395988bea0d71f74a7dd635b68b76`
- this specification and runner, committed before execution.

No legacy cleaner token, formal root/role, exact full-form feature, image/OCR
output, semantic label, or English gloss may enter the model.

## Panel and split

Use only strict zero-alternative loci containing at least two synchronized
groups. Each locus contributes exactly its first and last group. The physical
folio is the leading `f` plus digits of the page identifier, keeping
recto/verso and panels together.

For each held folio, train on endpoint groups from every other folio. A held
endpoint family surface is `seen` if that exact complete surface occurs as
either a first or last endpoint outside the held folio. The target locus set
requires at least one endpoint to be unseen. The target-blind capacity audit
finds 2,873 multi-group loci: 1,903 have both endpoints seen, 970 have at least
one unseen endpoint, and 117 have both unseen. The 970 primary targets span 100
physical folios.

The 1,903 both-seen loci are a preflight/calibration set. Target scores may be
joined to first/last labels only after every preflight gate passes.

## Frozen compositional score

For each endpoint family surface, extract five namespaced features:

- `P1`: first family;
- `P2`: first two families, or the whole one-family surface;
- `S1`: last family;
- `S2`: last two families, or the whole one-family surface;
- `LEN`: exact length 1 through 7, with 8 or more pooled as `8+`.

The theoretical vocabulary sizes are 21 for P1/S1, 462 for P2/S2 (21
one-family plus 441 two-family values), and 8 for LEN. For class `FIRST` or
`LAST`, feature namespace `j`, value `v`, and Jeffreys `alpha=.5`, compute

```
log P_j(v|FIRST) - log P_j(v|LAST)
```

from training folios only, using the fixed theoretical vocabulary denominator.
The compositional score is the sum over all five features. The baseline score
uses LEN only. No exact complete family surface is a predictor.

For each held locus, the paired contrast is score(first)-score(last). Folio
contrasts are means over loci; folios receive equal weight. Exact zero folio
contrasts are omitted only from the one-sided binomial sign test.

## Target-blind preflight gates

On the both-seen calibration set:

1. exactly 1,903 loci and at least 90 physical folios;
2. positive equal-folio compositional contrast;
3. at least 65% of nonzero locus pairs have the correct direction;
4. one-sided folio sign p-value at most .01;
5. compositional equal-folio contrast exceeds the LEN-only contrast;
6. minimum leave-one-folio-out contrast is positive;
7. maximum absolute folio contribution is at most .10;
8. scores are finite, the complete held score table is deterministic, and
   changing held-folio endpoint labels cannot affect its fitted score table.

A failure stops before the unseen-form target join.

## Primary target gates

On the 970 at-least-one-unseen loci, all must pass:

- exactly 100 target folios and at least 90 nonzero folio contrasts;
- positive equal-folio contrast and at least 60% correct nonzero locus pairs;
- one-sided folio sign p-value at most .01;
- compositional contrast exceeds LEN-only contrast;
- minimum leave-one-folio-out contrast positive;
- maximum absolute folio contribution at most .10;
- positive contrasts in the both-unseen subset (at least 50 folios), confirmed
  prose (at least 80 folios), all-three-exact-member endpoint pairs (at least
  80 folios), Currier A (at least 45 folios), and Currier B (at least 35
  folios).

The subsets are robustness gates, not separate discoveries. Section, hand,
kind, individual form, and individual feature coefficients are descriptive and
cannot rescue a failed primary result.

## Decision and claim ceiling

All gates yield `CONFIRMED_SOURCE_NATIVE_PRODUCTIVE_EDGE_GRAMMAR`; otherwise
the frozen result is a nonconfirmation and may not be retuned.

A pass establishes only that reusable STA-family prefixes/suffixes and length
carry transferable first-versus-last construction-group information on unseen
complete family forms across held physical folios. `FIRST` and `LAST` remain
structural positions, not START/STOP words or meanings. The result cannot prove
authorial word boundaries, a spoken language, sound, morphology in the
linguistic sense, part of speech, lexeme, plaintext, cipher, or translation.
