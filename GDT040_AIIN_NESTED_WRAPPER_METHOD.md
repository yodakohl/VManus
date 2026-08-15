# GDT040 — AIIN nested-wrapper construction

## Question

Does GDT037/038 residual host DAIIN decompose into an ordered formal stack
`[ch/che/sh] + [d] + AIIN`, and does the compatibility of the two wrapper
dimensions transfer between Herbal Currier B and Currier-B Stars/Recipe?

The operation names are literal surface descriptions, not morphemes or
meanings.

## Inventory

All strict-consensus GDT016 groups with residual host `aiin` or `daiin` are
mapped to a common literal base AIIN. `outer_carrier=1` iff the frozen outer
wrapper is `ch`, `che`, or `sh`. `inner_d=1` iff a carrier-wrapped residual is
literal `daiin`, or a noncarrier group is frozen as `d|aiin`. Thus the four
surface cells are observable without resegmentation:

- AIIN without carrier or D;
- D+AIIN without carrier;
- carrier+AIIN without D;
- carrier+D+AIIN.

The “no carrier/no D” cell may still carry another frozen outer wrapper such
as `s` or `t`; it means absence only from the two dimensions tested here, not
a universally bare surface form.

Herbal-B, S/B, Herbal-A, and other registers are kept separate. f84r is
excluded before inventory construction.

## Tests

Within each physical folio, inner-D assignments are permuted exactly among
that folio's AIIN-family occurrences while carrier count and D count remain
fixed. Hypergeometric distributions are convolved across folios. This tests
carrier×D compatibility without treating occurrences as independent.

Two directional held-register predictions are also reported. A Jeffreys-smoothed
binary model for `P(inner_d | outer_carrier)` learned on Herbal-B predicts S/B,
and the reverse model predicts Herbal-B. The matched baseline uses one global
`P(inner_d)`. Raw held bits and a one-additional-parameter BIC penalty of
`0.5 log2(training events)` are shown.

For complete retained lines, field-position distributions are compared across
HB/S using probability weighted-Jaccard. This is a context diagnostic, not a
semantic-role assignment.

## Decision

A Currier-B nested construction is supported if the double cell occurs across
multiple folios in both HB and S/B, the combined folio-stratified compatibility
test is positive, at least one directional held-register prediction beats the
global model after its complexity penalty, and Herbal-A does not show the same
compatibility.

This can establish an ordered reusable formal stack. It cannot establish a
morpheme, POS, sound, language, plaintext, meaning, or translation. f84r
remains sealed.
