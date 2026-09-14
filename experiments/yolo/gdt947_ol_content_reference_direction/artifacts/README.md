# GDT947 generated artifacts

`OCCURRENCES.tsv` inventories exact raw occurrences of primary `olshedy`/`olshey` and diagnostic `olkain`/`olkeedy`/`olchey`, retaining source IDs, reader, page/locus, leaf, exposure, paragraph ID, and raw separator flags. `CASES.tsv` repeats each occurrence for BACK and FORWARD; `anchor_ids` and `uncertainty_ids` are `|`-joined source IDs.

Per-case precedence is `NO_PARAGRAPH_CAPACITY`, then `TARGET_BOUNDARY_UNCERTAIN`, then written-anchor evaluation. Summary decisions reject when any missing-anchor case exists, even if other cases lack capacity. `CANDIDATE_DECISIONS.tsv` gives primary and joint-primary totals across all editions/exposures. `SOURCE_CONTEXT.json` includes complete raw lines for every target locus across all six snapshots; `PARAGRAPH_CONTEXT.json` preserves complete own-edition target paragraphs. `RESULT.json` records counts and the zero-meaning claim ceiling.
