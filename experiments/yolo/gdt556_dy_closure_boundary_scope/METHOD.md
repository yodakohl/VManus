# GDT556 method

## Question

Does the working root `DY=ABSCHLIESSEN` behave as a terminal closure marker
across all 30 already admitted pages, and does it close the entire statement,
a local step inside a continuing statement, or both according to position?

## Inputs

- the GDT407 4,576-event / 715-statement frozen 26-page prefix;
- the GDT539 546-event / 78-statement four-page edition.

The GDT407 mixed-source TSVs are read only through `./vmanus-exp query-tsv`
with the exact 26-page allow-list, explicit columns and an `f84` forbidden
prefix. The four current pages are disjoint. No new page is opened.

## Method

Join each event to its source statement and mark its ordinal, distance from the
statement end and recipe position of every `DY`. Classify a `DY` event as a
singleton closure, final-step closure, or internal local-step closure followed
by statement continuation. Retain the exact successor for every internal
case.

Compare `DY` with `OL`, `OT`, grade markers, execution `O` and `DA` on the same
event-finality table. Also compare final-event rates for `DY` versus non-`DY`,
inventory exact recipes that occur in more than one closure scope, and retain
current GDT539 action/argument state around internal `DY` events where those
fields are available.

## Decision rule and claim ceiling

Pass as a positional working audit if all 5,122 events and 793 statements join
exactly, every `DY` is counted once, its within-recipe position and successor
scope are explicit, and the old/current cohorts agree on the same classification
rules. The outcome may refine the editorial scope of “close” but may not change
the root value, recipe, statement boundary or German clause.

Position is supporting evidence for a working function, not recovered
plaintext or historical syntax. No new page, object, language, codebook,
segmentation, root or future-form license follows.
