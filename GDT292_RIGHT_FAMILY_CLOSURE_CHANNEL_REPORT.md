# GDT292 — right-family closure channel

Status: **RIGHT_FAMILY_CLOSURE_CHANNEL_WEAK_OR_LOCAL**.

## Held-folio result

| panel | gain (bits/event) | positive right classes | positive folios | null SD | local p | max-family p |
|---|---:|---:|---:|---:|---:|---:|
| AUGSBURG_ACCOUNTS_1402_1424 | +0.0040 | 9/13 | 9/12 | 0.0012 | 0.015384615385 | 0.015384615385 |
| ARBITRARY_LOCAL_CODEBOOK | +0.0885 | 11/13 | 176/176 | 0.0013 | 0.015384615385 | 0.015384615385 |
| COMPOSITIONAL_TECHNICAL_NOTATION | +0.1046 | 13/13 | 173/175 | 0.0020 | 0.015384615385 | 0.015384615385 |
| HYBRID_SHORTHAND | +0.0811 | 12/13 | 171/176 | 0.0015 | 0.015384615385 | 0.015384615385 |
| LATIN_SCHOLASTIC_GRAPHEMATIC | +0.0845 | 13/13 | 6/6 | 0.0037 | 0.015384615385 | 0.015384615385 |
| LATIN_MEDICAL_GRAPHEMATIC | +0.0445 | 13/13 | 10/10 | 0.0036 | 0.015384615385 | 0.015384615385 |
| LATIN_15C_GRAPHEMATIC | +0.0184 | 13/13 | 12/12 | 0.0014 | 0.015384615385 | 0.015384615385 |
| VOYNICH_REFERENCE | -0.0076 | 4/6 | 35/91 | 0.0007 | 0.015384615385 | 0.015384615385 |

Positive gain means the exact frozen right-family class improves held-folio closure-tuple code length after layout, exact host, wrapper, local frame, and inner-D.

The permutation test asks a different question: whether the observed right/closure alignment is less damaging (or more helpful) than shuffled alignments. Voynich may therefore be above its shuffled null while still losing to the outer-context predictive baseline. Frozen support requires positive absolute gain as well as a corrected null result.

## Voynich sensitivities

- HELD_PHYSICAL_FOLIO, prior 5.0: -0.025870 bits/event.
- HELD_PHYSICAL_FOLIO, prior 22.0: +0.004375 bits/event.
- HELD_SECTION, prior 11.0: +0.000251 bits/event.
- HELD_HAND, prior 11.0: +0.003827 bits/event.

## Frozen gates

- `primary_gain_positive`: **FAIL**
- `at_least_four_of_six_right_classes_positive`: **PASS**
- `at_least_sixty_of_ninety_one_folios_positive`: **FAIL**
- `held_section_gain_positive`: **PASS**
- `held_hand_gain_positive`: **PASS**
- `maxT_p_le_0_05`: **PASS**

## Interpretation and claim ceiling

This is a same-group parser-coupled formal association test. Even a positive result would not prove that the right family is a linguistic suffix, that it causally creates closure, or that it is content-neutral. It cannot establish a grammar name, lexical class, abbreviation, sound, language, meaning, plaintext, or translation.

Only the published f84-free native event inventory was read. No f84 row was opened, parsed, retained, joined, or scored.
