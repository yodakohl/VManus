# Independent-validator correction, after intake

The initial source-only receipt is preserved in PREINTAKE_VALIDATION_ORIGINAL.json;
src/validate_preintake_original.py exactly preserves the public165d8c151 version.
That source-only run did not exercise target evaluation. Its first target run
stopped with KeyError: models: leftover GDT952 model keys had no GDT953 SPEC field.
Further independent-evaluator defects included integer atom-row indexing, integer
versus string table comparison, and insufficient artifact coverage checks. These
were corrected in the separate validator, then actually run against all generated
records and candidate consequences. The source-only claim is not full validation.

The scored runner, source, SPEC, predictions, target input and preregistration
hashes did not change. This is a validator repair, not a scientific model repair.
The full validation checks84target records,1568predictions,168summaries/details,
58968pair rows and30184component rows, with exact key coverage and0mismatches.
The large component table's gzip roundtrip is checked against the original bytes.
A separate lock receipt records9unchanged preregistration files and2input sources.
No semantic confirmation is supplied by the software agreement.
