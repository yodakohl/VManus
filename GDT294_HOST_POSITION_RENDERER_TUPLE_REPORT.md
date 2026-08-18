# GDT294 — host-position renderer tuple

Status: **HOST_POSITION_RENDERER_TUPLE_SUPPORTED**.

## Held-folio nested gains

| panel | boundary | exact host | host×position | record slot | positive folios | local p | max-family p |
|---|---:|---:|---:|---:|---:|---:|---:|
| AUGSBURG_ACCOUNTS_1402_1424 | -0.0628 | +0.2703 | +0.0019 | -0.0082 | 7/12 | NA_ZERO_NULL_VARIANCE | NA_ZERO_NULL_VARIANCE |
| ARBITRARY_LOCAL_CODEBOOK | -0.0099 | -0.0875 | +0.0821 | -0.0137 | 154/176 | NA_ZERO_NULL_VARIANCE | NA_ZERO_NULL_VARIANCE |
| COMPOSITIONAL_TECHNICAL_NOTATION | -0.2472 | +0.4078 | +0.1414 | -0.2178 | 129/175 | NA_ZERO_NULL_VARIANCE | NA_ZERO_NULL_VARIANCE |
| HYBRID_SHORTHAND | -0.0782 | +0.1988 | +0.1687 | -0.1074 | 146/176 | NA_ZERO_NULL_VARIANCE | NA_ZERO_NULL_VARIANCE |
| LATIN_SCHOLASTIC_GRAPHEMATIC | -0.2358 | +0.6102 | -0.1742 | -0.2059 | 0/6 | NA_ZERO_NULL_VARIANCE | NA_ZERO_NULL_VARIANCE |
| LATIN_MEDICAL_GRAPHEMATIC | -0.3000 | +0.5212 | -0.2374 | -0.2695 | 0/10 | NA_ZERO_NULL_VARIANCE | NA_ZERO_NULL_VARIANCE |
| LATIN_15C_GRAPHEMATIC | -0.2730 | +0.4342 | -0.1595 | -0.1987 | 0/12 | NA_ZERO_NULL_VARIANCE | NA_ZERO_NULL_VARIANCE |
| VOYNICH_REFERENCE | -0.1037 | +1.4820 | +0.0709 | -0.0665 | 66/91 | 0.015384615385 | 0.015384615385 |

The primary host×position increment is measured after physical boundary context and exact opaque host. The record-slot column adds the finer host×position×record/field/group table.

Every control panel has an exact zero-variance null under the strict host-preserving strata, so the reported corrected variable-family p-value effectively contains only Voynich. It is not an eight-powered-family correction. The prior-5 sensitivity also changes the primary sign; treat the frozen support label as a weak, smoothing-sensitive positional lead rather than a stable magnitude.

## Voynich sensitivities

- HELD_PHYSICAL_FOLIO prior=5.0: host×position -0.002385; record slot -0.144188 bits/event (n=7661).
- HELD_PHYSICAL_FOLIO prior=22.0: host×position +0.120558; record slot -0.021984 bits/event (n=7661).
- HELD_SECTION prior=11: host×position +0.057923; record slot -0.082785 bits/event (n=7416).
- HELD_HAND prior=11: host×position +0.049215; record slot -0.079688 bits/event (n=7425).

## Frozen gates

- `host_position_gain_positive`: **PASS**
- `at_least_sixty_of_ninety_one_folios_positive`: **PASS**
- `held_section_gain_positive`: **PASS**
- `held_hand_gain_positive`: **PASS**
- `maxT_p_le_0_05`: **PASS**

## Claim ceiling

This can identify only a host-specific positional renderer distribution. It cannot establish a productive morphological rule, lexical class, word, code value, language, meaning, plaintext, or translation. Host and renderer remain complementary parser outputs. No f84 row was opened, parsed, retained, joined, or scored.
