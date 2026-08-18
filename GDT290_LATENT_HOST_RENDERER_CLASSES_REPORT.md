# GDT290 — latent opaque host renderer classes

Status: **HOST_POSITION_RENDERING_REMAINS_LEXICALIZED_OR_HIGH_CAPACITY**.

## K=4 primary

| panel | scored | gain (bits/event) | buckets + | positions + | local p | max-family p |
|---|---:|---:|---:|---:|---:|---:|
| AUGSBURG_ACCOUNTS_1402_1424 | 3964 | -0.0557 | 0/8 | 0/4 | NA_ZERO_NULL_VARIANCE | NA_ZERO_NULL_VARIANCE |
| ARBITRARY_LOCAL_CODEBOOK | 2976 | -0.0212 | 3/8 | 0/4 | 0.8923 | 1.0000 |
| COMPOSITIONAL_TECHNICAL_NOTATION | 3289 | +0.1215 | 5/8 | 2/4 | 0.9846 | 1.0000 |
| HYBRID_SHORTHAND | 3186 | +0.1994 | 7/8 | 2/4 | 0.4308 | 0.7538 |
| LATIN_SCHOLASTIC_GRAPHEMATIC | 0 | NA | 0/8 | 0/4 | NA_NO_LATENT_CLASS_CAPACITY | NA_NO_LATENT_CLASS_CAPACITY |
| LATIN_MEDICAL_GRAPHEMATIC | 647 | +0.0256 | 4/8 | 1/4 | NA_ZERO_NULL_VARIANCE | NA_ZERO_NULL_VARIANCE |
| LATIN_15C_GRAPHEMATIC | 1231 | +0.0025 | 3/8 | 1/4 | NA_ZERO_NULL_VARIANCE | NA_ZERO_NULL_VARIANCE |
| VOYNICH_REFERENCE | 7347 | -0.3851 | 0/8 | 0/4 | 1.0000 | 1.0000 |

## Voynich sensitivities

- HELD_PHYSICAL_FOLIO K=2: -0.4397 bits/event on 7347 events; buckets 0/8, positions 0/4.
- HELD_PHYSICAL_FOLIO K=8: -0.3089 bits/event on 7347 events; buckets 0/8, positions 0/4.
- HELD_SECTION K=4: -0.3955 bits/event on 6945 events; buckets 0/8, positions 0/4.
- HELD_HAND K=4: -0.3977 bits/event on 6976 events; buckets 0/8, positions 0/4.

## Frozen gates

- `minimum_capacity`: **PASS**
- `primary_gain_positive`: **FAIL**
- `at_least_six_positive_host_buckets`: **FAIL**
- `at_least_three_positive_positions`: **FAIL**
- `maxT_p_le_0_05`: **FAIL**
- `held_section_gain_positive`: **FAIL**
- `held_hand_gain_positive`: **FAIL**

The target host-position cell is absent from both its feature vector and its class target estimate. Hosts in its immutable bucket never train that class model.

## Claim ceiling

This can identify only compact opaque renderer classes. It cannot establish lexical classes, morphology, grammar functions, abbreviation, sound, language, meaning, plaintext, or translation. No f84 row was opened, parsed, retained, joined, or scored.
