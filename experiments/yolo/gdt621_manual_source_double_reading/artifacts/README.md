# GDT621 artifacts

- `REGISTERED_READING_PROFILE.json`: ten-file bindings, blinding order,
  diplomatic capture, reconciliation, display, control, and result contract.
  It separately binds the GDT620 code-registration and result-publication
  commits.
- `REGISTERED_VALIDATION.json`: deterministic registration audit.
- `LATIN_READER_A_RAW.json` and `LATIN_READER_B_RAW.json`: the two independent,
  canonical five-page diplomatic bundles.
- `LATIN_READER_ACCESS_AUDIT.json`: the ten manual Latin view events and global
  zero-access counts.
- `LATIN_RECONCILIATION_FROZEN.json`: canonical, hash-bound checkpoint with
  status `LATIN_RECONCILIATION_FROZEN__CLM_UNOPENED`, publicly committed before
  any Clm page opens.
  It binds both ordered raw bundles, all five reconciled Latin readings, the
  complete ledger, and reconciliation access audit.
- `LATIN_CHECKPOINT_VALIDATION.json`: compact result of the three-artifact
  validator and its 69-case in-memory suite.

Canonical SHA-256 preimages omit their own hash field. Public artifacts contain
no absolute/private paths or image bytes; bare registered filenames remain only
in the registered profile, not reader results.

No JPEG, rendering, crop, OCR output, private directory, or Voynich material
belongs here. The only source transcription is the compact diplomatic text
explicitly required by the registered checkpoint.
