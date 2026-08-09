# Held source-boundary family grammar transfer

## Purpose

Test whether an ordered local STA-family pair learned only from unanimous
source boundaries versus unanimous nonboundaries transfers to the unopened
majority-versus-minority boundary disagreements on held physical folios.

This is a source-transcription boundary-confidence test. ZL3b, IT2a, and RF1b
are alternate readings of one manuscript, and RF is partly derived from ZL.
No reading is an independent sample and no boundary is assumed authorial.

## Frozen inputs

- `results/source_sta_family_consensus_loci.tsv`, SHA-256
  `84354a9e5d291ab00f45c9bfe161f62d8cbd8c39db7511ff263cd9fcfe9d9e77`
- `results/source_sta_family_consensus_boundaries.tsv`, SHA-256
  `b32aa0a197f9a09eb19087ca80fcc0346601576d49429c346a5df23826ef3974`
- `results/source_sta_family_consensus.json`, SHA-256
  `193ac76bd14b3967844035e8c3997f402d556c7aecf3190145c5295b4eeab3f7`
- `results/source_boundary_grammar_capacity.json`, SHA-256
  `7216a0e5d777d709d303421b2a8a62f38d34eda4b28cf55ee668a0284d2b8e48`
- `results/source_boundary_grammar_capacity_validation.json`, SHA-256
  `9288b2bde84538a292bd048a51768da2af96cd7b3a0dca5bca618e128cf7fcde`
- this specification and the preregistered runner, committed before the target
  run.

No legacy cleaner token, retained formal root, role, image label, OCR output,
automated-vision output, or English gloss may enter the model.

## Gap panel and held unit

Reconstruct all internal gaps of the 3,572 strict zero-alternative,
exact-family loci exactly as in the capacity audit. The physical folio is the
leading `f` plus digits from the page identifier. Recto/verso and panel suffixes
therefore remain in one held unit.

Support 3 is the training positive class; support 0 is the training negative
class. Support 1 and support 2 are excluded from every fitted count and every
preflight statistic. Their scores may be joined to their labels only after all
preflight gates pass.

## Frozen first-order score

Let `c=(left_family,right_family)` be the ordered family pair and let `f` be the
held physical folio. The strict panel alphabet has 21 families, so `K=441`.
Using only support-0/support-3 gaps outside `f`, compute

```
S_f(c) = log((n_3(c)+0.5)/(N_3+0.5*K))
       - log((n_0(c)+0.5)/(N_0+0.5*K)).
```

This is the only fitted model. There is no tuning, feature selection, member-
code feature, metadata feature, higher-order context, or target-dependent
backoff. An unseen pair receives the same Jeffreys-smoothed formula.

## Target-blind preflight gates

Before joining scores to support-1/support-2 labels:

1. the frozen capacity decision and all its gates must pass;
2. all 102 physical folios must have both held support-0 and support-3 rows;
3. mean held-folio support-3-versus-support-0 AUC must be at least 0.90,
   minimum folio AUC at least 0.80, and all 102 folio mean score contrasts must
   be positive;
4. the equal-folio mean training contrast must be at least 4.0;
5. swapping every support-1 label with support 2 before fitting must leave the
   complete 102-by-441 score table byte-identical;
6. every fitted value and calibration statistic must be finite.

Any failure writes a target-unopened stop artifact and forbids the target join.

## Single primary target

For each of the 95 physical folios containing both target classes, compute

```
D_f = mean(S_f(c) | support 2) - mean(S_f(c) | support 1).
D   = equal-folio mean(D_f).
A   = D / equal-folio mean(training support-3 minus support-0 contrast).
```

Zero `D_f` values are discarded only from the exact one-sided sign test. Its
p-value is the binomial upper tail under `p=0.5`. No row is an independent
replicate.

All primary gates must pass:

- `D > 0` and `A >= 0.05`;
- one-sided folio sign-test `p <= 0.01`, with at least 80 nonzero folios;
- the smallest leave-one-folio-out equal-folio `D` remains positive;
- `max(abs(D_f))/sum(abs(D_f)) <= 0.10`;
- the confirmed-prose-only equal-folio contrast remains positive on at least
  50 shared folios;
- for each anchor reading ZL3b, IT2a, and RF1b, compare support-2 positions
  containing that reading against support-1 positions supported only by that
  reading; every anchored equal-folio contrast must remain positive and use at
  least 50 shared folios.

The confirmed-prose and three anchored results are prespecified robustness
gates, not separate discoveries. Other metadata partitions are descriptive
only.

## Decision and claim ceiling

If every preflight and primary gate passes, report
`CONFIRMED_SOURCE_BOUNDARY_FAMILY_GRAMMAR_TRANSFER`. Otherwise report
`NONCONFIRM_SOURCE_BOUNDARY_FAMILY_GRAMMAR_TRANSFER`; no threshold or model may
be changed afterward.

A pass establishes only that an ordered adjacent STA-family context learned
from unanimous source-boundary evidence transfers to stronger versus weaker
alternate-reading boundary support across held physical folios. It may support
a ranked source-aware tokenization confidence layer. It does not select an
authorial boundary, prove a word, correct a transcription, identify a grammar
role, sound, morpheme, lexeme, plaintext, language, cipher, or translation.
