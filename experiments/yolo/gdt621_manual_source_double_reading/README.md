# GDT621 — manual source double reading

Status: `DOUBLE_READING_PROFILE_REGISTERED__NO_SOURCE_IMAGE_OPENED`

GDT621 registers two independent diplomatic readings of the five Latin 6823
pages acquired by GDT620. Reader A and Reader B use different fresh local
renderings and submit the rubric plus twelve following whitespace lexical
tokens before either can see the other's rendering or reading.
The registered headwords are locator hints, not a blind discovery endpoint.
Each separate reader session receives only an opaque DEV ID and private JPEG;
profile, repository, catalog, edition, network, other sources, and other-reader
material are unavailable and this is attested.
The canonical packet contains exactly opaque candidate ID, source SHA-256,
session ID, and a path-free opaque rendering handle—never a headword, witness identity, URL, crosswalk, expected
rubric, repository locator, filename, or other submission.
The handle has a fixed nonspeaking `R[A|B]nn-HEX16` form.

Only after both Latin submissions are frozen may reconciliation begin. The Clm
pages open only after a canonical reconciled-Latin checkpoint is publicly
committed; they are locator/control pages only and cannot repair Latin.
The checkpoint binds both raw bundles, every reconciled reading, the complete
ledger, and adjudicator audit; the final result reuses these byte-identically.
Registration opens no image and performs no network request. See `METHOD.md`,
`PREREGISTRATION.md`, and `artifacts/REGISTERED_READING_PROFILE.json`.
The profile distinguishes GDT620's acquisition-code registration commit
`61a253ce…` from its separate result-publication commit `798e05f4…`.
