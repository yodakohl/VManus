# GDT475 — OT/OL page microrecord itineraries

Status: `OT_OPENS_EVENTS_AND_NEXT_SIBLINGS__OL_CONTINUES_RECORDS_OR_STAYS_INTERNAL`

GDT475 connects the 146 GDT474 locus bundles into six complete page
itineraries. The two order roots now have sharply different stream behaviour:

- all 41 `OT=DANACH` occurrences open an event; 40 open the bundle and one
  opens a later card in the same locus;
- `OL=FORTSETZEN` occurs 28 times: eleven bundle-leading, one later-card-leading
  and sixteen card-internal.

The eleven bundle-leading OL cards attach to the previous bundle. The complete
stream therefore forms 135 microrecords, including eight explicit two- or
three-locus continuation chains.

Read the six pages in
[`artifacts/GDT475_SIX_PAGE_MICRORECORD_ITINERARIES.md`](artifacts/GDT475_SIX_PAGE_MICRORECORD_ITINERARIES.md).

Rebuild and validate with:

```bash
python3 experiments/yolo/gdt475_ot_ol_page_microrecord_itineraries/src/run.py
python3 experiments/yolo/gdt475_ot_ol_page_microrecord_itineraries/src/validate.py
```
