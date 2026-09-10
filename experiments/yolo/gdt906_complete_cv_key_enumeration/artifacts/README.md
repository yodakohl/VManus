# GDT906 artifacts

`BINDINGS.json` seals unchanged inputs and prospective primary implementation.
`PLAN.json.gz` partitions all 2,240,785 surviving masks into 98,083 literal
segmentation classes and 439,399 vowel cases; `SCOPE.json` binds that plan.
`INDEPENDENT_PLAN_VALIDATION.json` verifies its complete exact coverage.

`CASES.json.gz` retains every complete primary case, all observed assignments
and grammar verdicts. `INDEPENDENT_CASES.jsonl.gz` retains every exact independent
receipt, its source version and primary receipt hash. `PACKING.json` and
`INDEPENDENT_PACKING.json` bind compressed and logical bytes. These compressed
artifacts are needed for complete coverage and per-case provenance validation.

`RESULT.json`, `INDEPENDENT_COMPLETE_VALIDATION.json` and `VALIDATION.json` are
the final complete result and checks. `LEXICAL_KEYS.json`/`.md` contain all three
lexical case assignments; `WITNESS_ROLLUP.json` records their two distinct key/
passages. `INDEPENDENT_WITNESS_VALIDATION.json` is the earlier limited check of
those three cases, preserved with its original scope and validator hash.
`INDEPENDENT_FLOW_BENCHMARK.json` records a technical optimization and its oracle
checks; it is not a manuscript discovery. No external work/cache paths are stored.
