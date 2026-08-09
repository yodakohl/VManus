# SCP001 alternating star-color phase — preregistration

Status: **REGISTERED, TARGET UNSCORED**
Date: 2026-08-09

## Claim under test

On the nine source-frozen final-section pages, the red versus faded-yellow
center of a marginal star may condition the formal construction of the exact
manually marked line attached to that star.

This is not a claim that red or yellow means a recipe class, odd/even, a
number, a word, or any English concept. Under a full pass the maximum claim is
one marker-color-conditioned formal construction on this panel.

## Frozen evidence and unit

- `star_color_phase/source_panel.tsv`: 120 exact star-marker-to-line rows on
  nine pages / seven physical folios; 63 red and 57 yellow.
- Every visible-star count equals the retained manual ZL `<%>` marker count.
- Every locus has exactly one ZL3b, IT2a, and RF1b formal-interlinear row.
- f113r and f114v begin yellow; the other seven pages begin red. The 28
  reversed-phase rows prevent color from being identical to ordinal parity.
- Both the 2004 and 2014 scan families were inspected directly by a human.
  No OCR, image model, automated color classifier, crop distance, or image
  feature is admitted.

The physical unit is the exact line carrying the manual `<%>` marker. No
unmarked star is attached by proximity, and no missing marker is repaired.

## Frozen features

Features are extracted separately in ZL3b, IT2a, and RF1b from the already
pre-grounded formal interlinear. Surface strings and root identities are never
features.

1. `WORD_COUNT`
2. `LINE_CARRIER_ANY`
3. `LINE_CARRIER_T`
4. `LINE_CARRIER_D`
5. `LINE_CARRIER_S`
6. `ROLE_RATE_BOUND_D`
7. `ROLE_RATE_BOUND_E`
8. `ROLE_RATE_Q`
9. `ROLE_RATE_REL_I`
10. `ROLE_RATE_FREE_L`
11. `ROLE_RATE_FREE_R`
12. `FIRST_HAS_BOUND_D`
13. `FIRST_HAS_BOUND_E`
14. `FIRST_HAS_Q`
15. `FIRST_HAS_REL_I`
16. `FIRST_HAS_FREE_L`
17. `FIRST_HAS_FREE_R`
18. `EDGE_RATE_D_TO_Q`
19. `EDGE_RATE_E_TO_Q`

`ROLE_RATE_*` counts exact plus-delimited role atoms over the full line and
divides by stored word count. `FIRST_HAS_*` reads only the first written
word's plus-delimited formal role path. `Q` is any formal role atom beginning
`Q_`. `EDGE_RATE_*` counts confirmed `BOUND_D/E > Q_*` edges and divides by
stored word count. Line-carrier features use only the pre-grounded carrier
field. These names remain structural tags, not letters or English glosses.

A feature is eligible without color access only if its pagewise odd-minus-even
contrast has finite nonzero phase-orbit variance in every reading and nonzero
support on at least five pages and four physical folios in every reading.
Ineligible features remain reported and cannot be restored after target.

## Exact estimand and null

For each page, reading, and eligible feature, compute the mean on odd-numbered
markers minus the mean on even-numbered markers. A page-phase sign converts
this into red-minus-yellow: `+1` for red-first and `-1` for yellow-first.

Average page contrasts within physical folio, then average the seven physical
folios equally. For each reading/feature, standardize by its exact standard
deviation across all `2^9 = 512` synchronized whole-page phase assignments.
The robust statistic is the weakest same-direction reading:

`R = max(min(z_ZL,z_IT,z_RF), min(-z_ZL,-z_IT,-z_RF), 0)`.

The family statistic is the maximum `R` over all eligible features. Exact
tails are inclusive and contain the observed assignment. The global
red/yellow swap is deliberately direction-equivalent, so a perfect planted
signal has a minimum two-sided tail of `2/512` rather than a unique optimum.

## Mandatory gates

A feature passes only if all gates hold:

1. eligible under the target-blind support rule;
2. all three reading effects have one nonzero sign;
3. robust `R >= 2.0`;
4. inclusive raw robust tail `p <= .025`;
5. inclusive max-family tail `p <= .05`;
6. the seven red-first pages and the two yellow-first pages each have the same
   effect sign as the overall result in all three readings;
7. deleting each physical folio in turn preserves the same nonzero sign in
   all three readings;
8. anonymous controls and independent prescore reconstruction pass exactly;
9. final target arithmetic and bindings reconstruct independently.

The two-phase-stratum and deletion gates are vetoes; they cannot be traded for
a smaller p-value. No threshold, feature, page, marker, reading, weighting, or
null may change after target.

## Anonymous controls required before target

- exact 512-assignment enumeration and global-complement invariance;
- a distributed three-reading planted construction reaching `2/512`;
- a parity-only construction rejected by the reversed-phase veto;
- one-folio leverage rejected by deletion/support gates;
- one-reading disagreement rejected by the robust statistic;
- constant/degenerate features rejected target-blind;
- exact feature-extraction fixture;
- exact 360-row matrix cardinality plus duplicate/missing/page/locus guards;
- deterministic repeat and output hash;
- proof that no target phase field or target artifact was accessed.

After controls, a separate nonimporting audit must reconstruct the complete
feature matrix, eligibility, all controls, exact orbit, and target absence.
Only then may a separate target runner read `first_color` once.

## Claim ceiling

Even a complete pass supplies no star-color meaning, recipe classification,
ordinal numeral, lexeme, plant name, language identification, plaintext, or
translation. A failure closes only this fixed marker-color/formal-construction
association.
