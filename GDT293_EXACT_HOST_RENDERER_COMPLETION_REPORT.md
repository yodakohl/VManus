# GDT293 — exact-host renderer completion

Status: **EXACT_HOST_RENDERER_COMPLETION_SUPPORTED**.

## Held-folio joint completion

| panel | eligible | joint gain bits/event | components positive | folios positive | local p | max-family p |
|---|---:|---:|---:|---:|---:|---:|
| AUGSBURG_ACCOUNTS_1402_1424 | 7646 | +0.2333 | 4/6 | 12/12 | 0.015384615385 | 0.015384615385 |
| ARBITRARY_LOCAL_CODEBOOK | 4816 | -0.0956 | 2/6 | 44/176 | 0.015384615385 | 0.015384615385 |
| COMPOSITIONAL_TECHNICAL_NOTATION | 4804 | +0.1998 | 3/6 | 114/175 | 0.015384615385 | 0.015384615385 |
| HYBRID_SHORTHAND | 4655 | +0.1222 | 1/6 | 112/176 | 0.015384615385 | 0.015384615385 |
| LATIN_SCHOLASTIC_GRAPHEMATIC | 6524 | +0.6103 | 4/6 | 6/6 | 0.015384615385 | 0.015384615385 |
| LATIN_MEDICAL_GRAPHEMATIC | 5282 | +0.5190 | 4/6 | 10/10 | 0.015384615385 | 0.015384615385 |
| LATIN_15C_GRAPHEMATIC | 4933 | +0.4335 | 4/6 | 12/12 | 0.015384615385 | 0.015384615385 |
| VOYNICH_REFERENCE | 7661 | +1.4149 | 6/6 | 90/91 | 0.015384615385 | 0.015384615385 |

Voynich joint codelength falls from 4.5921 to 3.1772 bits/event; top-1 accuracy rises from 0.2347 to 0.3981.

## Voynich component diagnostics

- `WRAPPER`: +0.467177 bits/event.
- `LOCAL_FRAME`: +0.322582 bits/event.
- `INNER_D`: +0.045151 bits/event.
- `RIGHT_FAMILY`: +0.362318 bits/event.
- `DY_CLOSURE`: +0.163927 bits/event.
- `B3`: +0.089966 bits/event.

## Voynich sensitivities

- HELD_PHYSICAL_FOLIO prior=5.0, n=7661: +1.464439 bits/event.
- HELD_PHYSICAL_FOLIO prior=22.0, n=7661: +1.375530 bits/event.
- HELD_SECTION prior=11, n=7416: +1.791567 bits/event.
- HELD_HAND prior=11, n=7425: +1.767488 bits/event.

## Frozen gates

- `joint_gain_positive`: **PASS**
- `at_least_four_of_six_components_positive`: **PASS**
- `at_least_sixty_of_ninety_one_folios_positive`: **PASS**
- `held_section_gain_positive`: **PASS**
- `held_hand_gain_positive`: **PASS**
- `maxT_p_le_0_05`: **PASS**

## Interpretation and claim ceiling

This tests only whether an exact opaque host recurring outside the held folio helps complete its parser-defined same-group renderer tuple. GDT165 immediate NEXT_HOST transfer remains negative and was not rerun. A positive same-group result would therefore not be evidence for stable word order or sequential syntax.

All three Latin graphematic controls also improve, so same-group renderer completion is not Voynich-specific. Voynich is larger on this fixed panel, but that magnitude comparison was not a separate frozen uniqueness test.

Host and renderer coordinates come from the same frozen parser. The result cannot establish lexical identity, a word, code value, morpheme, sound, language, meaning, plaintext, or translation. No f84 row was opened, parsed, retained, joined, or scored.
