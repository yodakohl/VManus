# GDT778 artifacts

- `EXACT_WHOLE_29_REGISTRY.tsv`: authored form deck with local cohort counts.
- `GDT778_39_EXACT_WHOLE_ATLAS.tsv`: every selected reader-exact span.
- `GDT778_EXACTNESS_EXCLUSIONS.tsv`: the two nonexact right-word exclusions.
- `GDT778_PROVENANCE_SOURCE_CONFLICT_AUDIT.tsv`: GDT734 legacy lineage,
  corrected body/later-whole evidence, and the explicit `ols` conflict.
- `GDT778_376_RENDERER.tsv`: full predecessor-preserving renderer.
- `GDT778_WORKING_DICTIONARY.tsv`: 29 replaceable exact-whole defaults and
  rivals.
- `GDT778_PASSAGE_PATCHES.tsv`: only the 37 displays that actually change.
- `GDT778_GDT388_RELATION_PACKET.tsv`,
  `GDT778_RELATION_EDGE_CROSSWALK.tsv`, and `RELATION_PACKET_INTAKE.json`:
  ineligible exploratory relation acquisition and its intake result.
- `RESULT.json`: compact runner result.
- `VALIDATION.json`: independent 37,991-check cohort, renderer, provenance,
  packet, safety, and twelve-file replay audit.

All TSVs and JSON are regenerated deterministically by `src/run.py`; no new
page, image, OCR, transcription, `f84`, or `f84r` input is used.
