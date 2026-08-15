# GDT117 — Q20 same-page OPEN/BODY retrieval

Status: **Q20_COMPILER_PROFILE_SUPPORTS_HELD_RECORD_RETRIEVAL_READING_SENSITIVE**

The held-folio task contains 99 records in same-page,
exact-OPEN-length candidate strata. Chance top-1 is
0.444. `COMPILER12` identifies the true OPEN with
top-1 accuracy 0.586, MRR 0.778, and pairwise
accuracy 0.638; its MRR local/max-four p-values are
0.0020/0.0034.
That is 58/99
exact first choices versus 44
expected. RF1b also clears the MRR max-four control
(0.0134); IT2a remains positive
but does not (0.2724), where the
wrapper-only representation is stronger. The linkage is therefore
transcription-sensitive in its exact representation.

ZL3b comparison:

| model | top-1 | MRR | pairwise | MRR max-4 p |
|---|---:|---:|---:|---:|
| `WRAPPER7` | 0.525 | 0.750 | 0.601 | 0.0945 |
| `COMPILER12` | 0.586 | 0.778 | 0.638 | 0.0034 |
| `EDGE29` | 0.465 | 0.704 | 0.478 | 0.8384 |
| `RAW_CHAR3_HASH32` | 0.475 | 0.714 | 0.514 | 0.6907 |

This is a specific record-linkage prediction on completely unseen folios. It
does not make OPEN a heading or identify what any record contains. No role,
word, morpheme, POS, sound, language, plaintext, meaning, or translation is
assigned. f84r remained excluded and unpredicted.
