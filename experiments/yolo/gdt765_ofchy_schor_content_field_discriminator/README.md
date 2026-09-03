# GDT765 — `ofchy` and `schor` content fields

Status: `PARTIAL__6_TARGET_OCCURRENCES__OFCHY_3_OF3_NOMINAL_SPECIFICATION_HEAD__SELECT_BLUETENMASSE_C0__SCHOR_3_ITEM_HEADS__SELECT_BLUETENSTAND_C1__25_OFCH_PREFIX__13_FCHY_SUFFIX__67_CHOR_VALUE_PAIRS__12_H_X_DAIIN__F22R_TWO_PARALLEL_TARGET_FIELDS__CFHY_TRANSITION_C1__ZERO_CONFIRMED_LEXEMES__NO_NEW_PAGE`

All three exact `ofchy` positions behave as nominal material/preparation heads,
not qualities, units, or actions. The portable default is “named drug in base
form”; the concrete working default is **Blütenmasse**. All three exact
`schor` positions behave as item/subentry heads. Its portable default is
“plant-part item”; the concrete working default is **Blütenstand**.

Reproduce with:

```bash
./vmanus-exp run experiments/yolo/gdt765_ofchy_schor_content_field_discriminator
./vmanus-exp validate experiments/yolo/gdt765_ofchy_schor_content_field_discriminator
```

The exact f22r.4 working line and the confidence/evidence split are in
`REPORT.md`. No new page is opened and no component meaning is exported.
