# GDT430 method

## Question

Which currently absent component recipes are genuinely useful predictions from
the nineteen-core substitution system, rather than arbitrary one-step variants?

## Inputs

- GDT416's 1,268 observed component-recipe types in 4,576 events;
- GDT413's current component dictionary;
- GDT428–GDT429's exact within-family substitution contrasts.

## Method

Replace exactly one root inside each observed recipe by another root in the
same substitution family: CH/S, K/OK/P, SH/CHD, Y/AIIN/AIN/OR,
AL/AR/L/AIR, or OL/OT. T and R remain separate and are never substituted.

Deduplicate the resulting recipes and count how many distinct observed
neighbours lead to each candidate. Use candidates that are already observed to
calibrate the neighbour count. Separately hide each of the 24 stored page keys
and replay every recipe unique to that page from the other pages.

## Decision rule and claim ceiling

- one neighbour: do not predict;
- two neighbours: narrow amber;
- three neighbours: strong amber;
- four or more neighbours: high-priority amber.

Only the component recipe and its fixed root reading are predicted. The surface
spelling is never generated, and an existing surface collision is not repaired
by force. This is a creative prospective deck, not confirmed plaintext or a
language identification.
