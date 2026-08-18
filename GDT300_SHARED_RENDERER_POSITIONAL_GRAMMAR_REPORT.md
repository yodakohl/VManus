# GDT300 — shared renderer positional grammar

Status: **POSITION_SIGNAL_HOST_SPECIFIC**.

## Held-folio decomposition

| panel | events | shared gain | exact-pair gain | shared/exact | positive shared folios |
|---|---:|---:|---:|---:|---:|
| COMPOSITIONAL_TECHNICAL_NOTATION | 3449 | +0.3148 | +0.2503 | 1.257748156824 | 169/175 |
| ARBITRARY_LOCAL_CODEBOOK | 3443 | +0.2990 | +0.2247 | 1.330480273540 | 168/176 |
| HYBRID_SHORTHAND | 3337 | +0.2656 | +0.2365 | 1.122852824445 | 164/176 |
| LATIN_GERMAN_APOTHECARY_LATE15 | 695 | -0.0009 | -0.0056 | NA | 2/6 |
| LATIN_15C_GRAPHEMATIC | 4090 | -0.0036 | -0.0045 | NA | 2/12 |
| IFORAL_1395_1411_GRAPHEMATIC | 4303 | -0.0050 | -0.0064 | NA | 0/6 |
| LATIN_SCHOLASTIC_GRAPHEMATIC | 5700 | -0.0060 | -0.0013 | NA | 0/6 |
| LATIN_MEDICAL_GRAPHEMATIC | 4348 | -0.0077 | -0.0021 | NA | 1/10 |
| VOYNICH_REFERENCE | 6844 | -0.0317 | +0.0383 | -0.827836408999 | 26/91 |
| LEARNED_ABBREVIATION_MAP | 6656 | -0.0463 | -0.0284 | NA | 0/4 |
| ORDINARY_NATURAL_LANGUAGE | 6634 | -0.0496 | -0.0195 | NA | 0/4 |
| LEARNED_ABBREVIATION_SAMPLED | 6603 | -0.0555 | -0.0320 | NA | 0/4 |
| ABBREVIATION_HEAVY_MEDIEVAL | 6401 | -0.0574 | -0.0219 | NA | 0/4 |
| AUGSBURG_ACCOUNTS_1402_1424 | 7413 | -0.0700 | +0.0227 | -3.088613858910 | 0/12 |

## Voynich renderer components

| component | gain beyond host | positive folios | local p | max-family p |
|---|---:|---:|---:|---:|
| renderer_tuple | -0.031736 | 26/91 | 0.015384615385 | 0.015384615385 |
| wrapper | -0.042010 | 25/91 | 0.015384615385 | 0.015384615385 |
| b3 | -0.067495 | 11/91 | 0.061538461538 | 0.507692307692 |
| inner_d | -0.069402 | 8/91 | 0.015384615385 | 0.015384615385 |
| right_family | -0.069416 | 8/91 | 0.107692307692 | 0.938461538462 |
| local_frame | -0.072607 | 5/91 | 0.676923076923 | 1.000000000000 |
| dy_closure | -0.072646 | 4/91 | 0.030769230769 | 0.338461538462 |

## Interpretation

The complete shared renderer changes held-folio position codelength by **-0.031736 bits/event** beyond opaque host, versus **+0.038336** for exact host×renderer memory. The shared fraction is **-0.827836408999**; 26/91 folios improve. Frozen gates are `{"both_prior_sensitivities_positive": false, "gdt299_exact_pair_reproduced": true, "max_seven_p_le_0_05": true, "minimum_positive_folios": false, "shared_fraction_at_least_half": false, "shared_gain_positive": false}`.

The exact pair reproduces GDT299, but the frozen cross-host renderer combination is harmful in absolute held-folio codelength. Its small tail means the observed renderer alignment is less harmful than shuffled alignments, not that it beats the host baseline. Under the frozen rule, the transferable placement signal therefore remains host-specific whole-form alternant behavior rather than a compact manuscript-wide renderer grammar. It does not identify a semantic or linguistic function.

## Claim ceiling

Shared physical line-position function of frozen source-form renderer fields across opaque hosts only; no word morpheme linguistic function semantic role code value sound language meaning plaintext or translation. No source string was inspected and no f84 row was opened, parsed, retained, joined, or scored.
