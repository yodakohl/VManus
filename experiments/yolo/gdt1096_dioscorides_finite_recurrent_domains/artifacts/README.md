# GDT1096 compact artifacts

`CANDIDATES.tsv` and `CASES.json` preserve all1428 original predictions and
statuses. `CERTIFICATES.json.gz` contains every newly evaluated case's complete
initial/final domains and deletion trace. `RESULT.json` aggregates those rows;
`VALIDATION.json` records independent algorithm replay of341 certificates and
206162 deletions. `CONTROL_RESULTS.json` is frozen before target execution.
`EXECUTION_RECEIPT.json` binds the preceding public registration commit.

`TABLE_VALIDATION.json` checks every displayed TSV cell against the primary
case JSON. Reproduce it with `python3` and `src/validate_table.py` in the
experiment directory. That presentation checker was added after the result;
the registered runner and scientific validator remain byte-unchanged.
