# GDT395 scoring execution correction V2

Status: `FROZEN_BEFORE_SCORING_V2`

The first scoring invocation authenticated the published blind-claim gate and
then failed while ingesting the first gzipped blind claim. The frozen scorer's
`open_tsv` helper always used `Path.open`, so gzip header byte `0x8b` caused a
UTF-8 decode error. Execution stopped before the scorer's explicitly marked
first sealed-oracle access and wrote no score artifact.

V2 changes only transport decoding. `score_identifiability_v2.py` imports the
unchanged, claim-freeze-bound scorer, replaces `open_tsv` with an otherwise
identical helper that uses `gzip.open` for `.gz` paths and `Path.open` for plain
TSV paths, then calls the unchanged `main`. It changes no claim, split, oracle
allow-list, representation, metric, threshold, decision rule, or output schema.

This correction is frozen and validated before V2 scoring. No synthetic oracle,
Voynich source, or f84 data was opened in diagnosing or freezing the repair.

