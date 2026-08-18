# GDT292 — right-family closure channel

## Question

Does the frozen `RIGHT_FAMILY` layer predict the same group's formal closure
architecture after controlling layout, opaque host, wrapper, local frame, and
inner-D?  A transferable positive result would support the GDT288 operational
ordering in which right-side rendering participates in closing a field or
line, rather than behaving as an autonomous payload coordinate.

This is deliberately a same-group, parser-coupled formal test.  It cannot by
itself prove causal order, linguistic suffixation, or content neutrality.

## Frozen population and outcome

Use the same eight 8,448-event f84-free panels as GDT286--291.  The categorical
target is the exact four-bit tuple:

`DY closure | B3 | physical line close | paragraph close`.

There are nine observed Voynich classes.  Hold out one complete physical folio
for every prediction.  No target-folio closure outcome is used as history.

## Frozen hierarchical predictors

Use Dirichlet-1/2 global smoothing and a fixed 11-event prior at each step:

1. `LAYOUT_CONTEXT`: section, Currier, hand, register, within-field position,
   record-ordinal bucket, field-ordinal bucket, physical group position, and
   host length;
2. `EXACT_HOST`: opaque PAGE_HOST identity;
3. `OUTER_LOCAL_CONTEXT`: exact host, wrapper, local frame, and inner-D;
4. `RIGHT_FAMILY`: add the exact frozen right-family class.

The primary effect is `OUTER_LOCAL_CONTEXT bits - RIGHT_FAMILY bits`.
Report per-folio, per-right-family, per-closure-class, per-panel, held-section,
and held-hand scores.  Repeat prior masses 5 and 22 on Voynich as fixed
sensitivities.

## Frozen null

After held-folio probability vectors are frozen, permute closure outcomes
within exact `physical folio × section × Currier × hand × register ×
within-field position × record bucket × field bucket × physical group position
× host length × wrapper × local frame × inner-D` strata.  This preserves the
baseline opportunity and every outcome count while destroying right-family to
closure alignment.  Use 64 shared worlds with seed family
`GDT292_HELD_CLOSURE_ALIGNMENT|panel|world|stratum`.

Report local and standardized max-eight p-values over panels with positive null
variance.  Zero-variance panels retain descriptive scores and receive
`NA_ZERO_NULL_VARIANCE`.

## Frozen decision

Call `RIGHT_FAMILY_CLOSURE_CHANNEL_SUPPORTED` only if Voynich has positive
gain, positive gain for at least four of its six right-family classes, positive
gain on at least 60 of 91 held folios, positive held-section and held-hand
gains, and variable-family maxT `p <= .05`.  Otherwise call
`RIGHT_FAMILY_CLOSURE_CHANNEL_WEAK_OR_LOCAL`.

## Claim ceiling and seal

At most this identifies a transferable formal association between right-side
rendering and closure architecture.  It cannot establish a suffix, grammar
name, lexical class, abbreviation, sound, language, meaning, plaintext, or
translation.  Only the published f84-free native event inventory is read.  No
f84 row may be opened, parsed, retained, joined, or scored.
