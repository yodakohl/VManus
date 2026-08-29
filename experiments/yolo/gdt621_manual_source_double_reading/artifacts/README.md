# GDT621 artifacts

- `REGISTERED_READING_PROFILE.json`: ten-file bindings, blinding order,
  diplomatic capture, reconciliation, display, control, and result contract.
  It separately binds the GDT620 code-registration and result-publication
  commits.
- `REGISTERED_VALIDATION.json`: later deterministic offline audit.
- `LATIN_RECONCILIATION_FROZEN.json`: later canonical, hash-bound checkpoint
  with status `LATIN_RECONCILIATION_FROZEN__CLM_UNOPENED`, publicly committed
  before any Clm page opens.
  It binds both ordered raw bundles, all five reconciled Latin readings, the
  complete ledger, and reconciliation access audit.

Canonical SHA-256 preimages omit their own hash field. Public artifacts contain
no absolute/private paths or image bytes; bare registered filenames remain only
in the registered profile, not reader results.

No JPEG, rendering, crop, OCR output, private directory, source transcription,
or Voynich material belongs here during registration.
