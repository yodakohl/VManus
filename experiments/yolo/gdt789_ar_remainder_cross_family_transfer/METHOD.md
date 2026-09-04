# GDT789 method

## Question

Does the independently useful complete word `ar`, provisionally rendered
**Anteil**, carry a reusable role into observed complete `Xar` forms, or does
the family require learned and form-specific wholes?

The experiment tests that practical value.  It does not assume that EVA `a`
or `r` is a medieval letter, sound, abbreviation, or morpheme.

## Target population and guarded cache

The GDT782 guarded loader reconstructs the inherited 179-page cache through
`vmanus-exp query-tsv`; forbidden `f84*` selectors are rejected before any
other field is materialised.  ZL3b, IT2a, and RF1b are alternate readings of
one manuscript and jointly license a reader-exact written occurrence, never
three semantic votes.

The target uses the longest-ending partition already introduced by GDT788:
all raw complete surfaces ending `ar`, except surfaces ending the longer
`dar`.  This prevents GDT789 from silently counting the DAL/DAR square twice.
The resulting target is 285 raw forms/1,698 tokens and 225 reader-exact
forms/1,348 tokens.

## New AR/OR transfer comparison

For every X with at least two reader-exact `Xar` and `Xor` tokens on at least
two physical folios per arm, GDT789 predicts the complete target whole with:

```text
ADD_AR(Xar) = normalize(clip(P(Xor) + P(ar) - P(or)))
```

This is arithmetic over profiles of four complete observed words.  It does
not segment `Xar`.  Each profile is balanced first inside physical folio; each
X type then gets one vote.

There are 47 robust X types. Two mechanically defined, partly overlapping
31-type views are reported. They are sensitivity cohorts, not independent
replications: 16 prefixes occur in both, and each has 15 exclusive prefixes.

- `SUPPORT_PRIMARY_31`: every `Xar` and `Xor` arm has at least three tokens on
  three folios;
- `HISTORICAL_EXCLUSION_31`: robust types not used as GDT654 calibration shells
  or GDT788 primary prefixes, after removing `*dar` targets.

ADD_AR competes with the complete same-X sister `Xor` and a mean of five clean
learned wholes ranked only by length, exact-frequency bin, physical-folio bin,
edit distance, and lexical tie-break. Target similarity and German meaning
are unused in ranking. Donor eligibility is nevertheless semantically
sanitised first: only clean W2/W3 wholes outside the mask survive, and HOLD or
retired-patient displays are excluded. Standalone X is a diagnostic when it
exists, not a common gate.

Scores are target-field-defined Jensen–Shannon similarities for full,
structural, register-free local, semantic-only, and immediate-value-binding
views.  They are not probabilities.

## Independent R/N level grids

Two separate surface parallelograms ask whether an R-versus-N role survives
across adjacent written index levels:

```text
RN12(Xar)   = normalize(clip(P(Xan)   + P(Xair) - P(Xain)))
RN23(Xaiir) = normalize(clip(P(Xaiin) + P(Xair) - P(Xain)))
```

RN12 has seven robust X rows and RN23 six.  All four cells in a row are real
complete words with at least two exact tokens on two folios.  The labels R/N
are analyst shorthand for surface contrasts only.

## Leakage mask and concrete role diagnostic

The semantic mask is the union of:

- GDT788's 996-surface mask;
- every raw cached surface ending `ar/or/an/ain/air/aiin/aiir/aiiin`;
- GDT734 cards whose lineage includes GDT654, GDT693, GDT724, GDT759,
  GDT760, or GDT788.

The union has 2,140 surfaces and is excluded from semantic-neighbour fields
and learned-whole donors.  This prevents old Anteil/Portion prose from scoring
its own descendants.

A secondary role diagnostic constructs PART, AMOUNT, and VALUE prototypes
from 253 clean W2/W3 complete-whole working cards outside the mask.  Each
surface gets one vote and is classified leave-one-surface-out.  The diagnostic
may name a target role only if every class recalls at least .50.  It fails that
condition because AMOUNT recall is .273, so its `ar→VALUE` output remains a
visible rival rather than a dictionary decision.

## Boundaries, constructions, and working cards

All adjacent `X ar` spans are inventoried.  Strict spans require both tokens
reader-exact and the ordered pair present in all three current readings.
Stolfi supplies a guarded boundary sensitivity only.  Every new relation row
is passed through `vmanus-exp check-edge-packet`; text order alone is
deliberately not score-ready visual evidence.

The construction deck separately counts `ar/or/s + ain/aiin/aiiin` and the
four `ar/or` nesting orders.  These can support a countable or value-bound head
without identifying a unit.

Every one of the 285 target forms receives a nonempty complete-whole working
card with confidence, evidence, counterevidence, and three semantic rivals.
Nineteen recurrent wholes have explicit short defaults. Because the role
selector fails its gate, none of its target labels becomes a preferred card;
they remain visible rivals and the other displays use replaceable recurrent,
singleton, or raw family priors. No card creates a renderer licence or
portable substring.

## Decision rule and ceiling

A portable AR role requires ADD_AR to beat both main controls in at least
21/31 rows in both primary cohorts and the additive R/N model to beat all
controls in at least 5/7 RN12 and 4/6 RN23 rows.  Structural-only success would
be `AR_OR_SHELL_BOUND`; otherwise the family is `WHOLE_ONLY`.

Executed outcome: 7/31, 8/31, 0/7, and 0/6, hence `WHOLE_ONLY`.

Ceiling: C2 observed complete-word and boundary facts; C1 formal AR/OR family
and the role of bare complete `ar`; C0 German complete-whole displays and
semantic rivals.  No confirmed lexeme, plaintext, unit, substance, EVA value,
free component, new page, image, OCR, transcription, `f84`, or `f84r`.
