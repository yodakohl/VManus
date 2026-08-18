# GDT295 — online page-local renderer adaptation

Status: **PAGE_LOCAL_RENDERER_ADAPTATION_WEAK_OR_LOCAL**.

## Online line-safe result

| panel | capacity | eligible | total page gain | page-host | page-position | positive pages | local p | max-family p |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| AUGSBURG_ACCOUNTS_1402_1424 | SCORED | 707 | +0.0276 | +0.0236 | +0.0039 | 71/112 | 1.000000000000 | 1.000000000000 |
| ARBITRARY_LOCAL_CODEBOOK | SCORED | 643 | +0.0261 | +0.0305 | -0.0044 | 32/141 | 1.000000000000 | 1.000000000000 |
| COMPOSITIONAL_TECHNICAL_NOTATION | SCORED | 1385 | +0.1073 | +0.1147 | -0.0073 | 65/162 | 1.000000000000 | 1.000000000000 |
| HYBRID_SHORTHAND | SCORED | 1077 | +0.1069 | +0.0951 | +0.0117 | 69/162 | 1.000000000000 | 1.000000000000 |
| LATIN_SCHOLASTIC_GRAPHEMATIC | UNSCORED | 0 | NA | NA | NA | NA | NA | NA |
| LATIN_MEDICAL_GRAPHEMATIC | UNSCORED | 0 | NA | NA | NA | NA | NA | NA |
| LATIN_15C_GRAPHEMATIC | UNSCORED | 0 | NA | NA | NA | NA | NA | NA |
| VOYNICH_REFERENCE | SCORED | 2880 | +0.0282 | +0.0413 | -0.0130 | 80/153 | 1.000000000000 | 1.000000000000 |

All events on a physical line are scored before that line updates history. The alternative may use earlier lines from the held folio, so this is an online within-page adaptation test rather than a completely unseen-folio prediction.

## Voynich prior sensitivities

- prior 5.0: total -0.078706, page-host -0.004274, page-position -0.074433 bits/event.
- prior 22.0: total +0.053777, page-host +0.045458, page-position +0.008319 bits/event.

## Frozen gates

- `total_gain_positive`: **PASS**
- `at_least_one_hundred_of_one_hundred_fifty_three_pages_positive`: **FAIL**
- `at_least_four_of_six_sections_positive`: **PASS**
- `both_prior_sensitivities_positive`: **FAIL**
- `maxT_p_le_0_05`: **FAIL**

## Claim ceiling

This can support only online page-local adaptation of a parser-defined renderer distribution. It cannot establish a page vocabulary meaning, lexical identity, code value, word, language, plaintext, or translation. No f84 row was opened, parsed, retained, joined, or scored.
