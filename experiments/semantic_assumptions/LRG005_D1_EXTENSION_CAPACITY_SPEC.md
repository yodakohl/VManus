# LRG005 exact D1-extension capacity

Status: `FROZEN_ASSOCIATION_UNOPENED_CAPACITY`

## Distinct question

LRG004 confirmed that manual-label groups favor source-native initial family
`A` and avoid initial family `D`.  Earlier opening work already established
that the exact `D1 A1` onset is literal `qo...`, that exact prose remainders
can occur both bare and after `D A`, and that this prose-internal alternation
does not transfer to external position or neighboring-group context.  S97
also found no whole-string label-to-prose recurrence enrichment.

LRG005 must not repeat any of those tests.  Its only new question is whether,
among already-confirmed A-initial groups, a label-associated group has an
unusually high held-folio prose ratio of the exact form

`D1 + complete three-reading member sequence`

to the corresponding unextended complete member sequence.  A future pass
could support only a cross-register marked/bare construction relation.

## Capacity universe

Start from the exact B/P rows of the frozen LRG001 page-by-length panel.  Keep
strict source-native groups whose initial family is `A`.  Refine every original
cell by the exact triplet of first member codes in ZL3b, IT2a, and RF1b, then
keep only refined cells containing both manual `L` and confirmed-prose `P`
rows.  This conditioning prevents the future test from merely rediscovering
which `A` member labels prefer.

For each retained row with complete member-sequence triplet `S` on physical
folio `f`, define the label-blind capacity score

`log((count_-f(D1 + S) + 0.5) / (count_-f(S) + 0.5))`,

where counts use all strict confirmed-prose groups outside `f`.  Alternate
readings remain one exact triplet, never three observations.  Do not compare
these scores by `L/P` role during capacity construction.

The public masked panel may contain only opaque unit/cell IDs, physical folio,
and section.  A separate quota table stores only per-cell `L/P` counts.  It may
not emit a locus, page, surface, family sequence, member code, score, or row
role.

Capacity requires at least 500 rows, 60 refined cells, 13 folios, 100 label
rows, 300 prose rows, 50 score-variable cells containing 500 rows, 300 rows
with held-folio D1-extension support, and at least 25 variable cells in each of
B and P.  These are feasibility gates, not evidence of association.

## Required next boundary

A target remains forbidden until target-free calibration demonstrates exact
fixed-quota type-I control, distributed positive power, rejection of
one-folio/one-section/one-parity plants, rejection of generic recurrence and
initial-member leakage, and robustness in both section and folio parity.  The
real `L/P` score contrast must stay unopened during calibration.

Even a later pass would not identify a prefix, classifier, morpheme, word,
part of speech, sound, language, cipher operation, English meaning, plaintext,
or translation.
