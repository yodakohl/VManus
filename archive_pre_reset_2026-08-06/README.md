# Curated pre-reset primary evidence

This directory is the compact subset of the pre-reset investigation needed to
reproduce the retained structural baseline. The original bulk snapshot was
retired on 2026-08-06 and its superseded caches, duplicate outputs, OCR/vision
artifacts, historical downloads, and failed-route working files were removed
on 2026-08-08.

- `semantic_assumptions/` retains the legacy 105-row ledger, shared parser,
  primary structural runners, reports, and result files.
- `ARCHIVE_MANIFEST.tsv` binds every retained regular file by size and SHA-256.
- Active negative-route memory is in
  `../experiments/semantic_assumptions/CLOSED_ROUTE_FAMILIES.tsv`; absence from
  this directory is not evidence that an old route succeeded or never ran.

The retained subset is read-only by policy, not by filesystem permissions. Do
not run a route from it or import an old claim into active state without first
consulting the compact closed-family index and stating genuinely new evidence.
The deleted untracked bulk files are not recoverable from Git.
