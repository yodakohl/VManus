# GDT281 — collision-free sensitivity of the GDT280 edge profile

Status: **HASH_COLLISION_SENSITIVITY_PRESERVES_LATIN_RIGHT_VOYNICH_WRAPPER_SPLIT**.

This pass changes only the context identity representation: exact immutable tuples replace SHA256-mod256 buckets. Absolute exact-context savings are sensitivities, because the number of occupied contexts varies and no new model-key charge is imposed.

## Native-order profiles

| panel | representation | outer wrapper | local frame | right family | renderer | edge increment | leader |
|---|---|---:|---:|---:|---:|---:|---|
| LATIN_SCHOLASTIC_GRAPHEMATIC | PUBLISHED_EXACT_CONTEXT | +0.1940 | +0.0494 | +0.2370 | +0.0000 | +0.4803 | RIGHT_FAMILY |
| LATIN_SCHOLASTIC_GRAPHEMATIC | LOFO_SAFE_EXACT_CONTEXT | +0.2969 | +0.0455 | +0.3652 | +0.0000 | +0.7076 | RIGHT_FAMILY |
| LATIN_MEDICAL_GRAPHEMATIC | PUBLISHED_EXACT_CONTEXT | +0.1455 | +0.0391 | +0.1931 | +0.0000 | +0.3777 | RIGHT_FAMILY |
| LATIN_MEDICAL_GRAPHEMATIC | LOFO_SAFE_EXACT_CONTEXT | +0.2021 | +0.0305 | +0.3469 | +0.0000 | +0.5795 | RIGHT_FAMILY |
| LATIN_15C_GRAPHEMATIC | PUBLISHED_EXACT_CONTEXT | +0.1416 | +0.0544 | +0.1480 | +0.0000 | +0.3440 | RIGHT_FAMILY |
| LATIN_15C_GRAPHEMATIC | LOFO_SAFE_EXACT_CONTEXT | +0.2083 | +0.0534 | +0.2141 | +0.0000 | +0.4758 | RIGHT_FAMILY |
| VOYNICH_REFERENCE | PUBLISHED_EXACT_CONTEXT | +0.2876 | +0.1205 | +0.0448 | -0.0267 | +0.4262 | OUTER_WRAPPER |
| VOYNICH_REFERENCE | LOFO_SAFE_EXACT_CONTEXT | +0.2701 | +0.0777 | +0.0366 | -0.0507 | +0.3337 | OUTER_WRAPPER |

## What collision removal changed

| panel | hashed published | exact published | hashed LOFO-safe | exact LOFO-safe |
|---|---:|---:|---:|---:|
| LATIN_SCHOLASTIC_GRAPHEMATIC | +0.4395 | +0.4803 | +0.6513 | +0.7076 |
| LATIN_MEDICAL_GRAPHEMATIC | +0.3525 | +0.3777 | +0.5322 | +0.5795 |
| LATIN_15C_GRAPHEMATIC | +0.3278 | +0.3440 | +0.4659 | +0.4758 |
| VOYNICH_REFERENCE | +0.2684 | +0.4262 | +0.0319 | +0.3337 |

The exact categories preserve the Latin-right/Voynich-wrapper ranking, but they do **not** preserve GDT280's apparent Voynich fold-safe magnitude collapse: `+.0319` becomes `+.3337` bits/event. This corrects the earlier instrument-level interpretation. It does not create a calibrated MDL magnitude, because exact subsets have unequal context capacities; it shows that the collapse itself was driven largely by the 256-bucket collision approximation.

## Matched-source layout bridge

| panel | view | published edge increment | published leader | safe edge increment | safe leader |
|---|---|---:|---|---:|---|
| LATIN_MEDICAL_GRAPHEMATIC | LENGTH_MATCHED_OVERLAY | +0.0564 | RIGHT_FAMILY | +0.0596 | RIGHT_FAMILY |
| LATIN_MEDICAL_GRAPHEMATIC | MATCHED_SAMPLE_NATIVE_LAYOUT | +0.1762 | RIGHT_FAMILY | +0.2441 | RIGHT_FAMILY |
| LATIN_15C_GRAPHEMATIC | LENGTH_MATCHED_OVERLAY | +0.0882 | RIGHT_FAMILY | +0.0966 | RIGHT_FAMILY |
| LATIN_15C_GRAPHEMATIC | MATCHED_SAMPLE_NATIVE_LAYOUT | +0.2756 | RIGHT_FAMILY | +0.2646 | RIGHT_FAMILY |
| VOYNICH_REFERENCE | LENGTH_MATCHED_OVERLAY | +0.3369 | OUTER_WRAPPER | +0.2589 | OUTER_WRAPPER |
| VOYNICH_REFERENCE | MATCHED_SAMPLE_NATIVE_LAYOUT | +0.3369 | OUTER_WRAPPER | +0.2589 | OUTER_WRAPPER |

The Latin layout bridge remains right-family-led and grows when the identical selected occurrences are restored to native layout; Voynich is unchanged by construction.

## Frozen checks

- `latin_published_right_family`: **PASS**
- `latin_lofo_safe_right_family`: **PASS**
- `voynich_published_outer_wrapper`: **PASS**
- `voynich_lofo_safe_outer_wrapper`: **PASS**
- `constant_latin_renderer_zero`: **PASS**

For the Latin panels, the exact-tuple allocation of the constant renderer is exactly zero, confirming that GDT280's tiny renderer values came from hash collisions. The substantive question is whether the Latin right-family and Voynich wrapper directions survive in both published and LOFO-safe views.

## Claim ceiling

This is an instrument sensitivity over an exposed formal profile. It does not identify abbreviation, morphology, a q-prefix function, language, code, notation, meaning, plaintext, or translation. No f84 source row was opened, parsed, retained, joined, or scored.
