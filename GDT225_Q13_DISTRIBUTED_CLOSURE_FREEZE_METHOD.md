# GDT225 — q13 distributed-closure mechanism freeze

## Motivation

GDT224 found that q13 has a readable-recipe-like aggregate balance of
clause-sized and short-argument-sized fields, but only 0.482 of its records end
in the externally learned closer-like class versus 0.783 for same-hand
Herbal-B.  GDT225 asks whether q13 closes records through already existing
document-compiler channels outside that short final field.

## Frozen mechanisms

Exactly two pre-existing channels are allowed:

1. `FINAL_LINE_B3`: the frozen GDT046 B3-like closing state is present on the
   final physical line of the mechanical record;
2. `FOLLOWING_LABEL_BLOCK`: at least one existing GDT012 human-annotated label
   has a source locus number after the record's final prose line and before the
   next registered prose line on that page (or before page end for the last
   record).

Their union is `DISTRIBUTED_CLOSURE_PROXY`.  The rule is source-order only.  It
does not assert spatial adjacency, ownership, a cross-reference, or a label
meaning.  No other wrapper, host, module, family, line ending, visual class, or
distance window may be selected after scoring.

## Frozen panel and predictions

The panel is exactly the 33 q13 and 22 Herbal-B records in the public GDT224
projection.  A record has a `MISSING_FIELD_CLOSER` when its final GDT224 field
is not `RECORD_CLOSER_LIKE`.

Three directions are fixed before the B3/label joins are inspected:

1. among missing-field-closer records, q13 has a higher distributed-proxy rate
   than Herbal-B;
2. in q13, the proxy is more frequent among missing-field-closer records than
   among field-closer records;
3. counting either a field closer or the proxy as an expanded closure reduces
   the q13-versus-Herbal closure deficit by at least half.

Report B3 and following-label components separately, exact 2x2 Fisher tests,
physical-folio leave-one-out directions, and source-gap distributions.  Because
the hypothesis follows GDT224's revealed deficit, it is a prospective
mechanism test on an exposed panel, not independent discovery.

## Decision and ceiling

All three directions plus at least eight of nine q13 folio deletions are
required for `DISTRIBUTED_CLOSURE_MECHANISM_PROVISIONAL`.  Otherwise report
`DISTRIBUTED_CLOSURE_PARTIAL_OR_GENERIC` or `DISTRIBUTED_CLOSURE_NOT_SUPPORTED`.

Even a pass can establish only that q13 record closure is distributed across
formal/text-layout channels.  It cannot establish that a label is a terminator,
index, word, semantic value, or translation.  f84r and every f84 row are
excluded and not accessed.
