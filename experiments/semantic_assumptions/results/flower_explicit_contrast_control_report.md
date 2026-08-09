# FLOWER001 blocked flower/no-flower control report

## Status

**Corrected anonymous controls and independent validation pass; target unrun.**

The human page atlas supplies 19 Herbal pages with the exact
Gheuens/Rapaport phrase `flower(s) seen from the side` and seven with the
exact phrase `no fruits or flowers`. Silence is not a negative. A first
source-only blocked build was rejected because it allowed recto and verso
sides of one folio to act as separate units. It extracted no target score and
created no target artifact.

The corrected panel admits one page per folio, prevents a positive from
sharing a negative folio, and freezes two minimum-total-distance positive
pages around each negative. It contains 21 distinct folios, all section H,
Currier A, hand 1. The 843 reading-specific confirmed-prose loci contain
1,817/1,793/1,787 literal and 1,766/1,750/1,740 parsed-root tokens in
ZL3b/IT2a/RF1b.

The frozen current-grammar inventory retains 430 recurrent features. Token
length and linear folio number are removed before scoring. The exact null
chooses one putative negative inside each of seven triplets, giving
`3^7 = 2,187` synchronized assignments.

## Controls

| Control | Result |
|---|---:|
| exact assignments | 2,187 |
| eligible features | 430 |
| unique synthetic planted tail | 1/2,187 |
| alternate-reading disagreement maximum | 0 |
| block-constant maximum | 0 |
| inclusive top-tie count | 3 |
| strict values above tied top | 0 |
| adjusted family maximum 95th percentile | 2.942953892458 |
| raw family maximum 95th percentile | 2.931606886482 |

The independent implementation imports no production experiment code. It
reconstructs the literal source census, distinct-folio matching optimum,
metadata, token totals, 430-feature identity, canonical count matrix, exact
orbit, both family nulls, and every synthetic control in 22 checks. Both
artifacts reproduce byte for byte on their own reruns.

One frozen target invocation is authorized. Even a pass can nominate only a
page-field pattern associated with this exact illustration contrast; it cannot
establish FLOWER, FRUIT, NO, a plant name, language, plaintext, or translation.

## Reproduction

```text
./vpy experiments/semantic_assumptions/flower_explicit_contrast/run_flower_explicit_contrast.py --mode controls --output experiments/semantic_assumptions/flower_explicit_contrast/CONTROL_RESULT.json
./vpy experiments/semantic_assumptions/flower_explicit_contrast/validate_flower_explicit_controls.py --output experiments/semantic_assumptions/flower_explicit_contrast/CONTROL_VALIDATION.json
```
