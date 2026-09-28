# GDT1069 method

## Question and decision

Do the 23 published first-prose-group plant-name candidates in GDT1062 end at
a definite source separator, or does a weak/uncertain gap require a longer
written unit? A weak boundary removes *standalone-group* eligibility for that
reader; a definite boundary only retains eligibility. Neither outcome chooses
plant name over opaque entry address.

This is the smallest useful check of a missing input in GDT1062, with an
inclusive 25-minute budget for preparation, code, validation and publication.
No decoder, source name, transcript rule or visual owner is changed. The
predecessor reports GDT1062–1064 and the f9v full-entry capacity decision
already leave plant-name meaning unbound. The newly noticed f9v `fochor`
boundary was inspected before this registration and is disclosed; this is a
descriptive completeness pass, not blind confirmation or a significance test.

## Frozen inputs and scope

- GDT1062 `src/claims.tsv`, SHA-256
  `8fff37db44c619c21b86422125e985d105bed5e2a6b6cd66e650390477c9d4f0`.
  Exactly its 23 admitted pages, names and literal strings; no additions.
- GDT1062 `artifacts/LABEL_RESULTS.tsv`, SHA-256
  `616e0813b249641eb2519fde9989a3efaff0cfb7d942880e66ba623c78dde4c3`.
  This fixes each first prose locus and all three reader-specific exact-match
  states before the new separator extraction.
- `experiments/semantic_assumptions/results/source_separator_transcription.tsv`,
  SHA-256 `4b649c8290d5afc7a5fbcc8e98db2bc123a1ceb5f3858d3befa781ce96b680f0`.
  Mixed rows are accessed only by `./vmanus-exp query-tsv --selector locus`
  with the 23 explicit GDT1062 first-prose-locus allow-values, output columns
  `edition,locus,kind,source_group_index,source_group_count,ivtff_group_raw,left_separator,right_separator`.
  The guard rejects `f84*` before materializing other fields. No image, reserve,
  f116v or new text selector is opened.

## Complete evaluation

For every page and ZL3b/IT2a/RF1b reading, preserve the source's first group
and its exact right-separator code. Include all 69 rows, even if the published
candidate did not match that reader in GDT1062. `DEFINITE_SPACE` qualifies as
a separately bounded first group; `LINE_END` would also qualify if present.
Every other separator remains unqualified and is reported literally. Readers
are alternate transcriptions of one manuscript and never pooled as independent
witnesses. Report all source-separated first-group rows, counts by reader and
the exact status of f9v; do not repair spellings or merge/split groups.

No whole-search control is available, and this check cannot distinguish a
name from an entry address. A failure of standalone eligibility is a boundary
limitation, not a refutation of a longer plant name. A pass is not a translated
word. A later semantic test still requires an independent owner relation.
