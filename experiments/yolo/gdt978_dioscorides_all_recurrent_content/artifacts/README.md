# Prediction and certificate artifacts

SOURCE_CONSEQUENCES.tsv accounts for every original source occurrence.
PARTITION_PREDICTIONS.json partitions all surviving old base IDs before fitting.
PARTITION_RESULTS.json.gz preserves solver outcomes and every found code/span
witness. BASE_CASE_RESULTS.tsv keeps all 8990 old candidate rows, including
previous exclusions and unresolved cases inside a SAT partition.
WITNESS_ALIGNMENTS.json shows source indices and exact target-character spans
only for verified witnesses; singleton-run internal boundaries remain unknown.
RESULT.json and VALIDATION.json give compact aggregate outcomes and ceilings.
