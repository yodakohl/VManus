# EAS001 provenance and bifolio re-audit

Status before audit: **HISTORICAL POSITIVE SUMMARY; REPRODUCIBILITY UNKNOWN**.

## Question

Can the active `EAS001` graphical-slot boundary claim still be treated as a
confirmed, reproducible result after the repository curation, and can its
13-folio synchronous null be rechecked against the public f67--f73 four-bifolio
codicology?

This is an integrity audit, not a rerun and not a new score. It must preserve
the historical ledger numerics without treating them as reconstructed facts.

## Frozen checks

1. Resolve every EAS001 scientific path named by the active ledger and test
   current existence.
2. Search every reachable Git object name and every dangling commit tree for
   EAS001/explicit-array scientific paths.
3. Read the reset commit `900c22f` manifest and recover the recorded size and
   SHA-256 metadata for the five precursor explicit-array files.
4. Search all Git blobs of matching sizes for those five SHA-256 values.
5. Bind the already independently validated public f67--f73 result: seven
   extant folios are four bifolios (`f67+f68`, `f69+f70`, `f71+f72`, and
   `f73+missing f74`).
6. Determine whether the exact EAS001 13-folio membership and per-folio effects
   survive anywhere, permitting a bifolio-clustered reconstruction.

## Decisions

- If source, target result, independent validator, exact 13-folio membership,
  or required score arrays are unavailable, demote the active confirmation to
  `PROVISIONAL_HISTORICAL_UNRECONSTRUCTED`.
- Do not call the historical number false. Do not recreate the inventory from
  prose or guesses. Reopen only by recovering hash-matching artifacts or by a
  new versioned, independently inventoried experiment.
- EAS001-dependent follow-ups inherit this provenance hold as active evidence;
  their ledger summaries remain historical routing memory.

No OCR, image recognition, manuscript score, lexical inference, or translation
is part of this audit.
