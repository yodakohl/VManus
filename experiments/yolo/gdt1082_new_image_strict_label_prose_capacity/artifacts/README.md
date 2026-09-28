# Artifacts

- `RESULT.json`: preregistered capacity decision and source hashes.
- `VALIDATION.json`: separate full-batch source reconstruction.
- `LABELS.tsv`: every one-group ZL3b local label, including zeroes.
- `MATCHES.tsv`: every exact ZL3b local-label/running-text event in the batch.
- `GUARD.txt`: selector-first guarded-query receipts; no source text.

All are small derived, already exposed data. Source records are selected by
the eleven allow-values in `src/SELECTORS.tsv`; f84-prefixed rows are rejected
before materialisation.
