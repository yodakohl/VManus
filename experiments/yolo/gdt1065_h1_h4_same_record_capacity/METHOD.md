# GDT1065 method

## Question

Do any of the thirteen already mapped deep-page records contain an H1+body
opening followed by H4+the exact same body at a line-internal position?

## Inputs

The fixed GDT735 96-form/24-body grid and GDT791 guarded 5,866-occurrence
spine, with SHA-256 values in `src/run.py` and `artifacts/RESULT.json`.
Independent validation uses GDT790's 123-line image-aware artifact. All data
were already admitted; no raw mixed sealed table is opened here.

## Method

The [pre-join decision note](../../../research_registry/decisions/idea643_same_record_capacity_20260928.md)
fixed the 13 GDT791 records on f77r/f82r/f83r and the 24 GDT735 bodies before
the first join. Select running-prose tokens in those records, then compare
complete exact forms. Enumerate every ordered H1/H4 same-body pair, retaining
both positions and all intervening forms. The strict capacity gate requires
H1 at token 1 of its physical record and H4 later inside a line. The validator
rebuilds each record from GDT790's independent line representation and checks
the entire pair set, not only the zero strict count.

## Decision rule and claim ceiling

Zero strict pairs means no capacity for IDEA643's opening-to-property reading
in this fixed 13-record frame. A strict pair would only permit a later
semantic test after an independently bound property; it would not identify a
referent by itself. GDT737's failed held-body H1/H4 affinity remains in force.
This is a ZL3b structural screen; alternate readings are not independent
manuscripts and no word meaning, decoder, source or holdout is tested.
