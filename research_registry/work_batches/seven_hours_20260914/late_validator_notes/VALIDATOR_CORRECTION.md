# Validator correction receipt

The initial pre-intake validator is preserved byte-for-byte as
`src/validate_preintake_original.py`. It only checked the 28 source rows, 56
cyclic candidates, 1,568 source predictions, and synthetic matching fixtures.

After target intake, the validator was corrected independently without
changing `run.py`, `SOURCE.json`, `SPEC.json`, or any locked file. The complete
validator uses the frozen two target views (`LITERAL` and
`LEGACY_ROOT_EXACT`), checks every raw group count and key, reconstructs all
84 target records, all 168 candidates, all 58,968 pair consequences and all
30,184 component checks, and compares candidate domains, both matching levels,
Hall certificates, mappings, result counts, and input hash. It also accepts the
plain component TSV or its exact gzip representation.

The frozen source model and semantic claim ceiling are unchanged. This is an
implementation correction to independent validation, not a scientific model
revision.
