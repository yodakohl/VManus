# Artifacts

`RESULT.json` records the guarded projection hash, query guard statistics,
completeness assertions, and output row counts. `guarded_projection.tsv` is the
exact stdout from the preregistered selector-first query; `query_guard_stderr.txt`
retains the guard's summary. `native_groups.tsv`, `repeated_forms.tsv`,
`block_intersections.tsv`, `repeated_ngrams.tsv`, `literal_edit1_pairs.tsv`,
and `line_first_last.tsv` are complete frozen-method inventories. They are
retained in full because every selected native group, exact recurrence,
separator signature, and eligible distance-one pair is a required audit trail;
sampling would make the census incomplete.
