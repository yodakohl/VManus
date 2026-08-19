# GDT347 — frozen compatibility-graph control transport

Status: **MANUSCRIPT_SPECIFIC_FORMAL_CONVENTION**.

The one-time frozen graph contains 3 edges and costs 8.830 bits. Its held Voynich panel scores 1231 transitions: raw gain +65.481 bits, cost-adjusted +56.651, exact recovery 289→287, coupling-null p=0.000244081, and non-neutral coverage 1.000000000.

Native-order controls:

| Control | Architecture | n | Gain | p | Coverage | Comparable | Transfers |
|---|---|---:|---:|---:|---:|---:|---:|
| ABBREVIATION_HEAVY_MEDIEVAL | REAL_DIPLOMATIC | 7699 | +1.117 | 1.000000000 | 0.914014807 | 1 | 0 |
| ARBITRARY_LOCAL_CODEBOOK | LEXICAL_CODEBOOK | 8269 | -3.171 | 1.000000000 | 0.946950458 | 1 | 0 |
| AUGSBURG_ACCOUNTS_1402_1424 | ORDINARY_OR_STRUCTURED_NATURAL_LANGUAGE | 7920 | -1.540 | 1.000000000 | 0.952777778 | 1 | 0 |
| COMPOSITIONAL_TECHNICAL_NOTATION | COMPILER_LIKE_SYNTHETIC | 8273 | -52.183 | 1.000000000 | 0.856037713 | 1 | 0 |
| HYBRID_SHORTHAND | COMPILER_LIKE_SYNTHETIC | 8272 | -20.013 | 1.000000000 | 0.886363636 | 1 | 0 |
| IFORAL_1395_1411_GRAPHEMATIC | REAL_DIPLOMATIC | 6072 | +0.685 | 1.000000000 | 0.943456302 | 1 | 0 |
| LATIN_15C_GRAPHEMATIC | REAL_DIPLOMATIC | 8397 | -3.206 | 1.000000000 | 0.895637331 | 1 | 0 |
| LATIN_GERMAN_APOTHECARY_LATE15 | REAL_DIPLOMATIC | 1546 | +0.015 | 1.000000000 | 0.992669254 | 1 | 0 |
| LATIN_MEDICAL_GRAPHEMATIC | REAL_DIPLOMATIC | 8432 | -4.677 | 1.000000000 | 0.866777356 | 1 | 0 |
| LATIN_SCHOLASTIC_GRAPHEMATIC | REAL_DIPLOMATIC | 8435 | -3.423 | 1.000000000 | 0.861094645 | 1 | 0 |
| LEARNED_ABBREVIATION_MAP | LEARNED_ABBREVIATION | 7760 | +0.000 | 1.000000000 | 1.000000000 | 0 | 0 |
| LEARNED_ABBREVIATION_SAMPLED | LEARNED_ABBREVIATION | 7731 | +0.000 | 1.000000000 | 1.000000000 | 0 | 0 |
| ORDINARY_NATURAL_LANGUAGE | ORDINARY_OR_STRUCTURED_NATURAL_LANGUAGE | 7685 | +3.522 | 1.000000000 | 0.937193667 | 1 | 0 |
| STE1_DIPLOMATIC_RECIPES | REAL_DIPLOMATIC | 109 | +0.000 | 1.000000000 | 1.000000000 | 0 | 0 |
| STE1_EXPANDED_RECIPES | ORDINARY_OR_STRUCTURED_NATURAL_LANGUAGE | 109 | +0.000 | 1.000000000 | 1.000000000 | 0 | 0 |

Transporting controls: none.

Post-score frozen-edge decomposition (decision-inert):

