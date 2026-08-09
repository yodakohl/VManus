# Public voynich.nu catalogue source refresh

The existing human-annotation atlas was built from the 18 public quire pages
at `voynich.nu`, but repository curation retained only derived TSV/JSON files
and removed the cached HTML named in the provenance manifest. This made the
page-description layer impossible to rebuild from the published repository.

This pass restores the exact public source snapshot and checks whether the
live catalogue changed relative to the retained 228-row page annotation TSV.
It downloads only:

`q01`–`q15`, `q17`, `q19`, and `q20` from
`https://www.voynich.nu/<quire>/index.html`.

Every response must match the SHA-256 already registered in
`existing_human_annotation_atlas.json`. The parser independently reconstructs
page IDs and the five named prose fields: general description, illustrations,
text, tentative identifications, and other information. Every field is
compared exactly with `existing_human_page_annotations.tsv`.

No manuscript image, OCR, automated vision, Voynich string, grammar feature,
or semantic score is used. Tentative identifications remain modern public
descriptions, not authorial meanings or lexical keys.
