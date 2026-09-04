# GDT803 method — recurrent complete context versus rarity

## Question

Do any recurrent complete left/right neighbours of GDT800's paired `Xl/Xm`
targets form a repeated construction that is more informative than neighbour
rarity, target-family propensity and physical line position?  If so, do broad
field roles assigned before GDT803 yield a useful working three-slot reading?

This is a text-internal continuation of GDT800–GDT802.  GDT799's clothing
observations are not inputs and grant no meaning.

## Inputs and scope

The source lock fixes five already published artifacts: GDT802's 4,137-event
neighbour atlas, 275 context-coefficient rows and held-folio predictions;
GDT800's section/language/hand metadata; and GDT734's cached exact ZL3b lines.
`CONTEXT_ROLE_PRIORS.tsv` records fourteen broad, replaceable roles inherited
from GDT730/GDT744/GDT759.  It is a semantic comparison instrument, not a
dictionary.

No new page, image or transcription is opened.  `f84` and `f84r` remain
forbidden and are checked before analysis.

## Stable deck and core groups

The stable deck contains the fourteen side/surface cells with 25/25 crossed
fold eligibility, one coefficient sign throughout those folds and at least 20
cache-rest events.  Two exploratory `l`-favouring groups are compacted:

- left `qokeey/qokedy/qokeedy/qokain`;
- right `daiin/shedy/chedy`.

The right group is the high-capacity numerical cluster (at least 90 events,
30 stems, 35 folios and residual beta at most -0.35).  The left group is an
explicit post-outcome cohort of four `qok`-near complete surfaces; the same
numeric screen would also admit left `shedy`.  Therefore all group
enumerations are exploratory ranks, never p-values.

## Outcome-blind exposure controls

For every complete surface define

```text
v = (ln(events), ln(target stems), ln(physical folios)).
```

Euclidean distance in this space selects a unique injective control for each
candidate on the same side.  Neither terminal outcomes, coefficients nor
residuals enter matching.  The chosen controls are
`al/shedy/shol/ar` on the left and `chol/ol/dy` on the right.

Candidate and control events receive the already held-folio GDT802
position-plus-stem prediction `page_s`.  Their residual is
`I(terminal=m)-page_s`.  Candidate groups are compared with all unique
injective control sets obtainable from the 5, 8 and 10 nearest exposure
matches.  The two-sided bracket comparison crosses all 1,595 left and 120
right ten-nearest sets and counts events, `m`, stems and folios from an exact
left/target/right join.

## Exact pairing

Candidate events are paired to chosen control events inside the same target
stem and six-level distance cell.  Each event is used once and the two events
must be on different physical folios.  `candidate=l/control=m` supports the
lead; the reverse contradicts it; equal terminals tie.  Deterministic sorted
augmenting-path matching makes the artifact reproducible.

## Distributed identity-versus-rarity audit

For each test event and side, training excludes both its complete physical
folio and its target stem.  Within its exact distance cell, a complete context
is eligible with at least five training events, three stems and three folios.
The identity score is its alpha-20 shrunk `m` log-odds relative to the distance
baseline.  The outcome-blind rarity score is negative training count.

Every cross-folio `l/m` pair inside
`section × language × hand × stem × distance_cell` receives both AUC scores.
Micro AUC weights pairs; macro AUC weights strata.  Two hundred thousand fixed
seed sign flips act on whole stratum deltas.  Section/language/hand results
are retained as sensitivity, not semantic classes.

## Field bridge and claim ceiling

The exact two-sided pattern may receive the working display
`quality/condition + carrier/entry + value/state/result` because all seven
outer wholes already had broad quality/state/value rivals.  A descriptive
record, prescriptive record and opaque-address reading remain coequal rivals.

No final EVA sign becomes a morpheme.  No complete context receives a portable
word meaning.  The pass cannot establish terminal equivalence, a component,
language, sound, cipher, plaintext, lexeme, ingredient, plant, disease,
person, unit or translation.
