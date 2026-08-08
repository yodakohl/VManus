# Existing-human current-locus crosswalk

Decision: **PASS_CLUSTERED_MULTI_EVIDENCE_CURRENT_LOCUS_CROSSWALK**.

Important correction: the 1,018 source rows are not 1,018 physical labels. They represent **998 physical locations**; f75v has 20 locations with both U- and V-coded transcriptions. The prior record-level Hungarian assignment incorrectly forced those paired transcription records onto different loci and is superseded.

The source format defines field 6 as the one-letter transcriber code, field 7 as the EVA label/title, and field 8 as an alternate spelling. The active schema now uses `source_transcriber_code`; string matching always uses the field-7 text.

The corrected crosswalk retains all **1018** source records and maps **816 / 998** physical locations conservatively on 77 pages.

| match status | physical locations | source records |
|---|---:|---:|
| AMBIGUOUS_OR_LOW | 137 | 137 |
| EXACT_REPEAT_AMBIGUOUS | 12 | 12 |
| EXACT_UNIQUE | 297 | 297 |
| EXPLICIT_HUMAN_POSITION_KEY | 274 | 274 |
| EXPLICIT_MISSING_POSITION_NO_CURRENT_LOCUS | 1 | 1 |
| HIGH_RATIO_UNIQUE | 13 | 13 |
| MARGINED_RATIO | 52 | 52 |
| NO_CURRENT_PAGE_OR_ASSIGNMENT | 27 | 27 |
| NO_SOURCE_STRING | 5 | 5 |
| SEQUENCE_GROUP_POSITION | 180 | 200 |

Explicit human ring/Grove-number keys map 275 physical locations. Strongly separated sequence alignments map 395 locations in 38 whole groups. Conflicting strong evidence remains withheld for 0 locations.

Repeated words are not removed. 90 exact-normalized source text types occur at 239 physical locations. A repeated word at two physical locations remains two rows; sequence or explicit position evidence may disambiguate which occurrence is which. Alternate transcriptions of one physical location remain linked and never count as two labels or independent confirmation.

Clear current kinds by physical location: `{'L': 737, 'P': 40, 'R': 39}`. This is a document-role crosswalk, not evidence that a label is a name, noun, or translated word.

The page-role matrix covers 227 active pages with 226 literal catalogue matches; `fRos` remains `COMPOUND_ALIAS_REQUIRED`.

No image, OCR, automated vision, grammar feature, object identity, or English semantic score selected a mapping. The explicit position layer uses only human ring scope and Grove numbering. Ambiguous records were not dropped.
