# GDT1153 independent validation

Accounting: PASS (18/18 checks). No root/helper algorithm was imported.

All 13 pinned ZL contexts and their 26 original occurrences were reconstructed in each reader directly from the six GDT915 native JSON snapshots. All 78 case rows, matched host strings, full/partial paragraph streams, prefix exclusions, competitor group IDs/counts/distances and decisions were compared.

|Reader|Compatible|Contradiction|Abstain|Untestable|Decision|
|---|---:|---:|---:|---:|---|
|ZL3b|0|1|5|20|CONTRADICTED|
|IT2a|4|5|16|1|CONTRADICTED|
|RF1b|0|0|0|26|NO_CHOICE_CAPACITY|

The current shared context and all later words are excluded from prior memory. Missing boundaries or uncertain prior words/seams prevent scoring; recorded counts in these rows are descriptive only. One-word prior lines are allowed. All annotated words and native paragraph flags remain retained.

The strict rule is contradicted separately in ZL and IT. This does not determine meanings, establish shared referents or refute other continuation rules. These are exposed development cases; reader alternatives and overlapping paragraph windows provide no independent confirmation or significance.

Paragraph artifact metadata: root removed the old helper call-specific `seed` label before deduplication. This audit excludes only that label from paragraph serialization; all native lines, uncertainty and boundary checks are compared.

Reproduce: `python experiments/yolo/gdt1153_prior_continuation_choice/src/validate.py`.

Detailed checks, all six contradiction rows, native source pins and overlapping paragraph counts are in VALIDATION.json.
