# FT procedure source audit

**The frozen B TSV conserves all 655 source groups.** The original frozen JSON-ledger interface reports `FAIL_ACCOUNTING` because it recognizes zero rows: B stores its ledger in `FT_PROCEDURE_DERIVATION.tsv`, rather than a supported JSON ledger list. That interface failure is retained unchanged in `FT_PROCEDURE_ACCOUNTING.json`; it is not evidence that source groups were omitted or that a meaning failed.

The separate bounded source audit passes 56 checks with zero errors. It verifies all 13 `FT_DRAFT_INPUTS.json` hashes, the unchanged packet/validator/original source-only report, B's declared packet and TSV hashes, and a guarded projection selecting only the 11 source identity columns. The selector is `locus` with all 45 explicit allow-values before payload. Its receipt is selected=655, skipped-forbidden=0, skipped-not-allowed=0. No semantic contribution, type, argument, state, status or instantiation column was read.

| Source scope | ZL3b | IT2a | RF1b |
|---|---:|---:|---:|
| Lower f83 complete records plus four captions |126|123|127|
| f77 full predecessor record plus label |93|93|93|
| Total source rows |219|216|220|

All 655 IDs are unique and equal the packet's complete ID set. Every row's unit, reader, locus, group ordinal, unit position, exact raw group, left/right native separator and paragraph flags matches the frozen packet. Every unit/read sequence retains native source order; every repeated whole preserves the same occurrence IDs and order. All 45 loci are present. The 376 lower groups and 279 predecessor groups are **bound source counts**, not validated interpretation or execution counts.

Reproduce the frozen interface run:

```sh
python research_registry/proposals/laufenberg_f85r2_20260926/source_supply_20260929/FT_ACCOUNTING_VALIDATOR.py --ledger FT_AUTHOR_PROCEDURE.json --output FT_PROCEDURE_ACCOUNTING.json
```

The separate JSON records the exact guarded TSV command, projection hash, input hashes, all source-only checks and repeated-whole ID index. Its row comparison maps TSV `raw_group` to packet `ivtff_group_raw`, compares all other projected fields directly as strings, and compares each unit/read ID sequence against the packet. This is a narrow independent schema adapter, not a decoder or replacement of the frozen validator. Both outcomes remain explicit.

No B/source/validator edits, semantic ranking, author prose inspection, new manuscript access, Git action or global registry update. No grammar, meaning, authored state transition, image owner, interpreted-status count or completeness-of-reading PASS is claimed. Confirmed meanings added: 0.
