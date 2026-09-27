# GDT1049 — complete Galen season-concept countercheck

One complete edition-level annotation of WINTER and SUMMER, with uncertainty
and contextual reference preserved. No manuscript target is scored.

- [Preregistration](PREREGISTRATION.md)
- [Result and limits](REPORT.md)
- [All paragraph metadata](artifacts/SOURCE_UNITS.json)
- [Original BooksI/II annotations](artifacts/ANNOTATIONS_I_II.json)
- [Original BookIII annotations](artifacts/ANNOTATIONS_III.json)
- [Independent semantic review](artifacts/SECOND_REVIEW.json)

From repository root, with Python3 standard library only:

```sh
python experiments/yolo/gdt1049_galen_season_concept_countercheck/src/run.py --acquire
python experiments/yolo/gdt1049_galen_season_concept_countercheck/src/validate.py
```

The optional acquisition downloads exactly the recorded Gutenberg HTML if the
local source cache is missing, and accepts it only at the fixed SHA256. If the
remote representation changes, obtain the recorded source bytes; do not replace
its hash or call a changed-source result a reproduction. Full extracted text is
local in runtime. Published hashes/locators/annotations permit manual checking
against the original edition; code replays extraction and count arithmetic,
not human comprehension. No API-based annotation or model inference is rerun.

The initial extraction retained one untagged footnote number. Its documented
removal implements the already registered rule; initial metadata is retained.
All source paragraphs, boundaries and wordcounts stayed the same. Original
semantic annotations are immutable; review changes are separate records.
