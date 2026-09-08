# GDT877 — Four raw construction anchors; one annotation qualification

Four of the five fixed GDT764 H1–X–daiin constructions consist of three consecutive literal raw groups with definite internal spaces in all three readings. The fifth also has three consecutive groups and definite internal separators, but its ZL third group is `<!gap>daiin`; only its IT and RF readings meet the literal-whole criterion. This preserves four all-reading raw anchors and precisely qualifies the fifth. It does not establish their grammatical or numerical interpretation.

| Locus | Frozen construction | ZL | IT | RF |
|---|---|---|---|---|
| f105r.24 | pcheey dal daiin | Exact/clear | Exact/clear | Exact/clear |
| f105v.5 | pchedal qopchdy daiin | Exact/clear | Exact/clear | Exact/clear |
| f10v.1 | pcheey qoty daiin | Exact/clear | Exact/clear | Exact/clear |
| f22r.4 | pchaiin ofchy daiin | Exact/clear | Exact/clear | Exact/clear |
| f99r.15 | pcheody oteody daiin | Annotated raw group | Exact/clear | Exact/clear |

All fifteen complete raw-fragment lines match their corresponding cleaned cross-transcription lines before classification. Every pattern has one unique cleaned match in each reading. All fifteen matches map to three distinct consecutive raw groups, with definite internal separators; fourteen meet literal equality. There are no missing or ambiguous matches in this fixed set. The ZL annotation is retained exactly; this pass does not interpret it as a native physical gap or adjudicate a glyph. Its presence is a source qualification, not proof that the construction is absent or that an author wrote different words.

## What this changes

GDT764 used cleaned reader-exact tokens. Its structural anchors are now qualified at the complete raw-construction level. GDT868 previously checked CORE13 individual events; GDT874 checked local-record bridges. Neither cited contract already provided this fixed five-construction/internal-gap result. This is a narrow source-fidelity extension, not a new grammatical method or discovery of five new constructions.

No III, nominality, quality, amount, stage, H1 semantic role, native wordhood or translation is validated. The three editions are alternate readings of one manuscript. Neither their agreement nor the absence of a qualifier in IT/RF overrides ZL. No new images or pages were admitted, and no field/decoder/corpus expansion follows.

## Reproduction and validation

Preregistration and executable producer/independent validator were public in037aabe5 before the raw target run. Five historical patterns/loci were frozen from a selector-guarded GDT764 projection. Both target source tables are queried only for the five frozen selectors, with f84/f84r rejected before payload; complete target loci are retained in SOURCE_ATLAS.json and SOURCE_CROSS.json. Full page projections remain in ignored runtime and have reproducible hashes/statistics in SOURCE_RECEIPTS.json. The producer rechecks the original five-pattern projection before processing the raw data.

Run `python experiments/yolo/gdt877_h1_raw_construction_fidelity/src/run.py`, then `python experiments/yolo/gdt877_h1_raw_construction_fidelity/src/validate.py`. Independent guarded replay confirms retained source records, full-line parity, all fifteen classifications and aggregate counts. Thirteen synthetic checks include annotation/fragmentation, empty raw interruption, uncertain/drawing gaps, repeated matches, irrelevant outer boundary, missing/corrupted lines, and actual repeated-allow CLI filtering. Validation is PASS for transcription/source fidelity only.

Preparation began10:37UTC; target run and independent validation completed by10:46UTC. Publication budget11:05UTC includes registry refresh and staged privacy checks. No automatic follow-on test is selected.
