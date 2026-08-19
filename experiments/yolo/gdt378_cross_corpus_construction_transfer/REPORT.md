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

## Voynich multi-resolution stage

After the comparator/signature freeze was published, the four anonymous
detectors were applied unchanged to 8,448 GDT327 source groups and 2,400 exact
field spans on 91 non-f84 physical folios. The charged atlas contains 24,356
signature×resolution candidates; 1,064 meet the 12-event, three-folio,
two-register power minimum.

No candidate is promoted by the frozen primary test. Event-level null mobility
is ample—6,539 atomic events, 6,612 complete-group events, and 1,005 field
events—but the **global max statistic is degenerate**. The required null
conditions on exact position and closure, while the charged grammar-slot
candidate `CMP_FUNCTION_03 / FROM_START_X_CLOSURE / 1__LINE_END` is itself
defined by those variables. Its statistic is therefore invariant. Every one
of 4,096 null worlds has the same maximum, 561.258338, and every powered
candidate receives primary maxT p=1. This is an identifiability failure of the
combined slot-aware null, not evidence that all 1,064 candidates lack signal.
The rule that a low-effective-capacity null cannot promote is honored.

An explicitly post-hoc, non-promoting diagnosis then removed only the
deterministic slot panels while retaining all 960 powered opaque-identity
candidates across atomic tuples, complete source groups, and field spans. Its
4,096-world identity-only null has 3,393 distinct serialized maxima. Twenty-
four candidates have diagnostic max-family p<=.05, but only two also satisfy
every non-null transfer gate—and they are the same formal object at two
resolutions:

| Anonymous detector | Resolution / opaque ID | Events | Folios | Registers | mean placement residual | held SSE gain | positive-gain folios | diagnostic maxT p |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| CMP_FUNCTION_04 | atomic tuple `2f1c5e56e8f0ff459065` | 435 | 84 | 5 | +0.109185 | +5.135914 | 72.6% | 0.000244 |
| CMP_FUNCTION_04 | source group `c502a1edfafbe3e54262` | 249 | 78 | 5 | +0.174045 | +7.397961 | 64.1% | 0.000244 |

The complete-group ID is exactly the `d`-wrapper realization of the atomic
tuple ID, so this is **one linked exploratory lead**, not two independent
findings. Its placement residual is positive on 91.7% of atomic-tuple folios
and 78.2% of complete-group folios; the complete group is positive in three
registers, while the atomic object is positive in all five. Exact field spans
have only seven powered types per signature and yield no corresponding lead.

`CMP_FUNCTION_04` was calibrated against a readable-comparator
function-word oracle, but that name is not transferred to Voynich. The lead
may simply identify an unusually recurrent formal group whose equality and
context profile resemble the comparator detector. Because the diagnostic was
introduced after discovering the primary null degeneracy, it cannot nominate
a Voynich functional class. No neighboring-slot, valency, scope, or operator
interpretation is authorized.

The first execution wrote all score/null tables byte-identically but failed
while serializing a NumPy integer into the result JSON. The published
correction records the old/new scorer hashes and the four pre-correction
output hashes; the rerun reproduced all four exactly. No scientific setting
changed.

## Decision

The comparator conclusion is:

`HEAD_SIGNATURE_NO_CROSS_DOMAIN_TRANSFER`

plus:

`NO_PRIMARY_TARGET_PROMOTION_NULL_DEGENERATE`

plus one `POSTHOC_NONPROMOTING_OPAQUE_FORMAL_LEAD` represented at two linked
resolutions. GDT378 does not license a `HEAD_SLOT` or any of the readable
comparator functions. A confirmation would require a genuinely untouched
non-f84 target or independently new evidence; the already exposed 91-folio
panel cannot be repartitioned after the lead is known.

No f84 file, row, image, text, or formal payload was opened, parsed, retained,
or scored in either stage. Independent retained-output validation passes 41/41
checks.
