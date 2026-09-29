# Publication-path correction,29September2026

Commit7065cbc9b published a review JSON outside the structured experiment
directory with `gdt1096` in its filename. The exact-staged privacy check had
passed, but the task preflight reported this filename/layout violation. Root
incorrectly let the following commit/push proceed after receiving that failure.
This was an execution-sequencing error; no successful full preflight is claimed
for that commit. No credential or manuscript-access failure was reported.

The review is moved, byte-for-byte, to
`research_registry/decisions/finite_domains_review_20260929.json`.
Its append-only curation entry, evidence paths and scientific decision do not
change. No experiment source, method, registered lock, observation or result
has been changed. The intermediate local rename was not published.

For this corrective removal the stock task checker still reports the OLD,
deleted malformed path: it checks numbered paths before its deletion branch.
The checker is left unchanged. The complete corrected Git index was separately
passed to its existing `check_structured_layout` implementation and returned
no errors. Every remaining changed blob was checked with the existing filename,
credential/private-key and local-path checks; no errors. The removed path is
absent from the index and the new review has identical bytes. This explicitly
documented removal fixes the violation rather than exempting a malformed live
file. Global historical manifest issues are not certified by this narrow check.

Future dependent commit/push commands follow inspected check results in
separate calls, so a failed preflight cannot fall through to publication.
