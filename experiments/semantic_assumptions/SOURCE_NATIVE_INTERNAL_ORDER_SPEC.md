# Frozen edge-score transfer to internal locus order

## Purpose

Distinguish a discrete first/last template from a genuine ordered locus
coordinate. Apply the already frozen and validated source-native edge score to
internal synchronized groups that were never used as positional training
examples. Compare mirrored internal positions: second versus penultimate,
third versus antepenultimate, and so on.

No model component or threshold may be retuned from the confirmed edge result.

## Frozen inputs

- `results/source_sta_family_consensus_groups.tsv`, SHA-256
  `a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225`
- `results/source_native_edge_grammar.json`, SHA-256
  `2a4a246bf1d8de1f2bed76e4e790d44832e9c5ba85cc8d3ad6f2e832b035ea88`
- `results/source_native_edge_grammar_validation.json`, SHA-256
  `0a87ffb2c23fdc6882887e5a854112d678cb6c1de1946407068462ce91fca712`
- the edge score-table SHA-256
  `c27eaee78ec21c8f392157603c585cb44edaee8ad87d72363b9296cf05894b9f`
- this specification and runner, committed before execution.

The frozen score uses only namespaced P1/P2/S1/S2/LEN family features with
Jeffreys alpha .5 and leave-physical-folio-out endpoint training. It contains
no exact complete family-form feature, legacy root/role, semantic label, OCR,
automated vision, or English gloss.

## Target construction

Use strict zero-alternative loci with at least four synchronized groups. Exclude
the first and last group. Pair internal zero-based index `i` with `n-1-i`, for
`i=1,2,...` while `i < n-1-i`; omit an unpaired central group. The lower index
is `EARLIER`, the higher `LATER`. The score was trained only from endpoint
FIRST/LAST labels outside the held folio, never these internal order labels.

The score-blind capacity is 7,728 mirrored pairs in 2,579 loci on 102 physical
folios. Aggregate pair contrasts first to an equal-locus mean, then loci to an
equal-folio mean. A long locus or folio therefore cannot dominate. Exact-zero
folio contrasts are omitted only from the one-sided binomial sign test.

## Primary gates

All must pass:

1. exact capacity 7,728 pairs / 2,579 loci / 102 folios;
2. equal-folio `score(EARLIER)-score(LATER)` is positive and at least 5% of the
   frozen unseen-endpoint contrast 2.7612409548291317;
3. at least 55% of nonzero mirrored pairs have the positive direction;
4. at least 90 nonzero folios and one-sided folio sign p at most .01;
5. minimum leave-one-folio-out equal-folio contrast positive;
6. maximum absolute folio contribution at most .10;
7. compositional contrast exceeds the frozen LEN-only contrast;
8. pair reversal negates every stored contrast exactly;
9. the first three mirror depths each have a positive equal-folio contrast.

## Robustness gates

Each contrast must be positive with the stated minimum folio support:

- confirmed prose: at least 90 folios;
- both endpoint member sequences exact in all readings: at least 90 folios;
- at least one paired complete family form absent from endpoint training outside
  the held folio: at least 90 folios;
- both paired complete family forms absent from that endpoint training: at
  least 50 folios;
- Currier A: at least 45 folios;
- Currier B: at least 35 folios;
- loci of 4-7 groups and loci of 8 or more groups: each positive.

These are robustness gates, not separate discoveries. Individual family,
section, hand, form, or locus diagnostics cannot rescue failure.

## Decision and claim ceiling

All gates yield `CONFIRMED_SOURCE_NATIVE_INTERNAL_ORDER_COORDINATE`; otherwise
the frozen result is a nonconfirmation and this target may not be retuned.

A pass establishes only that the already frozen endpoint-family score extends
directionally through mirrored internal synchronized groups. This is a relative
construction-order coordinate, not temporal order, syntax type, SVO, a word,
START/STOP meaning, sound, linguistic morpheme, part of speech, lexeme,
plaintext, language, cipher, or translation.
