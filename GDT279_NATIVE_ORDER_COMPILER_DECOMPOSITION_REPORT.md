# GDT279 — native-order compiler decomposition

Status: **NATIVE_EXCESS_SHARED_OPPORTUNITY_INTERACTION_LEAD**.

GDT278 and its endpoint remain frozen. No new corpus, host substring, semantic field, or score threshold was added.

## Exact matched-sample bridge

| control | matched | same sample/native layout | native sample | layout delta | selection delta | leading layout block |
|---|---:|---:|---:|---:|---:|---|
| ABBREVIATION_HEAVY_MEDIEVAL | +0.2019 | -0.0015 | -0.0370 | -0.2034 | -0.0355 | CLOSURE_BOUNDARY |
| ARBITRARY_LOCAL_CODEBOOK | +0.0283 | +0.0226 | +0.0304 | -0.0056 | +0.0078 | CLOSURE_BOUNDARY |
| AUGSBURG_ACCOUNTS_1402_1424 | +0.0296 | +0.1453 | +0.0757 | +0.1157 | -0.0696 | EDGE_COMPILER |
| COMPOSITIONAL_TECHNICAL_NOTATION | +0.0344 | +0.0440 | +0.1026 | +0.0095 | +0.0586 | OPPORTUNITY |
| HYBRID_SHORTHAND | +0.0190 | +0.0362 | +0.0714 | +0.0172 | +0.0351 | CLOSURE_BOUNDARY |
| LATIN_15C_GRAPHEMATIC | +0.0409 | +0.2854 | +0.3518 | +0.2444 | +0.0664 | OPPORTUNITY |
| LATIN_MEDICAL_GRAPHEMATIC | +0.1039 | +0.2229 | +0.4106 | +0.1191 | +0.1876 | OPPORTUNITY |
| LEARNED_ABBREVIATION_MAP | -0.0237 | +0.0004 | +0.0052 | +0.0241 | +0.0048 | CLOSURE_BOUNDARY |
| LEARNED_ABBREVIATION_SAMPLED | -0.0171 | +0.0007 | +0.0037 | +0.0178 | +0.0030 | CLOSURE_BOUNDARY |
| ORDINARY_NATURAL_LANGUAGE | +0.1060 | +0.0129 | -0.0252 | -0.0931 | -0.0381 | OPPORTUNITY |
| VOYNICH_REFERENCE | +0.3592 | +0.3592 | +0.3646 | +0.0000 | +0.0054 | OPPORTUNITY |

`matched` and `same sample/native layout` use exactly the same source occurrences, mapped host strings, and host-length distribution. The second column restores only source order and layout. `native sample` uses the parent GDT278 native selection.

## Block allocation on the two eligible native-positive Latin panels

| control | layout delta | opportunity | edge compiler | closure/boundary |
|---|---:|---:|---:|---:|
| LATIN_15C_GRAPHEMATIC | +0.2444 | +0.1209 | +0.0916 | +0.0320 |
| LATIN_MEDICAL_GRAPHEMATIC | +0.1191 | +0.0591 | +0.0415 | +0.0185 |

For the **native full model itself**, however, the published Shapley allocation is edge-compiler dominated on all three Latin native reproductions:

| native control | opportunity | edge compiler | closure/boundary | full saving |
|---|---:|---:|---:|---:|
| LATIN_SCHOLASTIC_GRAPHEMATIC | -0.0017 | +0.4392 | +0.0356 | +0.4731 |
| LATIN_MEDICAL_GRAPHEMATIC | -0.0020 | +0.3596 | +0.0529 | +0.4106 |
| LATIN_15C_GRAPHEMATIC | -0.0005 | +0.3287 | +0.0236 | +0.3518 |

The first table is an exact Shapley allocation of the *change* in the fixed null-adjusted compressor score. `OPPORTUNITY` leads that layout-restoration change by removing a negative opportunity×edge mismatch on the overlay; it is not the largest native predictor. The second table shows that source-edge compiler structure carries most native saving, while closure is secondary. Neither table is a semantic decomposition. The Latin scholastic panel lacked GDT278 exact-length capacity, so it has no layout bridge.

## LOFO-safe full-model sensitivity

| control | matched | same sample/native layout | native sample | safe layout delta |
|---|---:|---:|---:|---:|
| VOYNICH_REFERENCE | +0.3573 | +0.3573 | +0.3438 | +0.0000 |
| LATIN_MEDICAL_GRAPHEMATIC | +0.0958 | +0.2789 | +0.4675 | +0.1831 |
| LATIN_15C_GRAPHEMATIC | +0.0467 | +0.2847 | +0.3994 | +0.2380 |

The representation-safe bridge preserves the two Latin layout gains. Alternate readings are not samples; no Voynich transcription replication is claimed.

## Interpretation

Native diplomatic excess can arise from authentic document order and boundary-conditioned graphematic regularity. This pass states exactly which frozen compiler block carries that difference and whether the same mechanism recurs across the two comparable positive Latin panels. It does not turn the magnitude into evidence for a particular language or abbreviation system.

Every inherited FULL score and every inherited FULL null world reproduced GDT278 before the new rows were accepted. LOFO-safe full magnitudes and observed block allocations are exported separately. No f84 source was opened, parsed, retained, joined, or scored.
