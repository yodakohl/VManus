# GDT306 — disjoint q post-DY entry test

## Question

GDT305 prospectively found that neutral→`q` raises parser-defined field-first
rate while lowering physical line-first rate.  GDT306 asks the direct
mechanistic question: on a third, disjoint set of exact surfaces, is `q`
enriched immediately after a preceding DY-closed group rather than at line
start?

No semantic or linguistic function is assigned.

## Score-blind freeze

Use f84-free `VOYNICH_REFERENCE` events on lines with at least two groups.
Exclude every exact surface appearing in either GDT303 or GDT305.  Retain only
events whose wrapper is `NONE` or `q` and whose exact matching cell contains
both states.  The primary cell is:

`PAGE_HOST × local_frame × inner_d × right_family × own_DY × B3 × register × section × Currier × hand`.

No group position, field position, record ordinal, preceding-group field, or
close outcome may enter selection.  All eligible cells and observations are
frozen before scoring, including one-occurrence forms.

## Frozen predictions

Primary: target-minus-source (`q` minus `NONE`) probability of
`PRECEDED_BY_DY` is positive, where the endpoint is rebuilt mechanically from
the immediately preceding physical group on the same locus.

Secondary: `q` minus `NONE` physical `LINE_START` probability is negative.

Compute event rates inside each matching cell and average cells equally.
An exact within-cell wrapper permutation is the primary null.  Report two
fixed opportunity sensitivities without changing the decision:

1. exact physical-folio-conditioned cells;
2. exact source-group-count-conditioned cells.

The result is `Q_POST_DY_ENTRY_TRANSFERS` only when the primary delta is
positive, its exact one-sided p is at most .05, and both sensitivity deltas are
positive.  Otherwise report `Q_POST_DY_ENTRY_WEAK_OR_FAILED`.

## Claim ceiling

At most this supports a formal q-conditioned transition after a DY closure in
the frozen HPR2 representation.  It does not establish a morpheme, grammatical
category, discourse role, sound, language, plaintext, meaning, or translation.
No f84 row may be opened, parsed, retained, joined, or scored.
