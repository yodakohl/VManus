# GDT096 — layout-channel transfer

## Outcome

**GDT095_HOST_WRAPPER_LAYOUT_LEAD_FAILS_HEDGED_STRATUM_TRANSFER**

The exact GDT095 layout regex and representation grid were frozen, trained on
83 UNHEDGED section-P plant labels, and applied without target refitting to all
35 HEDGED labels. Every prediction excludes its physical folio. Only four
targets contain the frozen position vocabulary.

The GDT095 PAGE_HOST×WRAPPER lead loses 8.363 bits and
is negative on all five target folios. Its exact within-folio rank is
p=0.7051. Raw and PAGE_HOST marginal trigrams are the
best sensitivities at +4.519 and +4.286
bits; both narrowly retain about one bit after the ten-way selector, and the
max-representation exact p is 0.0101.
This four-positive HEDGED endpoint is too small for semantic localization, and
raw slightly beats PAGE_HOST. The frozen construction interaction therefore
does not transfer to this certainty stratum; the surviving weak association
is ordinary string-level rather than HPR2-specific.

This is archived-data stress testing, not a pristine validation. HEDGED rows
are a different annotation-quality stratum and the source corpus was already
available. The miss nevertheless prevents promotion of the GDT095 association.
No role or gloss is assigned. f84r was absent and untouched.
