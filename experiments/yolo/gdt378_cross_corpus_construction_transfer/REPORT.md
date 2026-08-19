# GDT378 report — cross-corpus construction-level functional transfer

## Result

The comparator-first stage used 133,183 form-blind elements in 3,235 records
from five independent readable domains. All source words, translations, POS,
parses, editor roles, concepts, function labels, and parent links were hidden
from the detector. Evaluation held out one complete corpus domain at a time
and charged all 13 endpoints and seven representations in one 256-world
max-family null.

The requested construction-level `HEAD_WITH_DEPENDENTS` signature did **not**
generalize. Its best comparator-selected representation was `SCOPE_HORIZON`:

| Held domain | AUC | full structure − nuisance gain (bits) |
|---|---:|---:|
| CoReMA | 0.603566 | -6468.724 |
| PCEEC2 | 0.612480 | -1805.627 |
| Curious Cures | 0.602460 | +234.801 |
| Harleian cookery | 0.566032 | -3374.727 |
| Quinte Essence | 0.690146 | +144.879 |

The required transfer floor is 0.603566 and the max-family p-value is 1.0.
Only Quinte satisfies both AUC >= .65 and positive incremental structure gain.
The frozen HEAD gate therefore fails. This preserves GDT377 unchanged: exact
tuple identity was not rescued, and no construction-level `HEAD_SLOT` was
nominated.

## Secondary functional calibration

Seven secondary endpoints had a comparator-only transfer statistic >= .65
with max-family p <= .05. That broad diagnostic alone is not enough for
Voynich transfer because it can be driven by record position and length.
Before any Voynich access, a stricter safeguard retained only endpoints with
AUC >= .65 **and** positive structure-over-nuisance gain in at least three held
domains, including one syntax/non-recipe domain and one procedural domain.

Four anonymous signatures survive that safeguard:

| Anonymous ID | Comparator oracle used for calibration | Representation | transfer floor | max-family p | strong held domains |
|---|---|---|---:|---:|---|
| CMP_FUNCTION_01 | UNTIL_STATE_GATE | within-record rank | 0.835989 | 0.003891 | Curious, Harleian, PCEEC2 |
| CMP_FUNCTION_02 | ALTERNATIVE_OR | neighbor/recurrence | 0.899070 | 0.003891 | Curious, Harleian, PCEEC2, Quinte |
| CMP_FUNCTION_03 | POLARITY_EXCLUSION | neighbor/recurrence | 0.770314 | 0.003891 | Harleian, PCEEC2, Quinte |
| CMP_FUNCTION_04 | FUNCTION_WORD | absolute structural probability | 0.856462 | 0.003891 | Curious, Harleian, PCEEC2 |

These labels describe the hidden readable-comparator endpoints, not Voynich
meanings. On Voynich they remain `CMP_FUNCTION_01`–`04`, with semantic state
`UNASSIGNED`. Their fitted coefficients, standardization, score transforms,
and comparator-selected quantile thresholds are frozen in
`gdt378_secondary_transfer_signature_freeze.json` before target access.

Three other provisional comparator leads were not authorized for target use:

- coordinator had strong rank performance but its syntax-gold PCEEC2
  structure gain was negative;
- state-transition transferred in rank across the three procedural editions
  but added information over nuisance in only one;
- closer was unstable, including AUC 0.203 on Curious Cures, and had only two
  domains with positive incremental gain.

REF/anaphora, correlatives, NEXT/RESUME, comparison, high-valency headness, and
the primary HEAD endpoint did not clear the comparator transfer criterion.
Notable falsifiers include inverse/below-chance behavior for REF in CoReMA and
PCEEC2, ALTERNATIVE/OR in CoReMA, UNTIL in CoReMA, and closure in Curious
Cures. The source oracles for Curious, Harleian, and Quinte are frozen
high-precision lexical controls rather than syntax gold, so even the four
survivors remain provisional instrument signatures.

## Decision and next stage

The comparator conclusion is:

`HEAD_SIGNATURE_NO_CROSS_DOMAIN_TRANSFER`

plus:

`FOUR_SECONDARY_SIGNATURES_FROZEN_FOR_ANONYMOUS_MULTI_RESOLUTION_TEST`

The next stage may apply only those four frozen signatures to the f84-free
Voynich representation at the four charged resolutions. It must use whole-
folio holdout and one maxT family over signatures, resolutions, slots, and
operator families. No score may be called UNTIL, OR, polarity, exclusion, or
function word in Voynich unless independent transfer later justifies a
functional class; the initial output is only an anonymous construction score.

No Voynich row was opened or scored during this comparator pass. No f84 file,
row, image, text, or formal payload was opened, parsed, retained, or scored.
