# GDT342 prepublication raw-control correction

During the first uncommitted Stage-A dry run, the implementation labeled a
control `RAW_OPAQUE_WORD_IDENTITY` but used CoReMA's semantic
`commodity=Q...` attribute for ingredient/tool/dish/name elements. That was not
a diplomatic-word control; it substantially duplicated the global editor-
concept ceiling.

The defect was found by inspecting the exact XML attributes immediately after
the dry-run score. No GDT327 value or f84 artifact had been opened. The
candidate anonymous graph, weights, folds, truth, null, and decision gate were
not changed.

The corrected control hashes only diplomatic source tokens from element text,
uses direct text for container elements to avoid nested duplication, and never
uses `commodity` or English labels. The superseded uncommitted control had MRR
.864402. The corrected control has top-1 538/688, top-5 578/688, and MRR
.807524. It still decisively exceeds anonymous entity flow (MRR .540115), so
the scientific stop is unchanged.

`src/validate.py` independently reconstructs all 688 corrected raw-control
rankings directly from the six XML sources and reports PASS 778/778.
