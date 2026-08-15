# GDT064 — cross-wrapper PAGE_HOST page-context preservation

## Outcome

**CROSS_WRAPPER_PAGE_CONTEXT_PRESERVATION_SUPPORTED**

The inventory yields 10,705 page×host×wrapper units and
45,942 cross-folio exact-host pairs with a real matched control.
The corrected implementation excludes 140 formerly retained zero-control
pairs.  Across 619 host×register cells,
different-wrapper exact-host context similarity averages 0.21247
versus 0.20821 for matched different-host controls; 373/619 cells
are positive (descriptive exact sign p=3.74605e-07).  The absolute gain is
+0.00426, or +2.04% of the matched-control similarity.  In the
460 cells with both pair types, same-wrapper exact-host similarity
averages 0.21345; different-wrapper minus same-wrapper is
-0.00098.

GDT063's `d` and `ok` cells are retained explicitly but are not allowed to set
the manuscript-wide statistic.  `ok` is positive against its matched control
in 5/5 register cells; `d` in
4/5.  Pair observations share pages and the sign
test treats host×register cells as exchangeable, so its p-value is a ranking
diagnostic rather than independent confirmation.  This is an internal page-inventory result;
it can support renderer invariance but cannot validate the archived external
annotation leads.  No role, gloss, word, morpheme, POS, sound, language,
plaintext, meaning, or translation is assigned.  f84r was excluded before
aggregation and not opened, retained, queried, joined, or scored.
