# GDT303 — matched renderer-operation position deltas

## Question

GDT300 rejected one global renderer predictor, while GDT302 found a small set
of strong host-specific positional contrasts.  Test the narrower compositional
claim: when two complete forms share an opaque host and differ in exactly one
frozen renderer field, does that directed renderer change predict the same
`FIRST/MIDDLE/LAST` probability delta on an unseen host?

No meaning is assigned.  This is cross-host prediction of a physical-position
delta, not prediction of a word or interpretation.

## Frozen pairs and direction

Use the exact 6,844-event GDT299 population and renderer fields
`wrapper, local_frame, inner_d, right_family, dy_closure, b3`.  A form needs at
least 5 events on 3 folios.  Pair two forms of the same host only when their
renderer tuples differ in exactly one field.  If one value is neutral
`NONE/0`, direct neutral→nonneutral; otherwise use lexical value order.  Retain
an operation only with at least 4 pairs on 4 distinct hosts.  Pair selection
and direction use no position outcomes.

For each operation and host, average all pair deltas in the three physical
role rates.  In leave-one-host-out folds, predict the held host delta by the
equal-host mean delta from all other hosts.  Compare squared error against a
zero-delta baseline and report directional dot-product accuracy.

## Null and decision

In 4,096 deterministic worlds, independently reverse the complete delta vector
for each operation×host, preserving its magnitude and host support while
destroying the directed operation convention.  Use inclusive local and max-
family tails across every powered operation.  Label an operation
`TRANSFERRED_DELTA` only if gain is positive, at least 70% of held hosts have a
positive predicted/observed dot product, and max-family `p <= .05`.
`WEAK_DELTA` requires positive gain without all gates; otherwise label
`FAILED_DELTA`.

## Claim ceiling

At most this identifies a frozen renderer-field change with a reusable
physical-position delta across opaque hosts.  It establishes no morpheme,
grammatical function, semantic role, sound, language, meaning, plaintext, or
translation.  No f84 row may be opened, parsed, retained, joined, or scored.
