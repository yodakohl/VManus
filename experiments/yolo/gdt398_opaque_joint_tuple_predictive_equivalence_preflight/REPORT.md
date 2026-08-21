# GDT398 opaque joint-tuple predictive equivalence preflight

Status: **APPARENT_EQUIVALENCE_EXPLAINED_BY_EXISTING_STRUCTURE**.

## Decisive held-folio result

| quantity | result |
|---|---:|
| exact tuple types | 1,676 |
| median selected retained fraction | 0.90 |
| raw gain over exact tuple | +347.103 bits |
| partition cost | 116.837 bits |
| selector cost | 28.435 bits |
| selector-paid gain | +201.832 bits |
| positive outer folds | 5/11 |
| matched-null p | 1.000000 |
| mean pairwise ARI / null q95 | 0.3872 / 0.3142 |
| gain without largest cluster | -216.368 bits |
| gain without top 5% frequent types | -203.128 bits |

## Baselines

| model | held codelength (bits) | difference from exact |
|---|---:|---:|
| GLOBAL_FREQUENCY | 159406.013 | +12033.782 |
| EXACT_TUPLE | 171439.794 | +0.000 |
| PAGE_HOST | 174007.371 | -2567.577 |
| GDT338_NORMALIZED | 171439.794 | +0.000 |
| STRING_SIMILARITY | 176179.927 | -4740.132 |
| PLACEMENT_FREQUENCY | 178730.375 | -7290.580 |
| LEARNED_LATENT_CLASS | 171092.691 | +347.103 |

`GDT338_NORMALIZED` is exactly the exact-tuple predictor at group resolution, as frozen: GDT338 removes wrapper rendering but preserves every joint tuple.

## Gate audit

- `k_meaningfully_below_exact`: **PASS**
- `selector_paid_gain_positive`: **PASS**
- `aggregate_raw_gain_positive`: **PASS**
- `at_least_8_of_11_positive_folds`: **FAIL**
- `multiple_registers_and_sections`: **PASS**
- `stability_above_matched_null`: **PASS**
- `positive_without_largest_cluster`: **FAIL**
- `positive_without_top_frequent_types`: **FAIL**
- `beats_frequency_page_host_and_gdt338_after_cost`: **FAIL**
- `not_reducible_to_string_similarity`: **FAIL**

## Failure localization

GLOBAL/FREQUENCY is 11686.678 bits shorter than the selected latent model. Every one of the 64 matched assignment worlds has a larger selector-paid gain than observed (`p=1.000000`). Removing the largest selected class changes the gain to -216.368 bits; removing the top 5% frequent types changes it to -203.128 bits. No direct merge pair reaches the frozen 0.70 coassignment-stability publication threshold.

The positive aggregate exact-versus-latent difference is therefore ordinary shrinkage concentrated in high-frequency/large-class structure, not a stable freely learned latent lexicon.

## Interpretation

The candidate algorithm saw only opaque type occurrences and the frozen structural views. PAGE_HOST and raw spelling entered named baselines and post-hoc diagnostics only. The result does not license a word, lexeme, morpheme, stem, allomorph, synonym, entity, POS, language, meaning, sound, plaintext, or translation.

If the paid exact-identity comparison fails, this route is closed under the registered stop rule; no alternate clustering algorithm or relaxed K/stability search follows automatically.

## Seal

The GDT327 input and bound 8,448-row source view are f84-free. The view was created through the executable exact-locus allow-list guard with `f84*` rejection before materializing selected columns; the scorer reads only that frozen view. f84 and f84r were not retained, joined, or scored. No semantic or visual annotation was used.
