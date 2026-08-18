# GDT307 — selected renderer-operation domain stability

## Purpose and prior overlap

GDT303 selected three exact same-host renderer operations with transferable
physical position deltas across opaque hosts: `ch->s`, `d->s`, and
`NONE->q`.  GDT307 asks whether each selected operation keeps its positional
delta when learned outside and evaluated inside a held manuscript domain.

This is not an independent discovery test: the operation family was selected
using the complete GDT303 corpus.  It is a frozen post-selection stability
analysis.  It differs from GDT289's failed global wrapper rule by conditioning
on the exact one-field operation and exact same-host surface pair.

## Score-blind fold freeze

Use only GDT303's published pair rows for the three operations.  For each of
`section`, `register`, `Currier`, and `hand`, retain a pair/held-domain cell
only when both exact forms have at least two events inside the held domain and
at least two events outside it.  Selection may read identity, domain, and
support only; it may not read group position.

## Frozen score

For every retained pair, compute target-minus-source physical
`FIRST/MIDDLE/LAST` probability vectors separately in train and held events.
Average multiple pairs equally within operation × domain type × held value ×
opaque host.  The transfer statistic is the equal-cell mean dot product of
the train and held vectors; direction accuracy is the fraction of host-domain
cells with positive dot product.

Use 8,192 deterministic held-vector sign reversals.  Standardize each of the
12 operation×domain statistics by its null and report a max-12 tail.

An operation is `DOMAIN_STABLE` only if both held-section and held-hand means
are positive, both direction accuracies are at least .60, and at least one of
their max-12 p-values is at most .05.  Otherwise classify it
`DOMAIN_MIXED_OR_UNSTABLE`.  Register and Currier are fixed sensitivities.

## Claim ceiling

At most this establishes domain stability of a selected formal positional
operation.  It does not establish a morpheme, grammatical category, semantic
role, sound, language, plaintext, meaning, or translation.  No f84 row may be
opened, parsed, retained, joined, or scored.
