# GDT295 — online page-local renderer adaptation

## Question

Does a recurrent opaque host use a page-local renderer table, beyond the
cross-folio host×position distribution supported by GDT293--294?  This tests a
central page-conditioned-codebook prediction without predicting PAGE_HOST
identity or using neighboring hosts.

## Frozen online population

Use the same eight f84-free native panels.  Preserve their published event
order.  Within each page, group consecutive events by physical locus.  Score
every event on a physical line before any event from that line updates page
history.

An event is eligible only if its exact host occurs on another physical folio
and has occurred on an earlier physical line of the same page.  Five panels
have capacity; the three Latin graphematic panels have zero eligible events
under this same-page definition and remain explicitly unscored.

The target is the exact joint
`wrapper|frame|inner-D|right|DY|B3` renderer tuple.

## Frozen models

All outside-folio distributions use the GDT294 layout/boundary/exact-host/
host×position hierarchy.  The two online extensions use only earlier physical
lines of the held page:

1. `CROSS_FOLIO_HOST_X_POSITION`;
2. `PAGE_LOCAL_HOST`: exact page+host renderer counts backed off to model 1;
3. `PAGE_LOCAL_HOST_X_POSITION`: exact page+host+within-field-position counts
   backed off to model 2.

Use Dirichlet-1/2 global smoothing and prior mass 11 throughout.  Prior masses
5 and 22 are fixed Voynich sensitivities.  No same-line, future-line,
neighboring-host, host-glyph, substring, semantic, or f84 information enters.

## Frozen null and decision

After every online probability vector is frozen, permute eligible renderer
outcomes within exact page+host strata.  This preserves page-local host
membership and outcome inventories while disturbing their online/position
alignment.  Use 64 shared worlds and standardized max-five over positive-
variance powered panels.

Call `PAGE_LOCAL_RENDERER_ADAPTATION_SUPPORTED` only if Voynich's model-1 to
model-3 gain is positive, at least 100/153 eligible pages are positive, at
least four of six sections are positive, both prior sensitivities are
positive, and corrected `p <= .05`.  Otherwise call
`PAGE_LOCAL_RENDERER_ADAPTATION_WEAK_OR_LOCAL`.

## Claim ceiling and seal

At most this supports online page-local adaptation of a parser-defined
renderer distribution.  It cannot establish a page vocabulary meaning,
lexical identity, code value, word, language, plaintext, or translation.  No
f84 row may be opened, parsed, retained, joined, or scored.
