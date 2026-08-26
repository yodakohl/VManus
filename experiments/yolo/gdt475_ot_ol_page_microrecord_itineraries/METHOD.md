# GDT475 method

## Question

Do `OT=DANACH` and `OL=FORTSETZEN` connect successive GDT474 locus bundles in
different ways, and can that distinction turn the 146 bundles into complete
page-level microrecords without changing a meaning or selected reading?

## Inputs

- GDT474's 146 bundle triptych and selected readings;
- GDT474's 183 event triptych with exact recipe order;
- GDT429's unchanged OT/OL operational profiles.

## Method

Every OT and OL atom is classified by exact position:

- first atom of the first event in a bundle;
- first atom of a later event in that bundle;
- internal atom of an event.

At a page boundary the first bundle begins a record. Elsewhere a leading OT
starts a next sibling record, a leading OL continues the previous record, and
an unmarked visible locus starts a new record. A nonleading OT/OL remains inside
its visible bundle and never changes the cross-locus boundary. Thus the rule is
scope-sensitive but deterministic:

- `OT` opens the next event/record at the scope where it appears;
- `OL` keeps the active event/record going at the scope where it appears.

The unchanged GDT474 selected reading is then printed under its resulting
record. Consecutive leading-OL bundles form one cross-locus continuation chain.

## Decision rule and claim ceiling

The pass is complete only if all 183 events and 146 bundles replay in order,
all 69 order-root occurrences are located exactly, every bundle belongs to one
of six complete page itineraries, record continuation uses only a visibly
leading OL, and no selected GDT474 reading changes.

This is a creative stream interpretation of the fixed `DANACH/FORTSETZEN`
values, not confirmed historical syntax. It adds no component meaning, learned
name, selected model, recipe, spelling, event, page, object identity, plaintext,
language or confirmed lexeme.
