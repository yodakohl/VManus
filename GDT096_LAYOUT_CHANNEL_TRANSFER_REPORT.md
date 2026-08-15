# GDT096 — layout-channel transfer

## Outcome

**GDT095_HOST_WRAPPER_LAYOUT_LEAD_FAILS_BUT_PAGE_HOST_MARGIN_HAS_LOW_CAPACITY_TRANSFER**

The exact GDT095 layout regex and representation grid were frozen, trained on
83 UNHEDGED section-P plant labels, and applied without target refitting to all
35 HEDGED labels. Every prediction excludes its physical folio. Only four
targets contain the frozen position vocabulary.

The GDT095 PAGE_HOST×WRAPPER lead loses 1.325 bits and
is negative on all five target folios. Its exact within-folio rank is
p=0.7051. PAGE_HOST trigrams instead gain
+6.183 bits on all five folios, versus raw trigrams at
+4.534; PAGE_HOST retains +2.861
bits after the ten-way selector and has exact max p
0.0011. The advantage over raw is only
+1.649 bits and the HEDGED endpoint contains
four positives, so this is a low-capacity HPR2 marginal lead, not semantic
localization. The frozen construction interaction does not transfer.

This is archived-data stress testing, not a pristine validation. HEDGED rows
are a different annotation-quality stratum and the source corpus was already
available. The miss nevertheless prevents promotion of the GDT095 association.
No role or gloss is assigned. f84r was absent and untouched.
