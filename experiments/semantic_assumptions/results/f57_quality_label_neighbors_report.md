# F57 quality-position cross-page label-neighbour inventory

## Result

**PASS as an exhaustive post-hoc inventory; no semantic transfer.**

All 868 other-page `kind=L` loci present in ZL3b, IT2a, and RF1b were ranked
against each of the four source-mapped f57v quality-position labels. The
primary order uses the worst corresponding-reading normalized surface
similarity, then its three-reading mean. The alternate readings are robustness
views of one manuscript, not independent observations.

| f57 page-role position | Target | First primary neighbour | Worst / mean similarity | Human-described context |
|---|---|---|---|---|
| HOT | `f57v.6` | `f89r2.34` | 0.625 / 0.667 | label west of a plant fragment |
| MOIST | `f57v.7` | `f71v.9` | 0.700 / 0.700 | zodiac star/nymph-band label |
| COLD | `f57v.8` | `f77v.3` | 0.625 / 0.792 | ambiguous top bathing label near a nymph/tube |
| DRY | `f57v.9` | five-way tie led by `f67r2.57` | 0.750 / 0.750 | Moon/star or zodiac-band labels |

`f77v.3` is therefore the first primary neighbour of the COLD-position form in
the exhaustive candidate universe. It is also the only exact corresponding-
edition surface match for any of the four targets: ZL3b reads both as
`olkeedal`. IT2a and RF1b do not preserve that equality, and **none** of the
four targets has an all-reading exact cross-page match.

## Interpretation

The exhaustive context changes the weight of the resemblance in two opposite
ways:

1. `f77v.3` was not selected from a small hand-picked comparison. It remains
   the strongest robust full-form acquisition target for `f57v.8` among the
   868 eligible labels.
2. Comparable nearest neighbours for the other f57 strings occur in
   heterogeneous plant-fragment, star, Moon, zodiac-figure, container, and
   unannotated label contexts. The shared form therefore diagnoses label and
   circular-register morphology before it diagnoses English meaning.

This does not make the f77 candidate worthless. It makes the next question
precise: can an independent human-readable source establish what `f77v.3`
owns? More Voynich-string similarity cannot answer that question.

## Ceiling

Retain `f77v.3` as the first source-acquisition target for the f57v.8
COLD-position form. Do not call it COLD, a temperature, a nymph name, an organ,
a tube, or an outlet. Do not assign any nearest-neighbour context word to HOT,
MOIST, COLD, or DRY. The page-role English labels remain structural source
homologies rather than lexical translations.

## Reproduction

```text
./vpy experiments/semantic_assumptions/f57_quality_label_neighbors/audit_f57_quality_label_neighbors.py --output experiments/semantic_assumptions/results/f57_quality_label_neighbors.json
```

Two consecutive runs reproduced byte-for-byte. The JSON binds the design,
manual interlinear, and human annotation inputs and preserves the top 20
candidates under all four frozen similarity diagnostics.
