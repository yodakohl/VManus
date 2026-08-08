# Line-local AII+N before AI+N order

The adjacent AII+N -> AI+N direction was frozen before this test. This follow-up asks the held even folios whether the same direction transfers to every non-neighboring AI/AII pair inside a physical line. Odd folios are shown only as discovery history.

## Distance transfer

| subset | edition | mode | AII before AI | reverse | delta | exact page p |
|---|---:|---:|---:|---:|---:|---:|
| ODD | ZL3b | ADJACENT | 59 | 40 | +19 | 0.023104 |
| ODD | ZL3b | NONADJACENT | 231 | 200 | +31 | 0.238276 |
| ODD | ZL3b | LINE_ALL | 290 | 240 | +50 | 0.127842 |
| ODD | IT2a | ADJACENT | 59 | 34 | +25 | 0.001682 |
| ODD | IT2a | NONADJACENT | 226 | 195 | +31 | 0.238767 |
| ODD | IT2a | LINE_ALL | 285 | 229 | +56 | 0.097368 |
| ODD | RF1b | ADJACENT | 54 | 34 | +20 | 0.004937 |
| ODD | RF1b | NONADJACENT | 194 | 170 | +24 | 0.261351 |
| ODD | RF1b | LINE_ALL | 248 | 204 | +44 | 0.124619 |
| EVEN | ZL3b | ADJACENT | 61 | 41 | +20 | 0.035652 |
| EVEN | ZL3b | NONADJACENT | 254 | 163 | +91 | 0.001185 |
| EVEN | ZL3b | LINE_ALL | 315 | 204 | +111 | 0.000742 |
| EVEN | IT2a | ADJACENT | 67 | 42 | +25 | 0.013979 |
| EVEN | IT2a | NONADJACENT | 262 | 165 | +97 | 0.001257 |
| EVEN | IT2a | LINE_ALL | 329 | 207 | +122 | 0.000436 |
| EVEN | RF1b | ADJACENT | 54 | 37 | +17 | 0.042486 |
| EVEN | RF1b | NONADJACENT | 228 | 147 | +81 | 0.002045 |
| EVEN | RF1b | LINE_ALL | 282 | 184 | +98 | 0.001043 |
| ALL | ZL3b | ADJACENT | 120 | 81 | +39 | 0.002796 |
| ALL | ZL3b | NONADJACENT | 485 | 363 | +122 | 0.008754 |
| ALL | ZL3b | LINE_ALL | 605 | 444 | +161 | 0.001783 |
| ALL | IT2a | ADJACENT | 126 | 76 | +50 | 0.000129 |
| ALL | IT2a | NONADJACENT | 488 | 360 | +128 | 0.007671 |
| ALL | IT2a | LINE_ALL | 614 | 436 | +178 | 0.000742 |
| ALL | RF1b | ADJACENT | 108 | 71 | +37 | 0.000967 |
| ALL | RF1b | NONADJACENT | 422 | 317 | +105 | 0.012072 |
| ALL | RF1b | LINE_ALL | 530 | 388 | +142 | 0.002099 |

## Held lexical controls

| edition | scope | observed all-pair delta | null mean | p |
|---|---:|---:|---:|---:|
| ZL3b | BASE | +111 | +37.76 | 0.002165 |
| ZL3b | PAGE_BASE | +111 | +52.09 | 0.001210 |
| IT2a | BASE | +122 | +37.63 | 0.000775 |
| IT2a | PAGE_BASE | +122 | +54.44 | 0.000380 |
| RF1b | BASE | +98 | +38.43 | 0.006750 |
| RF1b | PAGE_BASE | +98 | +41.34 | 0.000895 |

## Even-folio stability

| edition | panel | forward | reverse | page p |
|---|---:|---:|---:|---:|
| ZL3b | FOLIO_MOD4_0 | 133 | 104 | 0.084952 |
| ZL3b | FOLIO_MOD4_2 | 182 | 100 | 0.001530 |
| ZL3b | CURRIER_A | 55 | 38 | 0.098259 |
| ZL3b | CURRIER_B | 260 | 166 | 0.002331 |
| IT2a | FOLIO_MOD4_0 | 143 | 103 | 0.037642 |
| IT2a | FOLIO_MOD4_2 | 186 | 104 | 0.002453 |
| IT2a | CURRIER_A | 52 | 38 | 0.140515 |
| IT2a | CURRIER_B | 277 | 169 | 0.000966 |
| RF1b | FOLIO_MOD4_0 | 121 | 87 | 0.036843 |
| RF1b | FOLIO_MOD4_2 | 161 | 97 | 0.008680 |
| RF1b | CURRIER_A | 48 | 34 | 0.126011 |
| RF1b | CURRIER_B | 234 | 150 | 0.002638 |

## Timm controls

| control | nonadjacent forward | reverse | page p | all-pair page p |
|---|---:|---:|---:|---:|
| Timm_19 | 273 | 244 | 0.171466 | 0.318789 |
| Timm_23 | 197 | 198 | 0.532006 | 0.627467 |
| Timm_41 | 219 | 240 | 0.734247 | 0.806911 |
| Timm_73 | 276 | 268 | 0.400210 | 0.529023 |
| Timm_97 | 210 | 231 | 0.796281 | 0.844462 |

## Decision

**LINE_LOCAL_AII_BEFORE_AI_ORDER_PASS.** On the held half, the adjacent rule transfers to non-neighboring positions in every reading. Both same-base nulls pass for the complete within-line order, including the stricter within-page version. The safe generalization is `[LINE-LOCAL AII+N BEFORE AI+N ORDER]`.

This is stronger than a single collocation but still not a numeral, countdown, phrase head, subject/object order, or lexical translation. AI/AII tokens are not more likely than chance to sit next to each other; only their relative order is asymmetric. The effect is strongest in Currier B, while Currier A remains directionally positive but not independently significant.

Runtime: **20.98 s**.