| Panel | Edge | Gain | p | max4 p | delta changes A/B |
|---|---|---:|---:|---:|---:|
| VOYNICH_FIXED_HOLDOUT | inner_d<->canonical_wrapper | +78.604 | 0.000244081 | 0.000244081 | 67/875 |
| VOYNICH_FIXED_HOLDOUT | dy_closure<->canonical_wrapper | -8.321 | 0.230900659 | 0.000244081 | 271/875 |
| VOYNICH_FIXED_HOLDOUT | right_family<->dy_closure | +5.374 | 0.002684891 | 0.000244081 | 323/271 |
| ABBREVIATION_HEAVY_MEDIEVAL | inner_d<->canonical_wrapper | +0.773 | 1.000000000 | 1.000000000 | 0/724 |
| ABBREVIATION_HEAVY_MEDIEVAL | dy_closure<->canonical_wrapper | +0.467 | 1.000000000 | 1.000000000 | 0/724 |
| ABBREVIATION_HEAVY_MEDIEVAL | right_family<->dy_closure | +0.565 | 1.000000000 | 1.000000000 | 2382/0 |
| ARBITRARY_LOCAL_CODEBOOK | inner_d<->canonical_wrapper | +0.127 | 1.000000000 | 1.000000000 | 0/1548 |
| ARBITRARY_LOCAL_CODEBOOK | dy_closure<->canonical_wrapper | -1.754 | 1.000000000 | 1.000000000 | 0/1548 |
| ARBITRARY_LOCAL_CODEBOOK | right_family<->dy_closure | -0.567 | 1.000000000 | 1.000000000 | 1915/0 |
| AUGSBURG_ACCOUNTS_1402_1424 | inner_d<->canonical_wrapper | -0.364 | 1.000000000 | 1.000000000 | 0/701 |
| AUGSBURG_ACCOUNTS_1402_1424 | dy_closure<->canonical_wrapper | -0.444 | 1.000000000 | 1.000000000 | 0/701 |
| AUGSBURG_ACCOUNTS_1402_1424 | right_family<->dy_closure | -0.113 | 1.000000000 | 1.000000000 | 1046/0 |
| COMPOSITIONAL_TECHNICAL_NOTATION | inner_d<->canonical_wrapper | -16.696 | 1.000000000 | 1.000000000 | 0/3317 |
| COMPOSITIONAL_TECHNICAL_NOTATION | dy_closure<->canonical_wrapper | -9.292 | 1.000000000 | 1.000000000 | 0/3317 |
| COMPOSITIONAL_TECHNICAL_NOTATION | right_family<->dy_closure | -8.809 | 1.000000000 | 1.000000000 | 4169/0 |
| HYBRID_SHORTHAND | inner_d<->canonical_wrapper | -4.782 | 1.000000000 | 1.000000000 | 0/2670 |
| HYBRID_SHORTHAND | dy_closure<->canonical_wrapper | -2.968 | 1.000000000 | 1.000000000 | 0/2670 |
| HYBRID_SHORTHAND | right_family<->dy_closure | -5.977 | 1.000000000 | 1.000000000 | 3437/0 |
| IFORAL_1395_1411_GRAPHEMATIC | inner_d<->canonical_wrapper | -0.147 | 1.000000000 | 1.000000000 | 0/730 |
| IFORAL_1395_1411_GRAPHEMATIC | dy_closure<->canonical_wrapper | +0.255 | 1.000000000 | 1.000000000 | 0/730 |
| IFORAL_1395_1411_GRAPHEMATIC | right_family<->dy_closure | +0.975 | 1.000000000 | 1.000000000 | 1101/0 |
| LATIN_15C_GRAPHEMATIC | inner_d<->canonical_wrapper | -0.685 | 1.000000000 | 1.000000000 | 0/1854 |
| LATIN_15C_GRAPHEMATIC | dy_closure<->canonical_wrapper | -0.842 | 1.000000000 | 1.000000000 | 0/1854 |
| LATIN_15C_GRAPHEMATIC | right_family<->dy_closure | -0.495 | 1.000000000 | 1.000000000 | 2377/0 |
| LATIN_GERMAN_APOTHECARY_LATE15 | inner_d<->canonical_wrapper | +0.000 | 1.000000000 | 1.000000000 | 0/0 |
| LATIN_GERMAN_APOTHECARY_LATE15 | dy_closure<->canonical_wrapper | +0.000 | 1.000000000 | 1.000000000 | 0/0 |
| LATIN_GERMAN_APOTHECARY_LATE15 | right_family<->dy_closure | +0.015 | 1.000000000 | 1.000000000 | 67/0 |
| LATIN_MEDICAL_GRAPHEMATIC | inner_d<->canonical_wrapper | -1.279 | 1.000000000 | 1.000000000 | 0/2015 |
| LATIN_MEDICAL_GRAPHEMATIC | dy_closure<->canonical_wrapper | -1.936 | 1.000000000 | 1.000000000 | 0/2015 |
| LATIN_MEDICAL_GRAPHEMATIC | right_family<->dy_closure | -0.158 | 1.000000000 | 1.000000000 | 3183/0 |
| LATIN_SCHOLASTIC_GRAPHEMATIC | inner_d<->canonical_wrapper | -0.726 | 1.000000000 | 1.000000000 | 0/2107 |
| LATIN_SCHOLASTIC_GRAPHEMATIC | dy_closure<->canonical_wrapper | -1.302 | 1.000000000 | 1.000000000 | 0/2107 |
| LATIN_SCHOLASTIC_GRAPHEMATIC | right_family<->dy_closure | +0.075 | 1.000000000 | 1.000000000 | 3778/0 |
| LEARNED_ABBREVIATION_MAP | inner_d<->canonical_wrapper | +0.000 | 1.000000000 | 1.000000000 | 0/0 |
| LEARNED_ABBREVIATION_MAP | dy_closure<->canonical_wrapper | +0.000 | 1.000000000 | 1.000000000 | 0/0 |
| LEARNED_ABBREVIATION_MAP | right_family<->dy_closure | +0.000 | 1.000000000 | 1.000000000 | 0/0 |
| LEARNED_ABBREVIATION_SAMPLED | inner_d<->canonical_wrapper | +0.000 | 1.000000000 | 1.000000000 | 0/0 |
| LEARNED_ABBREVIATION_SAMPLED | dy_closure<->canonical_wrapper | +0.000 | 1.000000000 | 1.000000000 | 0/0 |
| LEARNED_ABBREVIATION_SAMPLED | right_family<->dy_closure | +0.000 | 1.000000000 | 1.000000000 | 0/0 |
| ORDINARY_NATURAL_LANGUAGE | inner_d<->canonical_wrapper | +3.054 | 1.000000000 | 1.000000000 | 0/602 |
| ORDINARY_NATURAL_LANGUAGE | dy_closure<->canonical_wrapper | +1.702 | 1.000000000 | 1.000000000 | 0/602 |
| ORDINARY_NATURAL_LANGUAGE | right_family<->dy_closure | -0.605 | 1.000000000 | 1.000000000 | 1744/0 |
| STE1_DIPLOMATIC_RECIPES | inner_d<->canonical_wrapper | +0.000 | 1.000000000 | 1.000000000 | 0/0 |
| STE1_DIPLOMATIC_RECIPES | dy_closure<->canonical_wrapper | +0.000 | 1.000000000 | 1.000000000 | 0/0 |
| STE1_DIPLOMATIC_RECIPES | right_family<->dy_closure | +0.000 | 1.000000000 | 1.000000000 | 0/0 |
| STE1_EXPANDED_RECIPES | inner_d<->canonical_wrapper | +0.000 | 1.000000000 | 1.000000000 | 0/0 |
| STE1_EXPANDED_RECIPES | dy_closure<->canonical_wrapper | +0.000 | 1.000000000 | 1.000000000 | 0/0 |
| STE1_EXPANDED_RECIPES | right_family<->dy_closure | +0.000 | 1.000000000 | 1.000000000 | 0/0 |

The graph was never reselected or refit on a control. Control-specific learning was restricted to the independent-coordinate marginal reference. The held Voynich benefit is distributional: exact argmax recovery declines by two. More importantly, every admitted control has zero inner-D and zero DY changes under the frozen observation parser. The status therefore means manuscript-specific within this coordinate observation layer; it does not show that ordinary writing lacks an unobserved analogous mechanism. No semantics, PAGE_HOST factorization, tuple merging, or f84 access occurred.
